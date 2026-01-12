# Vector Database Access - How RAG Searches Your Files

## Overview

When you ask questions about your files, the system searches the **vector database** (embeddings) to find relevant information. This document explains how it works.

## How It Works

### 1. File Upload & Embedding

```
Upload File → Extract Text → Chunk Text → Generate Embeddings → Store in Vector DB
```

**Vector Database:** `document_chunks` table in Supabase
- Contains: text chunks with their vector embeddings
- Indexed: Using pgvector for fast similarity search
- Dimension: 768 (Nomic embedding model)

### 2. Question Processing

```
User Question → Embed Question → Vector Search → Retrieve Chunks → Generate Answer
```

**Vector Search:** Uses cosine similarity to find most relevant chunks

## File Listing Enhancement

### What You See Now

When you ask "what files do you have", you'll see:

```
I have access to 3 file(s) in your vault:

• document-1.pdf (2.5 MB, PDF)
  ✅ Embedded (45 chunks)

• log 1.txt (150 KB, TXT)
  ✅ Embedded (12 chunks)

• document-3.pdf (1.2 MB, PDF)
  ⚠️ Not embedded (needs embedding to answer questions)

Summary:
- 2 file(s) embedded in vector database (57 total chunks)
- 1 file(s) need embedding

Note: Only embedded files can be searched and queried. Upload files and embed them to enable question-answering!
```

### Embedding Status

- ✅ **Embedded**: File has chunks in vector database - can answer questions
- ⚠️ **Not embedded**: File uploaded but not embedded - cannot answer questions yet
- ❓ **Status unknown**: Error checking status

## Vector Database Search

### When Questions Are Asked

1. **Question is embedded** using Nomic model (768 dimensions)
2. **Vector search** finds similar chunks using cosine similarity
3. **Chunks retrieved** from `document_chunks` table
4. **Context built** from relevant chunks
5. **LLM generates answer** using context + general knowledge

### Search Process

```python
# 1. Embed user question
query_embedding = embed_text("What is RAG?")

# 2. Search vector database
chunks = search_embeddings(
    query_embedding=query_embedding,
    user_id=user_id,
    match_count=5
)

# 3. Retrieve relevant chunks
# Returns chunks with highest cosine similarity
```

### Vector Search Function

The `search_embeddings` RPC function:
- Searches `document_chunks` table
- Filters by `user_id` (security)
- Uses pgvector cosine similarity
- Returns top K most similar chunks

## Ensuring Vector Database Access

### Current Implementation

✅ **Vector search is active** when:
- Question is asked (not greeting/conversational)
- Files are embedded
- `query_classification["needs_rag"]` is True

✅ **Vector database is accessed via:**
- Supabase RPC function `search_embeddings`
- Filters by `user_id` for security
- Returns chunks sorted by similarity

### Logging

The system now logs:
- When vector search is performed
- How many chunks were found
- Which files the chunks came from
- Warnings if no chunks found (file not embedded)

### Example Logs

```
INFO: Searching vector database for user_id: user123, top_k: 5
INFO: Vector search returned 5 chunks from vector database
INFO: Found chunks from files: ['document-1.pdf', 'log 1.txt']
```

## File Types Supported

The system can embed and search:
- ✅ **PDF** (.pdf)
- ✅ **Word** (.docx)
- ✅ **Text** (.txt)
- ✅ **Markdown** (.md)
- ✅ **HTML** (.html, .htm)
- ✅ **JSON** (.json)

## Embedding Process

To make files searchable:

1. **Upload file** via `/api/vault/upload`
2. **Embed file** via `/api/embeddings/embed-document/{vault_id}`
3. **File is now searchable** in vector database

### What Happens During Embedding

```
1. Extract text from file
2. Clean text (remove null bytes, etc.)
3. Chunk text (1000 chars per chunk, 200 overlap)
4. Generate embeddings for each chunk (768 dimensions)
5. Store chunks + embeddings in document_chunks table
6. Create vector index for fast search
```

## Troubleshooting

### No Chunks Found

**Problem:** "No chunks found in vector database"

**Causes:**
- File not embedded yet
- Embedding failed
- Wrong user_id filter

**Solution:**
1. Check file list - see if file shows "Not embedded"
2. Embed the file: `POST /api/embeddings/embed-document/{vault_id}`
3. Verify chunks exist: Check `document_chunks` table

### Vector Search Not Working

**Problem:** Questions return no results

**Check:**
1. Are files embedded? (Check file list)
2. Are chunks in database? (Query `document_chunks`)
3. Is vector index created? (Check Supabase)
4. Are embeddings correct dimension? (Should be 768)

### Performance

**Vector search is fast:**
- Uses pgvector IVFFlat index
- Cosine similarity search
- Typically < 100ms for search

## Best Practices

1. **Embed files after upload** - Makes them immediately searchable
2. **Check embedding status** - Use file list to see status
3. **Re-embed if needed** - If you change embedding model
4. **Monitor logs** - See what files are being searched

## Summary

✅ **Vector database access is working:**
- Files are embedded into vector database
- Questions trigger vector search
- Relevant chunks are retrieved
- LLM uses chunks for answers

✅ **File listing shows:**
- Which files are embedded
- How many chunks each file has
- Which files need embedding

✅ **System ensures:**
- Only user's files are searched
- Vector search is fast and accurate
- Logging shows what's happening

