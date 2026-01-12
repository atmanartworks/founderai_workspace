# scripts/test_upload_local.py
import os
from app.database import supabase

LOCAL_PATH = "/mnt/data/response_1763621672334.html"   # your uploaded file path
USER_ID = "d07a8fbe-0655-49ae-bda0-fe7bbfa0ef09"

def run():
    if not os.path.exists(LOCAL_PATH):
        print("Local file not found:", LOCAL_PATH)
        return
    name = os.path.basename(LOCAL_PATH)
    storage_path = f"{USER_ID}/{name}"
    with open(LOCAL_PATH, "rb") as f:
        content = f.read()
    supabase.storage.from_("vault").upload(path=storage_path, file=content)
    file_data = {
        "user_id": USER_ID,
        "storage_path": storage_path,
        "original_name": name,
        "file_size": len(content),
        "content_type": "text/html"
    }
    inserted = supabase.table("vault_files").insert(file_data).execute()
    print("Inserted vault_files:", inserted.data)
    vault_id = inserted.data[0]["id"]
    print("Now call POST /api/embeddings/embed-document/{vault_id} via swagger or curl to embed.")
if __name__ == "__main__":
    run()
