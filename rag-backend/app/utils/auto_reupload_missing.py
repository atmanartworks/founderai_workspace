# app/utils/auto_reupload_missing.py

from supabase import create_client
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BUCKET = os.getenv("SUPABASE_BUCKET", "vault")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def auto_reupload_missing():
    """
    1. Detect missing files in storage
    2. Remove bad metadata
    3. Return vault_ids needing re-upload
    """

    result = supabase.table("vault_files").select(
        "id, storage_path, original_name"
    ).execute()

    missing = []

    for row in result.data:
        vault_id = row["id"]
        path = row["storage_path"]

        try:
            supabase.storage.from_(BUCKET).download(path)
        except Exception:
            missing.append(row)

    # Delete bad metadata
    for item in missing:
        supabase.table("vault_files").delete().eq("id", item["id"]).execute()
        supabase.table("vault").delete().eq("id", item["id"]).execute()
        supabase.table("document_chunks").delete().eq("vault_id", item["id"]).execute()

    return {
        "missing_files": missing,
        "reupload_required": [m["id"] for m in missing],
        "removed_from_db": len(missing)
    }
