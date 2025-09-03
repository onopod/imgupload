import os
from io import BytesIO

import boto3
from PIL import Image

THUMBNAIL_SIZE = (128, 128)


def handler(event, context, s3_client=None):
    """Resize uploaded images and store thumbnails."""
    s3 = s3_client or boto3.client("s3")
    for record in event.get("Records", []):
        bucket = record["s3"]["bucket"]["name"]
        key = record["s3"]["object"]["key"]

        if not key.lower().startswith("uploads/"):
            continue

        if not key.lower().endswith((".jpg", ".jpeg", ".png")):
            continue

        file_name = os.path.basename(key)
        thumb_key = f"thumbnails/{file_name}"

        obj = s3.get_object(Bucket=bucket, Key=key)
        image = Image.open(obj["Body"])
        image.thumbnail(THUMBNAIL_SIZE)

        buffer = BytesIO()
        image.save(buffer, format=image.format)
        buffer.seek(0)

        s3.put_object(Bucket=bucket, Key=thumb_key, Body=buffer, ContentType=obj.get("ContentType"))

    return {"statusCode": 200}
