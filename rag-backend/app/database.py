# app/database.py
from supabase import create_client, Client
# Import centralized config
from app.config import SUPABASE_URL, SUPABASE_KEY_TO_USE, SUPABASE_SERVICE_ROLE_KEY
import logging

# Lazy initialization - don't fail on import if env vars are missing
supabase: Client = None

def get_supabase() -> Client:
    """Get Supabase client, creating it if needed"""
    global supabase
    if supabase is None:
        if not SUPABASE_URL or not SUPABASE_KEY_TO_USE:
            raise Exception("Missing SUPABASE_URL or SUPABASE_KEY/SUPABASE_SERVICE_ROLE_KEY in environment variables")
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY_TO_USE)
        key_type = "service role" if SUPABASE_SERVICE_ROLE_KEY else "anon"
        logging.info(f"✅ Supabase client initialized with {key_type} key")
    return supabase

# For backward compatibility, try to initialize on import
# But don't fail if env vars aren't set yet (they'll be set in Render)
try:
    if SUPABASE_URL and SUPABASE_KEY_TO_USE:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY_TO_USE)
        key_type = "service role" if SUPABASE_SERVICE_ROLE_KEY else "anon"
        logging.info(f"✅ Supabase client initialized on import with {key_type} key")
    else:
        logging.warning("⚠️ SUPABASE_URL or SUPABASE_KEY not set - will initialize on first use")
except Exception as e:
    logging.warning(f"⚠️ Could not initialize Supabase on import: {e} - will initialize on first use")
