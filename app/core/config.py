from pydantic_settings import BaseSettings
from functools import lru_cache
from enum import Enum
from pydantic import validator

class FileUploadServer(str, Enum):
    LOCAL: str = "local"
    S3: str = "s3"


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Document Information Extractor"
    
    # API Keys
    OPENAI_KEY: str
    GROK_KEY: str

    class Config:
        env_prefix = 'API_'


class FileUploadSettings(BaseSettings):
    server: FileUploadServer
    bucket: str
    access_key: str | None
    key_id: str | None
    
    @validator('access_key', 'key_id')
    def validate_s3_credentials(cls, value, values):
        if values['server'] == FileUploadServer.S3 and value is None:
            raise ValueError(f"'access_key' and 'key_id' cannot be None when 'server' is 's3'")
        return value

    class Config:
        env_prefix = 'FILE_UPLOAD_'

FILE_UPLOAD_SETTINGS = FileUploadSettings()
SETTINGS = Settings()

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
