from fastapi import HTTPException
import httpx
from httpx import Timeout
from app.schemas import (
    S3UploadFileBytesRequest,
    ProductBytes,
    User
)
from app.tracing import tracer
from app.config import SETTINGS

class S3Service:
    """Service for handling S3-related operations"""
    
    def __init__(self):
        self.s3_upload_url_file_bytes = f"{SETTINGS.S3_BASE_URL}/s3/upload/oaas/files/v2"
        self.s3_auth_token = SETTINGS.S3_AUTH_TOKEN
        self.client = httpx.AsyncClient(timeout=30.0)

    def get_s3_headers(self):
        return {
            "Authorization": f"Bearer {self.s3_auth_token}",
            "x-request-id": "3e434",
            "x-app-id": "3434",
            "x-device-id": "dsd",
            "x-business-id": "bef46c45-14ec-4856-a3ef-4fa6f00f57ca"
        }

    async def upload_to_s3_file_bytes(self, user: User, docs: list[ProductBytes], tenant: str) -> dict:
        with tracer.start_as_current_span("upload_to_s3") as span:
            s3_request = S3UploadFileBytesRequest(
                user=user,
                products=docs,
                tenant=tenant
            )

            try:
                response = await self.client.post(
                    self.s3_upload_url_file_bytes,
                    json=s3_request.model_dump(),
                    headers=self.get_s3_headers(),
                    timeout=Timeout(60.0)
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to upload to S3: {str(e)}"
                )
            
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to upload to S3: {str(e)}"
                )
            finally:
                await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
