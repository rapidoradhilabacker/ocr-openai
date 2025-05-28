from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.document import router
from app.config import SETTINGS

app = FastAPI(
    title=SETTINGS.PROJECT_NAME,
    openapi_url=f"{SETTINGS.API_V1_STR}/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix=f"{SETTINGS.API_V1_STR}/documents", tags=["documents"])
