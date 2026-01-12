"""
Script to create the 'vault' storage bucket in Supabase
Run this once to set up the storage bucket for document uploads
"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def create_vault_bucket():
    """Create the vault storage bucket"""
    try:
        # Check if bucket already exists
        buckets = supabase.storage.list_buckets()
        bucket_names = [b.name for b in buckets]
        
        if 'vault' in bucket_names:
            print("✅ Vault bucket already exists!")
            return True
        
        # Note: Creating buckets via Python client might require admin privileges
        # You may need to create it manually in Supabase Dashboard
        print("⚠️  Creating storage buckets via Python client requires admin privileges.")
        print("📝 Please create the bucket manually in Supabase Dashboard:")
        print("")
        print("   1. Go to your Supabase project dashboard")
        print("   2. Navigate to Storage section")
        print("   3. Click 'New bucket'")
        print("   4. Set bucket name: 'vault'")
        print("   5. Set to Private (not public)")
        print("   6. Set file size limit: 50 MB (optional)")
        print("   7. Click 'Create bucket'")
        print("")
        print("   Then run the SQL migration to set up RLS policies:")
        print("   File: supabase/migrations/20251108052600_create_vault_bucket.sql")
        print("")
        
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("")
        print("📝 Please create the bucket manually in Supabase Dashboard:")
        print("   1. Go to Storage → New bucket")
        print("   2. Name: 'vault'")
        print("   3. Private bucket")
        print("   4. Create bucket")
        return False

if __name__ == "__main__":
    print("🚀 Setting up Vault Storage Bucket...")
    print("")
    create_vault_bucket()

