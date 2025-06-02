from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Form, Depends
from app.schemas import DocumentResponse, DocumentInfo, AIProvider
from app.service_factory import ServiceFactory
import time
import httpx
from typing import Optional, Union
from app.openai_service import OpenAIService
from app.grok_service import GrokService
from app.config import FILE_UPLOAD_SETTINGS
from io import BytesIO
import asyncio
from app.tracing import tracer
from app.schemas import Trace
from app.auth import get_current_user
from app.s3_file_service import S3Service
from app.schemas import User, ProductBytes, ImageBytes, InboundDocumentType
import base64

router = APIRouter()
DEFAULT_DOC_TYPE = "documents"

@router.post("/extract", response_model=DocumentResponse)
async def extract_document_info(
    file: Optional[UploadFile] = None,
    file_url: Optional[str] = Form(None),
    provider: AIProvider = Form(AIProvider.OPENAI),
    mobile: str = Form(None),
    tenant: str = Form(None),
    trace: Trace = Depends(get_current_user)
):
    start_time = time.time()

    # Start the tracing span for this operation
    with tracer.start_as_current_span("extract_document_info") as span:
        span.set_attribute("component", "document_extraction")
        span.add_event("Start processing request")

        image_bytes = None
        try:
            # Check if an uploaded file is provided
            if file:
                span.add_event("Uploaded file provided")
                image_bytes = await file.read()
                span.set_attribute("file.size", len(image_bytes))
            # Otherwise, check if a file URL is provided
            elif file_url:
                span.add_event("File URL provided")
                async with httpx.AsyncClient() as client:
                    response = await client.get(file_url)
                    span.set_attribute("http.status_code", response.status_code)
                    if response.status_code != 200:
                        span.add_event("Failed to retrieve file from URL")
                        raise HTTPException(status_code=400, detail="Unable to retrieve file from URL")
                    image_bytes = response.content
                    span.set_attribute("file.size", len(image_bytes))
            else:
                span.add_event("No file or URL provided")
                raise HTTPException(status_code=400, detail="No file or file URL provided")
        except Exception as e:
            span.record_exception(e)
            span.set_attribute("error", True)
            raise e

        # Ensure image_bytes is not empty
        if not image_bytes:
            span.add_event("Empty file content", {"error": True})
            raise HTTPException(status_code=400, detail="Empty file content")

        # Get the appropriate service based on the provider
        service: Union[OpenAIService, GrokService] = ServiceFactory.get_service(provider)
        span.add_event("Service selected", {"provider": provider})

        # Initialize the S3 file service for saving the image
        s3_service = S3Service()
        file_name = f"doc_{int(time.time())}.png"
        span.set_attribute("s3.file_name", file_name)

        # Wrap file bytes in a BytesIO if file object is not available
        if file is None:
            file_obj = BytesIO(image_bytes)
            file = UploadFile(filename=file_name, file=file_obj)
            span.add_event("Wrapped file bytes into BytesIO object")

        docs: list[ProductBytes] = [
            ProductBytes(
                product_code=DEFAULT_DOC_TYPE,
                images=[
                    ImageBytes(
                        image_name=file_name,
                        image_type=InboundDocumentType.PNG,
                        image_bytes=base64.b64encode(image_bytes).decode("utf-8")
                    )
                ]
            )
        ]
        user = User(
            mobile_no=mobile,
            company_name=""
        )
        save_task = s3_service.upload_to_s3_file_bytes(user, docs, tenant)
        extract_task = service.extract_document_info(image_bytes)
        span.add_event("Scheduled S3 upload and document extraction tasks")

        try:
            s3_response, result = await asyncio.gather(save_task, extract_task)
            url = s3_response.get('s3_urls', {}).get(DEFAULT_DOC_TYPE, [None])[0]
            span.add_event("Completed asynchronous tasks", {"s3_url": url})
        except Exception as e:
            span.record_exception(e)
            span.set_attribute("error", True)
            raise e

        try:
            doc_info = DocumentInfo(**result)
            span.add_event("Converted extraction result to DocumentInfo model")
        except Exception as e:
            span.record_exception(e)
            span.set_attribute("error", True)
            raise HTTPException(status_code=500, detail="Invalid document information format")

        time_taken = time.time() - start_time
        span.set_attribute("time_taken", round(time_taken, 2))
        span.add_event("Completed processing", {"duration": round(time_taken, 2)})

        return DocumentResponse(
            success=True,
            data=doc_info,
            time_taken=round(time_taken, 2),
            url=url
        )
