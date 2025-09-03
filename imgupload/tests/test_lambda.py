import os
import sys
from io import BytesIO

import boto3
from moto import mock_aws
from PIL import Image

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from imgupload.lambda_function import handler, THUMBNAIL_SIZE


@mock_aws
def test_thumbnail_creation():
    os.environ.setdefault('AWS_ACCESS_KEY_ID', 'testing')
    os.environ.setdefault('AWS_SECRET_ACCESS_KEY', 'testing')
    os.environ.setdefault('AWS_SESSION_TOKEN', 'testing')
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
    s3 = boto3.client('s3')
    bucket = 'test-bucket'
    s3.create_bucket(Bucket=bucket)

    # create sample image
    img = Image.new('RGB', (500, 500), color='red')
    buffer = BytesIO()
    img.save(buffer, format='JPEG')
    buffer.seek(0)
    s3.put_object(Bucket=bucket, Key='uploads/test.jpg', Body=buffer.getvalue(), ContentType='image/jpeg')

    event = {
        'Records': [
            {
                's3': {
                    'bucket': {'name': bucket},
                    'object': {'key': 'uploads/test.jpg'}
                }
            }
        ]
    }

    handler(event, None)

    resp = s3.get_object(Bucket=bucket, Key='thumbnails/test.jpg')
    thumb = Image.open(resp['Body'])
    assert thumb.size[0] <= THUMBNAIL_SIZE[0]
    assert thumb.size[1] <= THUMBNAIL_SIZE[1]
