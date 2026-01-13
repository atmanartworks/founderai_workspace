# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# Import config to ensure .env is loaded
from app import config

app = FastAPI(title="RAG Backend")

# CORS (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Health check endpoint
@app.get("/health")
def health():
    return {"status": "healthy"}

# Import routers (these modules must exist)
from app.routes import embeddings, chat, vault, search

app.include_router(vault.router)
app.include_router(embeddings.router)
app.include_router(chat.router)
app.include_router(search.router)
