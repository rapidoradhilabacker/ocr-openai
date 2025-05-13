

from enum import Enum
import aioboto3
from fastapi import UploadFile

class S3BucketContectType(str, Enum):
    JSON =  "application/json"
    PNG = "image/png"
    BINARY ="binary/octet-stream"

class S3FileService():

    def __init__(self, bucket_name: str, aws_access_key_id: str, aws_secret_access_key: str):
        self.bucket_name = bucket_name
        self.session = aioboto3.Session(aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

    async def save_file(self, file_obj: UploadFile, file_name: str) -> str:
        async with self.session.client('s3') as s3_client:
            bucket_location = await s3_client.get_bucket_location(Bucket=self.bucket_name)
            await s3_client.upload_fileobj(file_obj.file, self.bucket_name, file_name, ExtraArgs={'ACL': 'public-read'})
            s3_url = f"https://{self.bucket_name}.s3-{bucket_location['LocationConstraint']}.amazonaws.com/{file_name}"
            return s3_url

    async def save_file_with_content_type(self, file: UploadFile, file_name: str, content_type: S3BucketContectType) -> str:
        async with self.session.client('s3') as s3_client:
            bucket_location = await s3_client.get_bucket_location(Bucket=self.bucket_name)
            await s3_client.upload_fileobj(file.file, self.bucket_name, file_name, ExtraArgs={'ACL': 'public-read', 'ContentType':content_type.value})
            s3_url = f"https://{self.bucket_name}.s3-{bucket_location['LocationConstraint']}.amazonaws.com/{file_name}"
            return s3_url


    async def save_file_with_validity(self, source: str, file_name: str) -> str:
        async with self.session.client('s3') as s3_client:
            bucket_location = await s3_client.get_bucket_location(Bucket=self.bucket_name)
            await s3_client.upload_file(source, self.bucket_name, file_name)
            s3_url = await s3_client.generate_presigned_url(
                ClientMethod='get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': file_name
                },
            ExpiresIn=600
        )
        return s3_url