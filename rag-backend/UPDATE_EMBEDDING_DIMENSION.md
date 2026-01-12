# 🔧 Update Embedding Dimension: 384 → 768

## Current Status

Your `embedding` column exists and is type `vector`, but we need to check and update its dimension.

---

## Step 1: Check Current Dimension

Run this query in Supabase SQL Editor to see the actual dimension:

```sql
-- Check embedding column details
SELECT 
    attname as column_name,
    atttypid::regtype as type_name
FROM pg_attribute
WHERE attrelid = 'document_chunks'::regclass
AND attname = 'embedding';
```

**Expected results:**
- If you see `vector(384)` → **Needs update**
- If you see `vector(768)` → **Already correct!**

---

## Step 2: Update to 768 Dimensions

**⚠️ IMPORTANT: Delete old chunks first!**

Old chunks with 384 dimensions will cause issues. Delete them first:

```sql
-- Delete all existing chunks (they have wrong dimensions)
DELETE FROM document_chunks;
```

**Then update the column:**

```sql
-- Step 1: Drop old indexes
DROP INDEX IF EXISTS document_chunks_embedding_idx;
DROP INDEX IF EXISTS document_chunks_embedding_idx1;

-- Step 2: Update column dimension
ALTER TABLE document_chunks 
ALTER COLUMN embedding TYPE vector(768);

-- Step 3: Recreate index for vector search
CREATE INDEX document_chunks_embedding_idx 
ON document_chunks 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

---

## Step 3: Verify the Update

Run this to confirm:

```sql
SELECT 
    attname as column_name,
    atttypid::regtype as type_name
FROM pg_attribute
WHERE attrelid = 'document_chunks'::regclass
AND attname = 'embedding';
```

Should show: `vector(768)`

---

## Step 4: Re-Embed Your Files

After updating the schema:

1. **Upload new files** - They'll automatically use 768 dimensions
2. **Or re-embed existing files**:
   ```powershell
   python re_embed_all.py
   ```

---

## Complete SQL Script (All-in-One)

```sql
-- Complete migration: Update embedding dimension to 768

-- 1. Delete old chunks (optional but recommended)
DELETE FROM document_chunks;

-- 2. Drop old indexes
DROP INDEX IF EXISTS document_chunks_embedding_idx;
DROP INDEX IF EXISTS document_chunks_embedding_idx1;

-- 3. Update column dimension
ALTER TABLE document_chunks 
ALTER COLUMN embedding TYPE vector(768);

-- 4. Recreate index
CREATE INDEX document_chunks_embedding_idx 
ON document_chunks 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- 5. Verify
SELECT 
    attname as column_name,
    atttypid::regtype as type_name
FROM pg_attribute
WHERE attrelid = 'document_chunks'::regclass
AND attname = 'embedding';
```

---

## Troubleshooting

### "Permission denied"
- Make sure you're using the **Service Role Key** in Supabase
- Or use the Supabase Dashboard SQL Editor (has proper permissions)

### "Column does not exist"
- Check table name: `document_chunks` (not `document_chunk`)
- Verify you're in the correct database

### "Cannot alter type"
- Make sure you deleted old chunks first
- Or use: `ALTER TABLE document_chunks ALTER COLUMN embedding TYPE vector(768) USING embedding::vector(768);`

---

## After Migration

✅ Upload files - should work with 768-dim embeddings
✅ Re-embed existing files - will create new 768-dim embeddings
✅ Search/chat - will work with Nomic model

---

**Run the complete SQL script above, then try uploading again!** 🚀

