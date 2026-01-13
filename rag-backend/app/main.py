# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# Import config to ensure .env is loaded
from app import config

app = FastAPI(title="RAG Backend")

# CORS (adjust origins as needed)
# Note: allow_credentials cannot be True with allow_origins=["*"]
# For Vercel, we allow all origins without credentials
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
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
from app.routes import embeddings, chat, vault, search

app.include_router(vault.router)
app.include_router(embeddings.router)
app.include_router(chat.router)
app.include_router(search.router)
