"""
Script to re-embed all uploaded documents with the current embedding model.
Useful when switching embedding models (e.g., from MiniLM to Nomic).
"""
import requests
import time
import sys

BASE_URL = "http://localhost:8000"

def re_embed_all():
    """Re-embed all files in the vault"""
    print("🔄 Re-Embedding All Documents")
    print("=" * 50)
    
    # Get all files
    try:
        response = requests.get(f"{BASE_URL}/api/vault/list")
        response.raise_for_status()
        files = response.json().get("files", [])
    except Exception as e:
        print(f"❌ Error fetching files: {e}")
        print("Make sure the server is running on http://localhost:8000")
        sys.exit(1)
    
    if not files:
        print("ℹ️  No files found to re-embed")
        return
    
    print(f"📁 Found {len(files)} files to re-embed\n")
    
    success_count = 0
    error_count = 0
    skipped_count = 0
    
    for idx, file in enumerate(files, 1):
        vault_id = file["id"]
        filename = file.get("original_name", "Unknown")
        file_size = file.get("file_size", 0)
        
        print(f"[{idx}/{len(files)}] Processing: {filename}")
        print(f"  Vault ID: {vault_id}")
        print(f"  Size: {file_size:,} bytes")
        
        try:
            # Re-embed the document
            response = requests.post(
                f"{BASE_URL}/api/embeddings/embed-document/{vault_id}",
                timeout=300  # 5 minute timeout for large files
            )
            
            if response.status_code == 200:
                result = response.json()
                chunks = result.get("chunks", 0)
                print(f"  ✅ Success! Created {chunks} chunks")
                success_count += 1
            elif response.status_code == 404:
                print(f"  ⚠️  File not found (may have been deleted)")
                skipped_count += 1
            else:
                error_msg = response.text
                print(f"  ❌ Error {response.status_code}: {error_msg[:100]}")
                error_count += 1
                
        except requests.exceptions.Timeout:
            print(f"  ⏱️  Timeout - file may be too large")
            error_count += 1
        except Exception as e:
            print(f"  ❌ Exception: {str(e)[:100]}")
            error_count += 1
        
        # Small delay to avoid overwhelming the server
        if idx < len(files):
            time.sleep(1)
        
        print()
    
    # Summary
    print("=" * 50)
    print("📊 Summary:")
    print(f"  ✅ Success: {success_count}")
    print(f"  ❌ Errors: {error_count}")
    print(f"  ⚠️  Skipped: {skipped_count}")
    print(f"  📁 Total: {len(files)}")
    print("=" * 50)
    
    if success_count > 0:
        print("\n🎉 Re-embedding complete!")
        print("You can now test search/chat with the new embeddings.")

if __name__ == "__main__":
    try:
        re_embed_all()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)

