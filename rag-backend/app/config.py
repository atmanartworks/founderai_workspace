# app/config.py
"""
Centralized configuration loader for the application.
Loads .env file once and provides access to all environment variables.
"""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Determine the project root (rag-backend directory)
# This file is at: rag-backend/app/config.py
# Project root is: rag-backend/
PROJECT_ROOT = Path(__file__).parent.parent
ENV_FILE = PROJECT_ROOT / '.env'

# Load .env file with explicit path
if ENV_FILE.exists():
    load_dotenv(dotenv_path=ENV_FILE, override=True)
    logging.info(f"✅ Loaded .env from: {ENV_FILE}")
    
    # Verify key variables are loaded
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        # Try reading the file directly to find the key
        try:
            with open(ENV_FILE, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # Look for OPENAI lines (case-insensitive)
                openai_lines = [l.strip() for l in lines if 'OPENAI' in l.upper() and not l.strip().startswith('#')]
                if openai_lines:
                    logging.warning(f"⚠️ Found OPENAI lines in .env but not loaded properly:")
                    for line in openai_lines:
                        # Show the line but mask the value
                        if '=' in line:
                            key, value = line.split('=', 1)
                            logging.warning(f"  - {key.strip()}=*** (value length: {len(value.strip())})")
                            # Try to manually parse and set if it's OPENAI_API_KEY
                            if key.strip().upper() == 'OPENAI_API_KEY':
                                # Remove quotes if present
                                clean_value = value.strip().strip('"').strip("'")
                                os.environ["OPENAI_API_KEY"] = clean_value
                                openai_key = clean_value
                                logging.info(f"✅ Manually loaded OPENAI_API_KEY from .env")
                        else:
                            logging.warning(f"  - {line} (no '=' found, may be malformed)")
                else:
                    logging.error(f"❌ No OPENAI_API_KEY line found in .env file")
                    logging.error(f"")
                    logging.error(f"═══════════════════════════════════════════════════════════")
                    logging.error(f"  MISSING: OPENAI_API_KEY in .env file")
                    logging.error(f"═══════════════════════════════════════════════════════════")
                    logging.error(f"")
                    logging.error(f"Please add this line to your .env file:")
                    logging.error(f"  OPENAI_API_KEY=sk-your-api-key-here")
                    logging.error(f"")
                    logging.error(f"Current .env file contains:")
                    for i, line in enumerate(lines[:20], 1):
                        if line.strip() and not line.strip().startswith('#'):
                            # Mask sensitive values
                            if '=' in line:
                                key, value = line.split('=', 1)
                                logging.error(f"  {i}: {key.strip()}=***")
                            else:
                                logging.error(f"  {i}: {line.strip()}")
                    logging.error(f"")
                    logging.error(f"After adding OPENAI_API_KEY, restart the server.")
                    logging.error(f"═══════════════════════════════════════════════════════════")
        except Exception as e:
            logging.error(f"Error reading .env file: {e}")
    
    if openai_key:
        logging.info(f"✅ OPENAI_API_KEY loaded (length: {len(openai_key)})")
else:
    # Fallback: try current directory
    cwd_env = Path.cwd() / '.env'
    if cwd_env.exists():
        load_dotenv(dotenv_path=cwd_env, override=True)
        logging.info(f"✅ Loaded .env from: {cwd_env}")
    else:
        # Last resort: default load_dotenv
        load_dotenv()
        logging.warning("⚠️ Using default load_dotenv() - .env file location unknown")

# Export commonly used environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
# Prefer service role key for backend (bypasses RLS), fallback to anon key
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
# Use service role key if available, otherwise use anon key
SUPABASE_KEY_TO_USE = SUPABASE_SERVICE_ROLE_KEY or SUPABASE_KEY
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "vault")

# Get OPENAI_API_KEY (may have been manually set above)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
LOCAL_EMBEDDING_MODEL = os.getenv("LOCAL_EMBEDDING_MODEL", "nomic-ai/nomic-embed-text-v1")

