# api/index.py
# Vercel Serverless Function Handler for FastAPI

import sys
import os
from pathlib import Path
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Add rag-backend to Python path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

# Change to rag-backend directory for imports
os.chdir(backend_path)

# Import FastAPI app
from app.main import app

# CORS Middleware for Vercel
class CORSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
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

# Add CORS middleware at the top level
app.add_middleware(CORSMiddleware)

# Vercel expects the app to be exported
# FastAPI apps work directly with Vercel's Python runtime
