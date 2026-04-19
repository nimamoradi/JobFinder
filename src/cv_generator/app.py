import json
import os
from datetime import datetime, timezone

import boto3
from aws_durable_execution_sdk_python import (
    DurableContext,
    durable_execution,
    durable_step,
)

# Support both package layouts:
# - CodeUri: src/cv_generator (imports like 'cv_tools.*', 'gen_ai.*')
# - CodeUri: src (imports like 'cv_generator.cv_tools.*', 'cv_generator.gen_ai.*')
try:
    from cv_tools.create_cv import create_cv
    from cv_tools.yaml_parser import Loader
    from gen_ai.gemini import AskGemini
    from gen_ai.model_names import Flash
except ModuleNotFoundError:
    from cv_generator.cv_tools.create_cv import create_cv
    from cv_generator.cv_tools.yaml_parser import Loader
    from cv_generator.gen_ai.gemini import AskGemini
    from cv_generator.gen_ai.model_names import Flash

# --- Configuration & Client Initialization ---

dynamodb = boto3.resource('dynamodb')
sqs = boto3.client('sqs')
DYNAMODB_TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME')
EMAIL_QUEUE_URL = os.environ.get('EMAIL_QUEUE_URL')
BASE_DIR = os.path.dirname(__file__)
RESUME_PATH = os.path.join(BASE_DIR, 'config', 'resume.yaml')

table = dynamodb.Table(DYNAMODB_TABLE_NAME)


def generate_cv(cv_obj, job_description):
    gemini = AskGemini(model_name=Flash)
    return create_cv(cv_obj, job_description, include_certs=True, gemini=gemini)


@durable_step
def process_single_job(step_context, jobId):
    """
    Process a single job: fetch from DynamoDB, generate CV, update DB, send to queue.
    This is wrapped in @durable_step for automatic checkpointing.
    """
    step_context.logger.info(f'Processing job with ID: {jobId}')

    response = table.get_item(Key={'jobId': jobId})
    if 'Item' not in response:
        step_context.logger.info(f'Job ID {jobId} not found in DynamoDB. Skipping.')
        return {'status': 'skipped', 'jobId': jobId}

    job_item = response['Item']
    job_description = job_item.get('description')
    cv_obj = Loader(RESUME_PATH)

    generated_cv_text = generate_cv(cv_obj, job_description)

    step_context.logger.info(f'Updating DynamoDB for job ID: {jobId}')
    table.update_item(
        Key={'jobId': jobId},
        UpdateExpression='SET #status = :status, #cv = :cv, #date = :date',
        ExpressionAttributeNames={
            '#status': 'status',
            '#cv': 'generated_cv',
            '#date': 'generation_date',
        },
        ExpressionAttributeValues={
            ':status': 'CV_GENERATED',
            ':cv': generated_cv_text,
            ':date': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
        },
    )

    step_context.logger.info(f'Sending final job details for {jobId} to EmailQueue...')
    sqs.send_message(
        QueueUrl=EMAIL_QUEUE_URL,
        MessageBody=json.dumps(
            {
                'jobId': jobId,
                'title': job_item.get('title'),
                'company_name': job_item.get('company'),
                'joblink': job_item.get('joblink'),
                'generated_cv': generated_cv_text,
            }
        ),
    )

    return {'status': 'completed', 'jobId': jobId}


@durable_execution
def lambda_handler(event, context: DurableContext):
    """
    Durable function that processes job messages from SQS.
    Uses context.wait() to pause for 2 minutes between jobs without compute charges.
    """
    results = []
    records = event.get('Records', [])

    for i, record in enumerate(records):
        try:
            message_body = json.loads(record['body'])
            jobId = message_body.get('jobId')

            if not jobId:
                context.logger.info('Skipping record due to missing jobId.')
                continue

            result = context.step(process_single_job(jobId))
            results.append(result)

            if i < len(records) - 1:
                context.logger.info('Waiting 2 minutes before next job...')
                context.wait(120)

        except Exception as e:
            context.logger.error(
                f"ERROR processing job ID {jobId if 'jobId' in locals() else 'Unknown'}: {e}"
            )
            results.append(
                {
                    'status': 'error',
                    'jobId': jobId if 'jobId' in locals() else 'Unknown',
                    'error': str(e),
                }
            )
            continue

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Processing complete.', 'results': results}),
    }
