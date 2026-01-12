# app/utils/fix_storage_paths.py

from supabase import create_client
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BUCKET = os.getenv("SUPABASE_BUCKET", "vault")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def check_storage_paths():
    """
    1. Get all vault_files
    2. For each, check if storage file exists
    3. Return list of missing/broken entries
    """

    broken = []

    rec = supabase.table("vault_files").select(
        "id, storage_path, original_name"
    ).execute()

    for row in rec.data:
        vid = row["id"]
        path = row["storage_path"]

        try:
            # Try to download the file
            supabase.storage.from_(BUCKET).download(path)
        except Exception:
            broken.append({
                "vault_id": vid,
                "storage_path": path,
                "file": row["original_name"]
            })

    return {
        "total_rows": len(rec.data),
        "broken_files": broken,
        "broken_count": len(broken)
    }
