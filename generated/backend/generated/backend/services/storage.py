import os
from typing import Dict
from core.config import settings
import aiobotocore.session


class StorageService:
    @staticmethod
    async def generate_presigned_put(bucket: str, key: str, content_type: str, expires_in: int = 3600) -> Dict[str, str]:
        """Generate a presigned PUT URL for direct upload. Uses aiobotocore session.

        For MinIO local development, set AWS_ENDPOINT_URL in settings.
        """
        session = aiobotocore.session.get_session()
        async with session.create_client('s3', region_name=settings.AWS_REGION,
                                         aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                                         aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                         endpoint_url=settings.AWS_ENDPOINT_URL) as client:
            params = {"Bucket": bucket, "Key": key, "ContentType": content_type}
            url = await client.generate_presigned_url('put_object', Params=params, ExpiresIn=expires_in)
            return {"url": url}

    @staticmethod
    async def generate_presigned_get(bucket: str, key: str, expires_in: int = 3600) -> Dict[str, str]:
        session = aiobotocore.session.get_session()
        async with session.create_client('s3', region_name=settings.AWS_REGION,
                                         aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                                         aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                         endpoint_url=settings.AWS_ENDPOINT_URL) as client:
            params = {"Bucket": bucket, "Key": key}
            url = await client.generate_presigned_url('get_object', Params=params, ExpiresIn=expires_in)
            return {"url": url}