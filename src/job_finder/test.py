import hashlib
import json
import os
import re

from google import genai
_client = genai.Client(api_key="AIzaSyDD6oe7BealDvajjh_XeikRsS4oJUzLo7M")
with open('config/cv_summary.txt', 'r') as f:
    CV_summary = f.read()
with open('config/prompt.txt', 'r') as f:
    GEMINI_PROMPT_TEMPLATE = f.read()
def extract_json_content(text):
    start_marker = '```json'
    end_marker = '```'

    # Find the start position after the json marker
    start_pos = text.find(start_marker)
    if start_pos == -1:
        return text
    start_pos += len(start_marker)

    # Find the end position
    end_pos = text.find(end_marker, start_pos)
    if end_pos == -1:
        return text[start_pos:]  # Return rest of string if no end marker

    # Extract and return the content between markers
    return text[start_pos:end_pos].strip()

if __name__ == '__main__':
    # load the json from file
    with open('config/data.json', 'r') as f:
        results = json.loads(f.read())


    jobs = results.get('jobs_results', [])
    processed_count = 0
    for job in jobs:
        try:
            apply_link = (job.get('apply_options', [{}])[0] or {}).get('link')
            description = job.get('description')
            if not apply_link or not description:
                continue

            # Use a hash of the apply link as a unique and repeatable ID
            jobId = hashlib.sha256(apply_link.encode('utf-8')).hexdigest()

            # response = table.get_item(Key={'jobId': jobId})
            # if 'Item' in response:
            #     print(f"Job ID {jobId} already exists. Skipping.")
            #     continue

            print(f"Analyzing job: {job.get('title')[:50]}...")
            prompt = GEMINI_PROMPT_TEMPLATE.format(job_description=description, cv_summary=CV_summary)
            gemini_response =_client.models.generate_content(
                model='gemini-1.5-flash',
                contents=prompt,
            )

            # The prompt asks for JSON, so we can load it directly
            analysis_json = json.loads(extract_json_content(gemini_response.text))

            # The prompt also specifies the JSON format for the CV generation itself.
            # That format is perfect for the *next* Lambda function in your workflow (CVGenerator),
            # which will take this screening analysis and generate the final bullet points.

            score = analysis_json.get('score', 0)
            print(f"Gemini match score: {score}")

            if score < 6:
                continue

            print(f"MATCH FOUND! Saving job {jobId} to DynamoDB...")

            Item={
                'jobId': jobId,
                'jobType': 'job_type',
                'joblink': apply_link,
                'status': 'MATCH_FOUND',
                'title': job.get('title'),
                'description': description,
                'gemini_score': score,
                'gemini_analysis': json.dumps(analysis_json)
            }


            # sqs.send_message(QueueUrl=SQS_QUEUE_URL, MessageBody=json.dumps({'jobId': jobId}))
            processed_count += 1

        except Exception as e:
            print(f"Failed to process a job. Error: {e}")
            continue