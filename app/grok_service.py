import json
import base64
from typing import Dict
import httpx
from app.config import SETTINGS
from app.base_service import AIServiceBase
from app.tracing import tracer
class GrokService(AIServiceBase):
    def __init__(self):
        self.api_key = SETTINGS.GROK_KEY
        self.base_url = "https://api.x.ai/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def extract_document_info(self, image_bytes: bytes) -> dict:
        with tracer.start_as_current_span('extract_document_info_grok') as span:
            json_template = {
                "doc_id": "",
                "doc_type": "",
                "full_name": "",
                "fathers_name": "",
                "address": "",
                "dob": ""
            }

            instruction = f"""
            You are an expert at extracting information from documents. Carefully analyze the provided image and extract the following key details into JSON format.

            Please return ONLY the completed JSON with these fields:
            {json.dumps(json_template, indent=2)}

            Extraction guidelines:

            1. Document ID:
            - Look for any unique identifier in the document
            - This could be a number, alphanumeric code, or reference number

            1. Document Type:
                - Identify the type of document. This field should return either "PAN CARD" or "AADHAAR CARD".
                - For a PAN CARD, look for keywords such as "Permanent Account Number" or a 10-character alphanumeric code.
                - For an AADHAAR CARD, look for terms like "Aadhaar" or a 12-digit numeric sequence.
                - If the document type cannot be clearly determined, leave this field as NA.
            
            2. Full Name:
            - The person's complete name as mentioned in the document
            - Usually appears after labels like "Name:", "Full Name:"
            
            3. Father's Name:
            - Look for text labeled as "Father's Name:"
            - May be preceded by "S/O" (Son Of) or "D/O" (Daughter Of)
            
            4. Address:
            - Complete address as mentioned in the document
            - May span multiple lines
            
            5. Date of Birth:
            - Look for text labeled as "Date of Birth:" or "DOB:"
            - Format should be YYYY-MM-DD
            - Convert other date formats to this standard format

            Important instructions:
            - If any field cannot be clearly identified, leave it as an empty string
            - Do not make assumptions about data you cannot clearly see
            - Return ONLY the completed JSON without any explanations
            - Do not include any additional text or formatting
            - Ensure the response is valid JSON
            """
            # Convert image to base64
            image_format = self.detect_image_format(image_bytes)

            # Convert image bytes to base64
            mime_type = f'image/{image_format}'
            b64_image = base64.b64encode(image_bytes).decode("utf-8")

            # Prepare the request payload
            payload = {
                "model": "grok-1",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": instruction},
                            {
                                "type": "image",
                                "image": {
                                    "data": b64_image,
                                    "type": image_format
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 1000
            }

            # Make the API request
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    raise Exception(f"Grok API error: {response.text}")

                result = response.json()
                extracted_data = json.loads(result["choices"][0]["message"]["content"])
                extracted_data['file_type'] = image_format
                return extracted_data