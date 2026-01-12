# Embedding Model Configuration

## Using Nomic Embedding Model (Free & High Quality)

The RAG backend now uses **Nomic Embed** by default, which is:
- ✅ **Free** - No API costs
- ✅ **High Quality** - 768 dimensions (better than MiniLM's 384)
- ✅ **Open Source** - Available via sentence-transformers
- ✅ **Fast** - Runs locally on your machine

## Model Information

**Model Name:** `nomic-embed-text-v1`
- **Dimensions:** 768
- **Size:** ~137 MB (downloads automatically on first use)
- **Provider:** Nomic AI
- **License:** Apache 2.0 (free for commercial use)

## Configuration

### Option 1: Environment Variable (Recommended)

Add to your `.env` file:

```env
LOCAL_EMBEDDING_MODEL=nomic-embed-text-v1
```

### Option 2: Default (Already Set)

The code now defaults to Nomic, so you don't need to set anything if you want to use it.

## Alternative Models

You can switch to other models by changing `LOCAL_EMBEDDING_MODEL`:

### Nomic Models (Recommended)
- `nomic-embed-text-v1` - 768 dims, best quality (default)
- `nomic-embed-text-v1.5` - Latest version with improvements

### Other Free Models
- `all-MiniLM-L6-v2` - 384 dims, smaller and faster
- `all-mpnet-base-v2` - 768 dims, high quality
- `paraphrase-multilingual-MiniLM-L12-v2` - 384 dims, multilingual

## First Run

On first use, the model will automatically download from Hugging Face:
- Model files are cached in `~/.cache/huggingface/`
- Download size: ~137 MB
- Subsequent runs are instant (uses cached model)

## Performance

**Nomic Embed Text v1:**
- Embedding speed: ~100-200 texts/second (depends on hardware)
- Memory usage: ~500-800 MB
- Quality: Excellent for semantic search and RAG

## Verification

To verify the model is loaded correctly, check the server logs when starting:

```
INFO: Loaded embedding model: nomic-embed-text-v1
INFO: Embedding dimension: 768
```

Or test it:
```python
from app.services.embedding_service import embedding_service
import asyncio

async def test():
    embedding = await embedding_service.embed_text("test")
    print(f"Dimension: {len(embedding)}")  # Should be 768

asyncio.run(test())
```

## Troubleshooting

### Model Download Fails

If the model doesn't download automatically:
1. Check internet connection
2. Try manually: `python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('nomic-embed-text-v1')"`
3. Check Hugging Face access (should be public, no login needed)

### Out of Memory

If you get memory errors:
- Use a smaller model: `all-MiniLM-L6-v2` (384 dims)
- Close other applications
- Consider using a cloud embedding service instead

### Slow Performance

- First run is slower (model download)
- Subsequent runs are faster
- Batch embeddings are more efficient than single embeddings
- Consider GPU acceleration if available

## Database Compatibility

**Important:** If you switch models, you need to re-embed all documents!

Different models have different dimensions:
- Nomic: 768 dimensions
- MiniLM: 384 dimensions

Your Supabase database stores embeddings with a specific dimension. If you change models, you must:
1. Delete old chunks: `DELETE FROM document_chunks;`
2. Re-embed all documents using the new model

## Model Comparison

| Model | Dimensions | Size | Speed | Quality |
|-------|-----------|------|-------|---------|
| nomic-embed-text-v1 | 768 | 137 MB | Fast | ⭐⭐⭐⭐⭐ |
| all-MiniLM-L6-v2 | 384 | 90 MB | Very Fast | ⭐⭐⭐ |
| all-mpnet-base-v2 | 768 | 420 MB | Medium | ⭐⭐⭐⭐⭐ |

**Recommendation:** Use Nomic for best balance of quality and speed!

