# 🔧 Fix Embedding Dimension Error

## Problem

You're getting this error:
```
Failed inserting chunks: {'message': 'expected 384 dimensions, not 768', 'code': '22000'}
```

**Why?**
- Your database `document_chunks` table has an `embedding` column set to **384 dimensions** (for MiniLM)
- Nomic model produces **768-dimensional** embeddings
- Database constraint rejects the 768-dim vectors

---

## Solution: Update Database Schema

You need to update the embedding column dimension in Supabase.

### Step 1: Open Supabase SQL Editor

1. Go to your Supabase Dashboard
2. Navigate to **SQL Editor**
3. Click **New Query**

### Step 2: Run This SQL

```sql
-- First, drop the old constraint/index if it exists
ALTER TABLE document_chunks 
DROP CONSTRAINT IF EXISTS document_chunks_embedding_check;

-- Update the embedding column to accept 768 dimensions
ALTER TABLE document_chunks 
ALTER COLUMN embedding TYPE vector(768);

-- Recreate the index for vector similarity search
CREATE INDEX IF NOT EXISTS document_chunks_embedding_idx 
ON document_chunks 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

### Step 3: Verify the Change

Run this to check:
```sql
SELECT 
    column_name, 
    data_type,
    udt_name
FROM information_schema.columns 
WHERE table_name = 'document_chunks' 
AND column_name = 'embedding';
```

You should see `vector(768)` or similar.

---

## Alternative: If You Get Permission Errors

If you don't have permission to alter the table, you may need to:

1. **Use Supabase Dashboard → Table Editor**
   - Go to `document_chunks` table
   - Check if you can modify the column type there

2. **Or Create a Migration**

Create a new migration file in Supabase:
- Go to **Database → Migrations**
- Create new migration
- Paste the SQL above
- Apply it

---

## After Fixing: Re-Embed All Documents

Once the schema is updated:

1. **Delete old chunks** (they have wrong dimensions):
   ```sql
   DELETE FROM document_chunks;
   ```

2. **Re-embed all files** using the script:
   ```powershell
   python re_embed_all.py
   ```

Or re-embed via Swagger UI one by one.

---

## Quick Fix Script

If you want to automate this, here's a Python script to check and guide you:

```python
# check_embedding_dimension.py
from app.database import supabase

try:
    # Try to insert a test 768-dim vector
    test_embedding = [0.1] * 768
    
    result = supabase.table("document_chunks").insert({
        "vault_id": "test",
        "user_id": "test",
        "content": "test",
        "chunk_index": 0,
        "tokens": 10,
        "embedding": test_embedding
    }).execute()
    
    print("✅ Database accepts 768 dimensions!")
    
    # Clean up test
    supabase.table("document_chunks").delete().eq("vault_id", "test").execute()
    
except Exception as e:
    if "expected 384 dimensions" in str(e):
        print("❌ Database still expects 384 dimensions")
        print("Run the SQL migration in Supabase to fix this")
    else:
        print(f"Error: {e}")
```

---

## Prevention: Always Match Dimensions

When switching embedding models:
1. ✅ Check model dimensions first
2. ✅ Update database schema BEFORE embedding
3. ✅ Delete old chunks
4. ✅ Re-embed with new model

---

## Model Dimensions Reference

| Model | Dimensions |
|-------|-----------|
| all-MiniLM-L6-v2 | 384 |
| nomic-embed-text-v1 | 768 |
| all-mpnet-base-v2 | 768 |
| paraphrase-multilingual-MiniLM-L12-v2 | 384 |

---

**After running the SQL migration, try uploading again!** 🚀

