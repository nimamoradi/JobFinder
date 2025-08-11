import os
import json
import boto3
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

# --- Client Initialization ---
ses = boto3.client('ses', region_name='us-east-1')
sqs = boto3.client('sqs')

# --- Environment Variables ---
SENDER_EMAIL = os.environ.get('SENDER_EMAIL')
RECIPIENT_EMAIL = os.environ.get('RECIPIENT_EMAIL')
EMAIL_QUEUE_URL = os.environ.get('EMAIL_QUEUE_URL')


def create_email_with_attachments(jobs):
    """Builds a multipart email with a summary and .tex file attachments."""
    msg = MIMEMultipart()
    msg['Subject'] = f"Job Application Summary: {len(jobs)} CVs Generated"
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL

    body_text = "Here is your summary of generated CVs:\n\n"
    for job in jobs:
        company = job.get('company_name', 'UnknownCompany')
        title = job.get('title', 'UnknownTitle').replace(' ', '_').replace('/', '-')
        filename = f"{company}_{title}.tex"

        body_text += f"- Job Title: {job.get('title', 'N/A')}\n"
        body_text += f"  Apply Link: {job.get('joblink', 'N/A')}\n"
        body_text += f"  Attached CV: {filename}\n"
        body_text += f"  Job ID: {job.get('jobId')}\n\n"

    msg.attach(MIMEText(body_text, 'plain'))

    for job in jobs:
        company = job.get('company_name', 'UnknownCompany')
        title = job.get('title', 'UnknownTitle').replace(' ', '_').replace('/', '-')
        filename = f"{company}_{title}.tex"

        cv_content = job.get('generated_cv', '')
        part = MIMEApplication(cv_content)
        part.add_header('Content-Disposition', 'attachment', filename=filename)
        msg.attach(part)

    return msg


def lambda_handler(event, context):
    """
    Pulls all available messages from the EmailQueue, creates a single summary
    email with attachments, and sends it.
    """
    all_jobs_for_email = []
    messages_to_delete = []

    # Loop to pull all messages from the queue
    while True:
        print(f"Polling SQS queue for up to 10 messages...")
        response = sqs.receive_message(
            QueueUrl=EMAIL_QUEUE_URL,
            MaxNumberOfMessages=10,  # Get up to 10 messages at a time
            WaitTimeSeconds=2  # Use long polling to be efficient
        )

        messages = response.get('Messages', [])
        if not messages:
            print("Queue is empty. Exiting polling loop.")
            break  # Exit loop if queue is empty

        for message in messages:
            job_data = json.loads(message['Body'])
            all_jobs_for_email.append(job_data)
            # Add the message handle to a list for batch deletion
            messages_to_delete.append({
                'Id': message['MessageId'],
                'ReceiptHandle': message['ReceiptHandle']
            })

    if not all_jobs_for_email:
        print("No jobs found in the queue. Nothing to email.")
        return {'statusCode': 200, 'body': 'No jobs to process.'}

    print(f"Pulled a total of {len(all_jobs_for_email)} jobs. Building email...")
    email_message = create_email_with_attachments(all_jobs_for_email)

    try:
        print(f"Sending email to {RECIPIENT_EMAIL}...")
        ses.send_raw_email(
            Source=SENDER_EMAIL,
            Destinations=[RECIPIENT_EMAIL],
            RawMessage={'Data': email_message.as_string()}
        )
        print("Email sent successfully.")
    except Exception as e:
        print(f"ERROR: Failed to send email via SES. {e}")
        raise

    # Finally, delete the messages from the queue so they aren't processed again
    if messages_to_delete:
        print(f"Deleting {len(messages_to_delete)} messages from the queue...")
        sqs.delete_message_batch(
            QueueUrl=EMAIL_QUEUE_URL,
            Entries=messages_to_delete
        )

    return {'statusCode': 200, 'body': 'Email summary sent successfully.'}