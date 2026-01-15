# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# Import config to ensure .env is loaded
from app import config

app = FastAPI(title="RAG Backend")

# CORS (adjust origins as needed)
# Note: allow_credentials cannot be True with allow_origins=["*"]
# For development and production, allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (works for both localhost and production)
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    allow_credentials=False,
)

# Health check endpoint
@app.get("/health")
def health():
    return {"status": "healthy"}

# Explicit OPTIONS handler for CORS preflight
@app.options("/{full_path:path}")
async def options_handler(full_path: str):
    from fastapi.responses import Response
    response = Response()
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Max-Age"] = "3600"
    return response

# Import routers (these modules must exist)
from app.routes import embeddings, chat, vault, search, documents

app.include_router(vault.router)
app.include_router(embeddings.router)
app.include_router(chat.router)
app.include_router(search.router)
app.include_router(documents.router)
