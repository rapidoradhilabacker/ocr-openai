from pydantic import BaseModel
from datetime import date
from typing import Optional
from pydantic.networks import HttpUrl
from enum import Enum
from humps import camelize
from typing import Any, Self

def to_camel(string):
    return camelize(string)

class CamelModel(BaseModel):
    class Config:
        alias_generator = to_camel
        populate_by_name = True

class AIProvider(str, Enum):
    OPENAI = "openai"
    GROK = "grok"

class InboundDocumentType(str, Enum):
    PDF = "application/pdf"
    IMAGE = "image/jpeg"
    ZIP = "application/zip"
    JSON = "application/json"
    PNG = "image/png"
    BINARY = "binary/octet-stream"

class DocumentInfo(BaseModel):
    doc_id: str
    doc_type: str
    file_type: str
    full_name: str
    fathers_name: Optional[str] = None
    address: Optional[str] = None
    dob: Optional[date] = None

class DocumentResponse(BaseModel):
    success: bool
    data: Optional[DocumentInfo] = None
    error: Optional[str] = None
    time_taken: float
    url: Optional[str] = None


class SuccessCode(str, Enum):
   SUCCESS = '200'

class ErrorCode(str, Enum):
   ERROR_CODE_NA = ''
   ERROR_CODE_UNKNOWN = 'EONDC0000'
   ERROR_CODE_INVALID_REQUEST_ID = 'EONDC0001'
   ERROR_CODE_INVALID_TOKEN = 'EONDC0003'
   ERROR_CODE_INVALID_REQUEST = 'EONDC0007'
   ERROR_CODE_INTEGRATION_ERROR = 'EONDC0008'
   ERROR_CODE_AUTH_ERROR = 'EONDC0077'
   ERROR_CODE_ALREADY_EXISTS = 'EONDC0011'
   ERROR_CODE_DUPLICATE_REQUEST = 'EONDC0005'
   ERROR_CODE_ENTITY_NOT_EXIST = 'EONDC0006'
   ERROR_CODE_TIMEOUT = 'EONDC0010'

class GenericResponse(CamelModel):
    error_code: ErrorCode
    customer_message: str
    code: str
    status: bool
    debug_info: dict[str, Any] | None = None
    info: dict[str, Any] | None = None

    @classmethod
    def get_error_response(cls, error_code: ErrorCode, customer_message: str, debug_info: dict[str, Any] | None = None, info: dict[str, Any] | None = None):
        return GenericResponse(
            error_code=error_code,
            customer_message=customer_message,
            debug_info=debug_info,
            info=info,
            status=False,
            code=''
        )

    @classmethod
    def get_success_response(cls, customer_message: str, debug_info: dict[str, Any] | None = None, info: dict[str, Any] | None = None) -> Self:
        return cls(
            error_code=ErrorCode.ERROR_CODE_NA,
            customer_message=customer_message,
            debug_info=debug_info,
            info=info,
            status=True,
            code=SuccessCode.SUCCESS
        )

    @property
    def is_error_response(self):
        return not self.status


class Trace(BaseModel):
    request_id: str
    device_id: str

class TokenRequest(BaseModel):
    """
    Request model for generating authentication tokens
    """
    service_id: str

class TokenResponse(BaseModel):
    """
    Response model for token generation endpoint
    """
    token: str
    expires_at: str
    
    class Config:
        schema_extra = {
            "example": {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "expires_at": "2025-08-29T06:54:39Z"
            }
        }

class User(BaseModel):
    mobile_no: str  
    company_name: Optional[str] = ""

class ImageBytes(BaseModel):
    image_name: str
    image_type: InboundDocumentType
    image_bytes: str

class ProductBytes(BaseModel):
    product_code: str
    images: list[ImageBytes]
    
class S3UploadFileBytesRequest(BaseModel):
    user: User
    products: list[ProductBytes]
    tenant: str = 'placeorder'