import os
import json
import boto3
from datetime import datetime, timezone

from cv_tools.create_cv import create_cv

# --- Configuration & Client Initialization ---

# Initialize clients
dynamodb = boto3.resource('dynamodb')
sqs = boto3.client('sqs')
# Environment Variables
DYNAMODB_TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME')
EMAIL_QUEUE_URL = os.environ.get('EMAIL_QUEUE_URL') # URL for the second queue

table = dynamodb.Table(DYNAMODB_TABLE_NAME)


def generate_cv(cvObj, job_description, cv_summary):
    return create_cv(cvObj, job_description, cv_summary, include_certs=True, )


def lambda_handler(event, context):
    """
    Processes job messages from SQS, generates a tailored CV,
    and updates the job item in DynamoDB.
    """
    for record in event['Records']:
        try:
            message_body = json.loads(record['body'])
            jobId = message_body.get('jobId')

            if not jobId:
                print("Skipping record due to missing jobId.")
                continue

            print(f"Processing job with ID: {jobId}")

            # 1. Fetch the full job details from DynamoDB
            response = table.get_item(Key={'jobId': jobId})
            if 'Item' not in response:
                print(f"Job ID {jobId} not found in DynamoDB. Skipping.")
                continue

            job_item = response['Item']
            job_description = job_item.get('description')
            with open('config/cv_summary.txt', 'r') as f:
                cv_summary = f.read()
            with open('config/resume.yaml', 'r') as f:
                from cv_tools.yaml_parser import Loader
                cvObj = Loader('config/resume.yaml')

            # 2. Call Gemini to generate the tailored CV JSON
            generated_cv_text = generate_cv(cvObj, job_description, cv_summary)

            # 3. Update the item in DynamoDB with the new CV and status
            print(f"Updating DynamoDB for job ID: {jobId}")
            table.update_item(
                Key={'jobId': jobId},
                UpdateExpression="SET #status = :status, #cv = :cv, #date = :date",
                ExpressionAttributeNames={
                    '#status': 'status',
                    '#cv': 'generated_cv',
                    '#date': 'generation_date'
                },
                ExpressionAttributeValues={
                    ':status': 'CV_GENERATED',
                    ':cv': generated_cv_text,
                    ':date': datetime.now(timezone.utc).strftime('%Y-%m-%d')
                }
            )
            # 4. Send all data needed for the email to the second queue
            print(f"Sending final job details for {jobId} to EmailQueue...")
            sqs.send_message(
                QueueUrl=EMAIL_QUEUE_URL,
                MessageBody=json.dumps({
                    'jobId': jobId,
                    'title': job_item.get('title'),
                    'company_name': job_item.get('company'),
                    'joblink': job_item.get('joblink'),
                    'generated_cv': generated_cv_text
                })
            )
        except Exception as e:
            print(f"ERROR processing job ID {jobId if 'jobId' in locals() else 'Unknown'}: {e}")
            # Continue to the next message in the batch
            continue

    return {'statusCode': 200, 'body': json.dumps('Processing complete.')}