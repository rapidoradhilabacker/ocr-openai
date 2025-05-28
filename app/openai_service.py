import json
import base64
from typing import Dict
from openai import OpenAI
from app.config import SETTINGS
from app.base_service import AIServiceBase
from app.tracing import tracer

class OpenAIService(AIServiceBase):
    def __init__(self):
        self.client = OpenAI(api_key=SETTINGS.OPENAI_KEY)

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

            image_format = self.detect_image_format(image_bytes)

            # Convert image bytes to base64
            mime_type = f'image/{image_format}'
            b64_image = base64.b64encode(image_bytes).decode("utf-8")


            # Create the API request
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": instruction},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{b64_image}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )
            
            # Extract the response content
            content = response.choices[0].message.content.strip()
            
            # Try to find JSON in the response
            try:
                # First try direct JSON parsing
                extracted_data = json.loads(content)
            except json.JSONDecodeError:
                # If direct parsing fails, try to find JSON-like structure
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = content[start_idx:end_idx]
                    extracted_data = json.loads(json_str)
                else:
                    # If no JSON structure found, return empty template
                    extracted_data = json_template
            
            # Validate the extracted data has all required fields
            for key in json_template.keys():
                if key not in extracted_data:
                    extracted_data[key] = ""
            
            extracted_data['file_type'] = image_format
            return extracted_data