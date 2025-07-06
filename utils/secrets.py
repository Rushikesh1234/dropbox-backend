import os
import json
import boto3
import boto3.session
from dotenv import load_dotenv
from botocore.exceptions import BotoCoreError, ClientError

def load_secrets(secret_name="dropbox-clone/dev/env", region_name="us-east-1"):
    try:
        session = boto3.session.Session()
        client = session.client(service_name='secretsmanager', region_name=region_name)

        secret_value = client.get_secret_value(SecretId=secret_name)
        secret = json.loads(secret_value["SecretString"])

        for key, value in secret.items():
            os.environ[key] = value

    except (BotoCoreError, ClientError) as e:
        print(f"Warning: Could not load AWS Secrets — {e}")
        print("Falling back to local .env file.")
        load_dotenv()