# verify_vault_files.py
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "vault")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def verify_vault_files():
    print("🔍 Checking vault_files entries against Supabase storage...")
    vault_files = supabase.table("vault_files").select("id, storage_path, original_name").execute()
    missing = []

    for f in vault_files.data:
        try:
            supabase.storage.from_(SUPABASE_BUCKET).download(f["storage_path"])
        except Exception:
            print(f"❌ MISSING: {f['original_name']} ({f['storage_path']})")
            missing.append(f)
        else:
            print(f"✅ Found: {f['original_name']}")

    print("\nSummary:")
    print(f"✅ Found: {len(vault_files.data) - len(missing)}")
    print(f"❌ Missing: {len(missing)}")

    if missing:
        print("\nList of missing files:")
        for f in missing:
            print(f"- {f['original_name']} ({f['id']})")

if __name__ == "__main__":
    verify_vault_files()
