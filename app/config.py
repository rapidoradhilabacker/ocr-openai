from pydantic_settings import BaseSettings
from functools import lru_cache
from enum import Enum
from pydantic import validator

class FileUploadServer(str, Enum):
    LOCAL = "local"
    S3 = "s3"


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Document Information Extractor"
    
    # API Keys
    OPENAI_KEY: str = ""
    GROK_KEY: str = ""

    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = ""
    SERVICE_ID: str = ""

    S3_BASE_URL: str = ""
    S3_AUTH_TOKEN: str = ""

    class Config:
        env_prefix = 'API_'


class FileUploadSettings(BaseSettings):
    server: FileUploadServer = FileUploadServer.LOCAL
    bucket: str = ""
    access_key: str = ""
    key_id: str = ""
    
    @validator('access_key', 'key_id')
    def validate_s3_credentials(cls, value, values):
        if values['server'] == FileUploadServer.S3 and value is None:
            raise ValueError(f"'access_key' and 'key_id' cannot be None when 'server' is 's3'")
        return value

    class Config:
        env_prefix = 'FILE_UPLOAD_'


@lru_cache()
def get_settings():
    return Settings()

@lru_cache()
def get_file_upload_settings():
    return FileUploadSettings()

SETTINGS = get_settings()
FILE_UPLOAD_SETTINGS = get_file_upload_settings()