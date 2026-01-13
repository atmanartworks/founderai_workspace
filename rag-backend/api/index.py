# api/index.py
# Vercel Serverless Function Handler for FastAPI

import sys
import os
from pathlib import Path

# Add rag-backend to Python path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

# Change to rag-backend directory for imports
os.chdir(backend_path)

# Import FastAPI app
from app.main import app

# Wrap app with CORS handler for Vercel
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import Response

async def cors_handler(request: Request, call_next):
    """Handle CORS for all requests including OPTIONS"""
    # Handle OPTIONS preflight requests
    if request.method == "OPTIONS":
        response = Response()
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Max-Age"] = "3600"
        return response
    
    # For other requests, add CORS headers
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

# Wrap the app with CORS handler
app.middleware("http")(cors_handler)

# Vercel expects the app to be exported
# FastAPI apps work directly with Vercel's Python runtime
