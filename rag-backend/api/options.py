# api/options.py
# Explicit OPTIONS handler for CORS preflight requests

from fastapi.responses import Response

def handler(request):
    """Handle OPTIONS preflight requests"""
    response = Response()
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Max-Age"] = "3600"
    return response
