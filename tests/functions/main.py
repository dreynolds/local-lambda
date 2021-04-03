import os
import json


def debug_me(event, context):
    body = {
        'AWS_DEFAULT_REGION': os.environ.get('AWS_DEFAULT_REGION', ''),
        'AWS_ACCOUNT': os.environ.get('AWS_ACCOUNT', '')
    }
    return {
        "headers": {},
        "statusCode": 200,
        "body": json.dumps(body),
    }
