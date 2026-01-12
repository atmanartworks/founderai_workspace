# 🔄 Re-Embedding Documents Guide

## Why Re-Embed?

When you switch embedding models (like from MiniLM to Nomic), you need to re-embed all documents because:
- **Different dimensions**: MiniLM = 384 dims, Nomic = 768 dims
- **Different embeddings**: Same text produces different vectors
- **Database compatibility**: Old embeddings won't work with new model

---

## Method 1: Re-Embed Individual Files (Via Browser)

### Step 1: Get List of Files

Open in browser:
```
http://localhost:8000/api/vault/list
```

Or use Swagger UI:
1. Go to http://localhost:8000/docs
2. Find `GET /api/vault/list`
3. Click "Try it out" → "Execute"
4. Copy the `id` (vault_id) of files you want to re-embed

### Step 2: Re-Embed a File

**Using Swagger UI (Easiest):**

1. Go to http://localhost:8000/docs
2. Find `POST /api/embeddings/embed-document/{vault_id}`
3. Click "Try it out"
4. Enter the `vault_id` in the path parameter
5. Click "Execute"
6. Wait for the response:
   ```json
   {
     "success": true,
     "chunks": 15,
     "vault_id": "your-vault-id"
   }
   ```

**What happens:**
- ✅ Old chunks are deleted automatically (line 86 in embeddings.py)
- ✅ Text is extracted from the file
- ✅ New chunks are created with Nomic embeddings (768 dims)
- ✅ New embeddings are saved to database

---

## Method 2: Re-Embed All Files (Script)

Create a script to re-embed all files at once:

### Option A: Python Script

Create `re_embed_all.py`:

```python
import requests
import time

BASE_URL = "http://localhost:8000"

def re_embed_all():
    # Get all files
    response = requests.get(f"{BASE_URL}/api/vault/list")
    files = response.json().get("files", [])
    
    print(f"Found {len(files)} files to re-embed")
    
    success_count = 0
    error_count = 0
    
    for file in files:
        vault_id = file["id"]
        filename = file["original_name"]
        
        print(f"\nRe-embedding: {filename} (ID: {vault_id})")
        
        try:
            # Re-embed the document
            response = requests.post(
                f"{BASE_URL}/api/embeddings/embed-document/{vault_id}"
            )
            
            if response.status_code == 200:
                result = response.json()
                chunks = result.get("chunks", 0)
                print(f"✅ Success! Created {chunks} chunks")
                success_count += 1
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                error_count += 1
                
            # Small delay to avoid overwhelming the server
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ Exception: {e}")
            error_count += 1
    
    print(f"\n{'='*50}")
    print(f"Summary:")
    print(f"✅ Success: {success_count}")
    print(f"❌ Errors: {error_count}")
    print(f"{'='*50}")

if __name__ == "__main__":
    re_embed_all()
```

**Run it:**
```powershell
python re_embed_all.py
```

### Option B: PowerShell Script

Create `re_embed_all.ps1`:

```powershell
$baseUrl = "http://localhost:8000"

# Get all files
$filesResponse = Invoke-RestMethod -Uri "$baseUrl/api/vault/list" -Method Get
$files = $filesResponse.files

Write-Host "Found $($files.Count) files to re-embed" -ForegroundColor Green

$successCount = 0
$errorCount = 0

foreach ($file in $files) {
    $vaultId = $file.id
    $filename = $file.original_name
    
    Write-Host "`nRe-embedding: $filename (ID: $vaultId)" -ForegroundColor Yellow
    
    try {
        $response = Invoke-RestMethod -Uri "$baseUrl/api/embeddings/embed-document/$vaultId" -Method Post
        
        $chunks = $response.chunks
        Write-Host "✅ Success! Created $chunks chunks" -ForegroundColor Green
        $successCount++
        
        Start-Sleep -Seconds 1
    } catch {
        Write-Host "❌ Error: $_" -ForegroundColor Red
        $errorCount++
    }
}

Write-Host "`n$('='*50)" -ForegroundColor Cyan
Write-Host "Summary:" -ForegroundColor Cyan
Write-Host "✅ Success: $successCount" -ForegroundColor Green
Write-Host "❌ Errors: $errorCount" -ForegroundColor Red
Write-Host "$('='*50)" -ForegroundColor Cyan
```

**Run it:**
```powershell
.\re_embed_all.ps1
```

---

## Method 3: Using JavaScript (Browser Console)

Open browser console (F12) and run:

```javascript
// Re-embed all files
async function reEmbedAll() {
  // Get all files
  const filesResponse = await fetch('http://localhost:8000/api/vault/list');
  const data = await filesResponse.json();
  const files = data.files || [];
  
  console.log(`Found ${files.length} files to re-embed`);
  
  let successCount = 0;
  let errorCount = 0;
  
  for (const file of files) {
    const vaultId = file.id;
    const filename = file.original_name;
    
    console.log(`Re-embedding: ${filename} (ID: ${vaultId})`);
    
    try {
      const response = await fetch(
        `http://localhost:8000/api/embeddings/embed-document/${vaultId}`,
        { method: 'POST' }
      );
      
      if (response.ok) {
        const result = await response.json();
        console.log(`✅ Success! Created ${result.chunks} chunks`);
        successCount++;
      } else {
        console.error(`❌ Error: ${response.status}`);
        errorCount++;
      }
      
      // Small delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
    } catch (error) {
      console.error(`❌ Exception: ${error}`);
      errorCount++;
    }
  }
  
  console.log(`\nSummary: ✅ ${successCount} success, ❌ ${errorCount} errors`);
}

// Run it
reEmbedAll();
```

---

## Method 4: Direct API Call (cURL/PowerShell)

### Re-Embed Single File

**PowerShell:**
```powershell
$vaultId = "your-vault-id-here"
Invoke-RestMethod -Uri "http://localhost:8000/api/embeddings/embed-document/$vaultId" -Method Post
```

**cURL:**
```bash
curl -X POST "http://localhost:8000/api/embeddings/embed-document/your-vault-id-here"
```

---

## What Happens During Re-Embedding?

1. **Finds the file** in `vault_files` table by `vault_id`
2. **Downloads file** from Supabase Storage (if text not cached)
3. **Extracts text** using text extraction service
4. **Chunks the text** into ~1000 char pieces with 200 char overlap
5. **Deletes old chunks** for this vault_id (line 86)
6. **Generates new embeddings** using Nomic model (768 dims)
7. **Saves new chunks** to `document_chunks` table

---

## Verification

After re-embedding, verify it worked:

### Check Chunks Count

```sql
-- In Supabase SQL Editor
SELECT vault_id, COUNT(*) as chunk_count 
FROM document_chunks 
GROUP BY vault_id;
```

### Test Search

Try a semantic search to see if embeddings work:
1. Go to http://localhost:8000/docs
2. Find `POST /api/search/semantic-search`
3. Test with a query related to your documents

---

## Troubleshooting

### "Vault file not found"
- Check the vault_id is correct
- Verify file exists in `/api/vault/list`

### "No usable text found"
- File might be corrupted
- File format might not be supported
- Try re-uploading the file

### "Storage download failed"
- Check file exists in Supabase Storage
- Verify `SUPABASE_BUCKET` is correct
- Check storage permissions

### Slow Re-Embedding
- Normal for large files
- Nomic model takes time to generate embeddings
- Consider re-embedding in batches

---

## Best Practices

1. **Re-embed after model change**: Always re-embed when switching models
2. **Test one file first**: Re-embed a single file to verify it works
3. **Batch processing**: Use scripts for multiple files
4. **Monitor progress**: Watch server logs for errors
5. **Backup first**: Consider backing up old chunks if needed

---

## Quick Reference

| Action | Endpoint | Method |
|--------|----------|--------|
| List files | `/api/vault/list` | GET |
| Re-embed file | `/api/embeddings/embed-document/{vault_id}` | POST |
| Check chunks | SQL query | - |

---

**Ready to re-embed? Start with one file via Swagger UI, then use a script for bulk re-embedding!** 🚀

