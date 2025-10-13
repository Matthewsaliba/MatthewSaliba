import os
import boto3
import json

cloudformation = boto3.client('cloudformation')

STACK_NAME = os.environ.get('STACK_NAME')

def lambda_handler(event, context):
    print("Rollback Lambda triggered with event:")
    print(json.dumps(event))

    if not STACK_NAME:
        print("Error: STACK_NAME env var not set")
        return {"status": "error", "message": "STACK_NAME environment variable not set"}

    try:
        response = cloudformation.cancel_update_stack(StackName=STACK_NAME)
        print(f"CancelUpdateStack response: {response}")
        return {"status": "success", "message": "Rollback initiated by cancelling stack update", "stack": STACK_NAME}

    except cloudformation.exceptions.ClientError as e:
        error_msg = str(e)
        print(f"CloudFormation ClientError: {error_msg}")

        if "No update in progress" in error_msg or "cannot be called from current stack status" in error_msg:
            print("No update in progress, nothing to cancel.")
            return {"status": "noop", "message": "No update in progress"}

        raise
