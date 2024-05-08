import json
import os
import boto3
import platform
import uuid
import subprocess
import shutil

# import requests

s3_client = boto3.client('s3')


def lambda_handler(event, context):
    architecture = platform.processor()
    print("Architecture: ", architecture)
    # If the architecture is NOT x86_64 and NOT aarch64, return an error
    if architecture not in ["x86_64", "aarch64"]:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": "Unsupported architecture",
                "architecture": architecture
            }),
        }
        
    bucket_prefix = "x86" if architecture == "x86_64" else "arm64"
    
    # Get the "packages" list from the body
    
    packages = event.get("packages", [])
    print("Downloading packages: ", packages)
    os.system(f"rm -rf /tmp/pip_layer")
    os.system(f"mkdir /tmp/pip_layer")
    os.system(f"pip install {' '.join(packages)} --target /tmp/pip_layer")
    print("Packages downloaded!")
    # run ls to prove
    result = subprocess.run(["ls", "/tmp/pip_layer"], capture_output=True, text=True)
    print("Files downloaded: ", result.stdout)
    print("Zipping packages...")
    # os.system(f"zip -r /tmp/pip_layer.zip /tmp/pip_layer")
    # result = subprocess.run(["zip", "-r", "/tmp/pip_layer.zip", "/tmp/pip_layer"], capture_output=True, text=True)
    shutil.make_archive("/tmp/pip_layer", "zip", "/tmp/pip_layer")
    print("Packages zipped!")
    print("Sending packages to S3...")
    bucket = f"{bucket_prefix}-pip-downloader"
    # This time using boto3
    with open("/tmp/pip_layer.zip", "rb") as f:
        s3_client.upload_fileobj(f, bucket, f"{uuid.uuid4().hex}.zip")
    
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Packages downloaded and uploaded to S3!",
            "architecture": architecture,
            "packages": packages,
            "s3_bucket": bucket,
            "url": f"https://s3.eu-central-1.amazonaws.com/{bucket}/{uuid.uuid4().hex}.zip"
        }),
    }
