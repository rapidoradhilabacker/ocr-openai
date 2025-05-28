from enum import Enum
from typing import Union
from abc import abstractmethod
import imghdr
import base64
import json
import httpx

# Create a parent class with a factory method and abstract method
class AIServiceBase():

    @abstractmethod
    async def extract_document_info(self, image_bytes: bytes) -> dict:
        """
        Extract information from the provided image bytes.
        Concrete implementations should override this method.
        """
        pass

    def detect_image_format(self, img_bytes: bytes) -> str:
        # First try imghdr detection
        format = imghdr.what(None, img_bytes)
        if format in ['jpeg', 'png', 'gif', 'webp']:
            return format
        
        # Manual format detection as fallback
        if len(img_bytes) >= 2:
            if img_bytes.startswith(b'\xff\xd8'):
                return 'jpeg'
            if img_bytes.startswith(b'\x89PNG\r\n\x1a\n'):
                return 'png'
            if img_bytes.startswith((b'GIF87a', b'GIF89a')):
                return 'gif'
            if len(img_bytes) >= 12 and img_bytes.startswith(b'RIFF') and img_bytes[8:12] == b'WEBP':
                return 'webp'
        
        raise ValueError("Unsupported image format")
