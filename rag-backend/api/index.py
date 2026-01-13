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

# Vercel expects the app to be exported
# FastAPI apps work directly with Vercel's Python runtime
