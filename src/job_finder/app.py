import hashlib
import json
import os

import boto3
from google import genai
from serpapi import GoogleSearch

with open('config/cv_summary.txt', 'r', encoding='utf-8') as f:
    CV_SUMMARY = f.read()
with open('config/prompt.txt', 'r', encoding='utf-8') as f:
    GEMINI_PROMPT_TEMPLATE = f.read()

dynamodb = boto3.resource('dynamodb')
sqs = boto3.client('sqs')

DYNAMODB_TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME')
JOB_QUEUE_URL = os.environ.get('JOB_QUEUE_URL')
EMAIL_QUEUE_URL = os.environ.get('EMAIL_QUEUE_URL')
SERPAPI_API_KEY = os.environ.get('SERPAPI_API_KEY')
JOB_MATCH_MODEL = os.environ.get('JOB_MATCH_MODEL', 'gemma-3-27b-it')

RAW_NO_CV_GEN = os.environ.get('NO_CV_GEN', 'false')
NO_CV_GEN = RAW_NO_CV_GEN.lower() == 'true'

table = dynamodb.Table(DYNAMODB_TABLE_NAME)
_client = genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))


def extract_json_content(text):
    start_marker = '```json'
    end_marker = '```'

    start_pos = text.find(start_marker)
    if start_pos == -1:
        return text
    start_pos += len(start_marker)

    end_pos = text.find(end_marker, start_pos)
    if end_pos == -1:
        return text[start_pos:]

    return text[start_pos:end_pos].strip()


def lambda_handler(event, context):
    job_type = event.get('job_type')
    if not job_type:
        raise ValueError("Error: 'job_type' not found in the trigger event.")

    search_query = f"{job_type} jobs canada since yesterday"
    print(f"Starting scheduled job search for: '{search_query}' with NO_CV_GEN={NO_CV_GEN}")

    params = {"api_key": SERPAPI_API_KEY, "engine": "google_jobs", "q": search_query}
    search = GoogleSearch(params)
    results = search.get_dict()

    jobs = results.get('jobs_results', [])

    processed_count = 0
    for job in jobs:
        try:
            apply_options = job.get('apply_options', [])
            apply_link = apply_options[0].get('link') if apply_options else None

            description = job.get('description')
            company_name = job.get('company_name')
            title = job.get('title', 'Unknown Title')

            if not apply_link or not description:
                continue

            job_id = job.get('job_id') or hashlib.sha256(apply_link.encode('utf-8')).hexdigest()

            response = table.get_item(Key={'jobId': job_id})
            if 'Item' in response:
                print(f"Job ID {job_id} already exists. Skipping.")
                continue

            print(f"Analyzing job: {title[:80]}...")
            prompt = GEMINI_PROMPT_TEMPLATE.format(job_description=description, cv_summary=CV_SUMMARY)
            gemini_response = _client.models.generate_content(
                model=JOB_MATCH_MODEL,
                contents=prompt,
            )

            analysis_json = json.loads(extract_json_content(gemini_response.text))

            score = analysis_json.get('score', 0)
            print(f"Match score for {job_id}: {score}")

            if score < 6:
                continue

            table.put_item(
                Item={
                    'jobId': job_id,
                    'jobType': job_type,
                    'joblink': apply_link,
                    'company': company_name,
                    'status': 'MATCH_FOUND',
                    'title': title,
                    'description': description,
                    'gemini_score': score,
                    'gemini_analysis': json.dumps(analysis_json),
                }
            )

            if NO_CV_GEN:
                print("NO_CV_GEN is True. Sending match directly to EmailQueue.")
                sqs.send_message(
                    QueueUrl=EMAIL_QUEUE_URL,
                    MessageBody=json.dumps(
                        {
                            'jobId': job_id,
                            'title': title,
                            'company_name': company_name,
                            'joblink': apply_link,
                            'generated_cv': '',
                        }
                    ),
                )
            else:
                print("NO_CV_GEN is False. Sending match to JobsQueue for CV generation.")
                sqs.send_message(
                    QueueUrl=JOB_QUEUE_URL,
                    MessageBody=json.dumps({'jobId': job_id}),
                )

            processed_count += 1

        except Exception as e:
            print(f"Failed to process a job. Error: {e}")
            continue

    print(f"Search complete. Found and queued {processed_count} qualified jobs.")
    return {'statusCode': 200, 'body': json.dumps(f"Queued {processed_count} jobs.")}


if __name__ == '__main__':
    lambda_handler(event={'job_type': 'Android Developer'}, context=None)
