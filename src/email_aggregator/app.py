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


def chunk_list(data, chunk_size):
    """Yield successive n-sized chunks from a list."""
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]


def create_email_with_attachments(jobs):
    """Builds a multipart email with a summary and .tex file attachments."""
    msg = MIMEMultipart()
    msg['Subject'] = f"Job Application Summary: {len(jobs)} Jobs Found"
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL

    body_text = "Here is your summary of job matches:\n\n"
    jobs_with_cv = []
    
    for job in jobs:
        company = job.get('company_name', 'UnknownCompany')
        title = job.get('title', 'UnknownTitle').replace(' ', '_').replace('/', '-')
        cv_content = job.get('generated_cv')

        body_text += f"- Job Title: {job.get('title', 'N/A')}\n"
        body_text += f"  Company: {company}\n"
        body_text += f"  Apply Link: {job.get('joblink', 'N/A')}\n"
        body_text += f"  Job ID: {job.get('jobId')}\n"
        
        if cv_content:
            filename = f"{company}_{title}.tex"
            body_text += f"  Attached CV: {filename}\n"
            jobs_with_cv.append({'job': job, 'filename': filename, 'cv_content': cv_content})
        else:
            body_text += f"  CV: Not generated (NO_CV_GEN mode)\n"
        
        body_text += "\n"

    msg.attach(MIMEText(body_text, 'plain'))

    # Only attach CVs for jobs that have them
    for item in jobs_with_cv:
        part = MIMEApplication(item['cv_content'])
        part.add_header('Content-Disposition', 'attachment', filename=item['filename'])
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
        print(f"Deleting {len(messages_to_delete)} messages from the queue in batches of 10...")
        for chunk in chunk_list(messages_to_delete, 10):
            sqs.delete_message_batch(
                QueueUrl=EMAIL_QUEUE_URL,
                Entries=chunk
            )
            print(f"Deleted a batch of {len(chunk)} messages.")

    return {'statusCode': 200, 'body': 'Email summary sent successfully.'}
