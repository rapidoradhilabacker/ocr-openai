from pydantic import BaseModel
from datetime import date
from typing import Optional
from pydantic.networks import HttpUrl
from enum import Enum

class AIProvider(str, Enum):
    OPENAI = "openai"
    GROK = "grok"

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