# FAISS Migration Guide

## Overview

The RAG system has been migrated from Supabase PostgreSQL (pgvector) to FAISS for local vector storage.

## What Changed

### ✅ New Components

1. **FAISS Vector Store** (`app/services/faiss_store.py`)
   - Local FAISS index storage
   - Metadata stored in pickle files
   - Multi-user support via user_id filtering
   - Per-vault filtering support

2. **Updated Embeddings Route** (`app/routes/embeddings.py`)
   - Now uses FAISS instead of Supabase `document_chunks` table
   - Embeddings are normalized for cosine similarity
   - Chunks stored locally in `faiss_storage/` directory

3. **Updated Chat Route** (`app/routes/chat.py`)
   - Queries FAISS index instead of Supabase RPC
   - Maintains user_id and vault_id filtering
   - Same API interface (no breaking changes)

### 📦 Dependencies

Added to `requirements.txt`:
- `faiss-cpu>=1.7.4` - FAISS library for vector search
- `numpy>=1.24.0` - Required by FAISS

### 🗂️ Storage Structure

```
rag-backend/
└── faiss_storage/
    ├── foundergpt.index      # FAISS index file
    └── chunks_metadata.pkl   # Chunk metadata (content, vault_id, user_id, etc.)
```

## Installation

1. **Install new dependencies:**
   ```bash
   pip install faiss-cpu numpy
   ```

2. **Restart the server:**
   ```bash
   uvicorn app.main:app --reload
   ```

## How It Works

### 1. Document Embedding Flow

1. User uploads file → stored in Supabase `vault_files` table
2. User calls `/api/embeddings/embed-document/{vault_id}`
3. System:
   - Extracts text from file
   - Chunks the text
   - Generates embeddings using Nomic (768 dimensions, normalized)
   - Adds to FAISS index
   - Stores metadata in pickle file

### 2. Query Flow

1. User sends message → `/api/chat/message`
2. System:
   - Classifies query (greeting, file list, RAG-needed)
   - Rewrites question (optional, for clarity)
   - Embeds query using Nomic
   - Searches FAISS index (filtered by user_id, optionally vault_id)
   - Retrieves top-k chunks
   - Builds context
   - Generates answer using OpenAI

### 3. Multi-User Isolation

- All chunks include `user_id` in metadata
- FAISS search filters results by `user_id` before returning
- Users can only see their own documents

## API Compatibility

✅ **No breaking changes** - All existing API endpoints work the same:

- `POST /api/embeddings/embed-document/{vault_id}` - Same interface
- `POST /api/chat/message` - Same request/response format
- `GET /api/vault/list` - Same interface

## Benefits

1. **No External Dependencies**: No need for pgvector extension or Supabase vector search
2. **Faster**: Local FAISS index is very fast for similarity search
3. **Simpler**: No database schema changes needed
4. **Portable**: Index files can be backed up/restored easily
5. **Cost**: No additional database costs for vector operations

## Limitations (MVP)

1. **Index Rebuild**: When deleting chunks, the index isn't fully rebuilt (orphaned vectors remain but aren't returned)
2. **Single Server**: FAISS index is local to one server (not distributed)
3. **Backup**: Need to backup `faiss_storage/` directory manually

## Future Improvements

1. **Proper Index Rebuild**: Store embeddings separately to enable proper deletion
2. **Distributed FAISS**: Use FAISS with sharding for multi-server deployments
3. **Incremental Updates**: Better handling of chunk updates
4. **Backup Automation**: Automatic backup of FAISS index

## Migration from Supabase

If you have existing chunks in Supabase:

1. **Re-embed all documents** after migration:
   ```bash
   # For each vault_id, call:
   POST /api/embeddings/embed-document/{vault_id}
   ```

2. **Old Supabase chunks** can be left in database (they won't be used)

3. **Clean up** (optional):
   ```sql
   -- In Supabase SQL Editor
   DELETE FROM document_chunks;
   ```

## Troubleshooting

### Index Not Found

If you see errors about missing index:
- The index is created automatically on first use
- Check `faiss_storage/` directory exists and is writable

### Embeddings Mismatch

If embeddings dimension errors occur:
- Ensure Nomic model is used (768 dimensions)
- Check `LOCAL_EMBEDDING_MODEL=nomic-ai/nomic-embed-text-v1` in `.env`

### Slow Performance

- FAISS IndexFlatIP is fast for < 1M vectors
- For larger datasets, consider IndexIVFFlat or IndexHNSW

## Testing

Test the FAISS implementation:

1. **Upload a document:**
   ```bash
   POST /api/vault/upload
   ```

2. **Embed the document:**
   ```bash
   POST /api/embeddings/embed-document/{vault_id}
   ```

3. **Query the document:**
   ```bash
   POST /api/chat/message
   {
     "message": "What is in this document?",
     "user_id": "your-user-id",
     "conversation_id": "test-conv"
   }
   ```

4. **Check FAISS stats:**
   ```python
   from app.services.faiss_store import get_stats
   print(get_stats())
   ```

