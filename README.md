# Document Information Extractor

A FastAPI application that extracts information from documents using OCR and AI processing.

## Features

- Document information extraction using OCR
- AI-powered information parsing using OpenAI GPT-4
- Structured JSON response with document details
- Scalable architecture for future enhancements

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
```bash
source venv/bin/activate  # Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy example.env to .env and fill in your API keys:
```bash
cp example.env .env
```

5. Run the application:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

### POST /api/v1/documents/extract

Upload a document image to extract information.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: file (image file)

**Response:**
```json
{
    "success": true,
    "data": {
        "doc_id": "string",
        "full_name": "string",
        "fathers_name": "string",
        "address": "string",
        "dob": "string"
    }
}
```

## Project Structure

```
.
├── app/
│   ├── api/
│   │   └── endpoints/
│   │       └── document.py
│   ├── core/
│   │   └── config.py
│   ├── schemas/
│   │   └── document.py
│   ├── services/
│   │   └── openai_service.py
│   └── main.py
├── requirements.txt
└── README.md
```
