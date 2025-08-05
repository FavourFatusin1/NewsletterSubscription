import json
import boto3
import os
import urllib.request

sns_client = boto3.client('sns')
TOPIC_ARN = os.environ.get('TOPIC_ARN')
MAILBOXLAYER_API_KEY = os.environ.get('MAILBOXLAYER_API_KEY')  # Set this env var in Lambda

def validate_email_mailboxlayer(email):
    url = f"http://apilayer.net/api/check?access_key={MAILBOXLAYER_API_KEY}&email={email}&smtp=1&format=1"
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read())
        # smtp = True means mail server responded
        # format_valid = True means email syntax okay
        return data.get('format_valid') and data.get('smtp_check')

def lambda_handler(event, context):
    headers = {
        'Access-Control-Allow-Origin': '*',  
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
    }

    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({"message": "CORS preflight successful"})
        }

    try:
        if 'body' not in event or not event['body']:
            raise ValueError("Missing request body")

        body = json.loads(event['body'])
        email = body.get('email', '').strip()

        if not email or '@' not in email:
            raise ValueError("Invalid or missing email address")

        if not MAILBOXLAYER_API_KEY:
            raise ValueError("Email validation API key not configured")

        # Validate email using MailboxLayer
        is_valid = validate_email_mailboxlayer(email)
        if not is_valid:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({"error": "Email address is not valid or not deliverable"})
            }

        if not TOPIC_ARN:
            raise ValueError("SNS Topic ARN not configured in environment variables")

        sns_client.subscribe(
            TopicArn=TOPIC_ARN,
            Protocol='email',
            Endpoint=email
        )

        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({"message": f"Subscription request sent to {email}. Please check your email to confirm."})
        }

    except Exception as e:
        print("Error:", str(e))
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }
