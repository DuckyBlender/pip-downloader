import json
import os
import boto3
import platform
import uuid
import subprocess

# import requests

s3_client = boto3.client('s3')


def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """
    
    # Get the "packages" list from the body
    architecture = platform.processor()
    print("Architecture: ", architecture)
    
    packages = event.get("packages", [])
    print("Downloading packages: ", packages)
    result = subprocess.run(["mkdir", "/tmp/pip_layer"], capture_output=True, text=True)
    print(f"STDOUT: {result.stdout}")
    # os.system(f"pip install {' '.join(packages)} --target /tmp/pip_layer")
    result = subprocess.run(["pip", "install", *packages, "--target", "/tmp/pip_layer", "-q"], capture_output=True, text=True)
    print(f"STDOUT: {result.stdout}")
    print("Packages downloaded!")
    print("Zipping packages...")
    # os.system(f"zip -r /tmp/pip_layer.zip /tmp/pip_layer")
    result = subprocess.run(["zip", "-r", "/tmp/pip_layer.zip", "/tmp/pip_layer"], capture_output=True, text=True)
    print(f"STDOUT: {result.stdout}")
    print("Packages zipped!")
    print("Sending packages to S3...")
    # This time using boto3
    with open("/tmp/pip_layer.zip", "rb") as f:
        s3_client.upload_fileobj(f, "x86-pip-downloader", f"{uuid.uuid4().hex}.zip")
    
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Packages downloaded and uploaded to S3!",
            "architecture": architecture,
            "packages": packages,
            "s3_bucket": "x86_pip_downloader_lambda",
            "url": f"https://s3.eu-central-1.amazonaws.com/x86-pip-downloader/{uuid.uuid4().hex}.zip"
        }),
    }
