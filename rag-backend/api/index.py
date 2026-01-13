# api/index.py
# Vercel Serverless Function Handler for FastAPI

import sys
import os
from pathlib import Path
from starlette.responses import Response

# Add rag-backend to Python path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

# Change to rag-backend directory for imports
os.chdir(backend_path)

# Import FastAPI app
from app.main import app as fastapi_app

# Wrap app with ASGI middleware that handles OPTIONS at the lowest level
async def cors_wrapper(scope, receive, send):
    """ASGI wrapper that handles OPTIONS before FastAPI"""
    if scope["type"] == "http":
        method = scope.get("method", "")
        
        # Handle OPTIONS requests immediately - this is critical for CORS
        if method == "OPTIONS":
            response = Response()
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
            response.headers["Access-Control-Allow-Headers"] = "*"
            response.headers["Access-Control-Max-Age"] = "3600"
            await response(scope, receive, send)
            return
    
    # For all other requests, pass to FastAPI app
    await fastapi_app(scope, receive, send)

# Export the wrapped app for Vercel
# Vercel expects the app to be exported - use the wrapper that handles OPTIONS first
# This ensures OPTIONS requests are handled before FastAPI routing
app = cors_wrapper
