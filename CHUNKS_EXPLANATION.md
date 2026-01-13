# 📚 Understanding Chunks Storage

## Why `document_chunks` Table is Empty

**Important:** The `document_chunks` table in Supabase is **NOT used** by the current system. Chunks are stored in **FAISS** (local file storage), not in Supabase.

## How Chunks Are Stored

### Current System (FAISS)
- Chunks are stored in **local files** on the server:
  - `faiss_storage/foundergpt.index` - Vector embeddings
  - `faiss_storage/chunks_metadata.pkl` - Chunk metadata
- Location: `rag-backend/faiss_storage/` directory
- **Problem:** On cloud deployments (Render), this storage is **ephemeral** - it gets wiped on each deployment

### Supabase Table
- The `document_chunks` table exists but is **not populated**
- It's a legacy table or for future use
- **You can ignore it** - it doesn't affect functionality

## How to Fix Missing Chunks

### Option 1: Re-embed Documents (Recommended)

1. **Go to Dashboard** → Vault
2. **Find your document** in the file list
3. **Click "Embed"** button (or the embed icon)
4. **Wait for processing** - this will:
   - Extract text from the document
   - Split into chunks
   - Generate embeddings
   - Save to FAISS

### Option 2: Automatic Fallback (Already Implemented)

The system now **automatically** uses `text_content` if FAISS chunks aren't available:

1. When you click a citation
2. System checks FAISS for chunks
3. If no chunks found, it splits `text_content` into chunks
4. Document viewer works even without embeddings!

## Check Document Status

You can check if a document has chunks using the API:

```bash
GET /api/documents/{document_id}/status?user_id={user_id}
```

This returns:
- `is_embedded`: true if chunks exist in FAISS
- `faiss_chunk_count`: number of chunks
- `has_text_content`: true if text was extracted
- `recommendation`: "embed" or "ready"

## Why Chunks Might Be Missing

1. **Document not embedded yet** - Click "Embed" in Dashboard
2. **FAISS storage cleared** - On Render, storage is ephemeral
3. **Deployment reset** - New deployment = fresh FAISS storage

## Solution for Production

For persistent storage, you have two options:

### Option A: Re-embed After Each Deployment
- Embed documents after each Render deployment
- Quick but manual

### Option B: Use Supabase for Chunks (Future Enhancement)
- Store chunks in `document_chunks` table
- More persistent but requires code changes

## Current Status

✅ **Good News:** The document viewer now works even without FAISS chunks!
- It automatically splits `text_content` into chunks
- Citations will work as long as `text_content` exists in `vault_files` table

## Next Steps

1. **Check if documents have `text_content`:**
   - Go to Supabase → `vault_files` table
   - Check if `text_content` column has data

2. **If `text_content` exists:**
   - Citations will work automatically
   - Document viewer will show chunks

3. **If `text_content` is empty:**
   - Re-upload the document
   - Or re-process it to extract text

4. **For better RAG search:**
   - Embed documents to create FAISS chunks
   - This enables semantic search

---

**TL;DR:** Chunks are in FAISS (local files), not Supabase. The system now automatically uses `text_content` if chunks are missing, so citations should work!
