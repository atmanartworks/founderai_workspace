# 🔧 Fix: Failed to Generate Query Embedding

## 🚨 The Problem

Error: `(500, 'Failed to generate query embedding')`

**Root Cause:** `sentence-transformers` is not installed (we excluded it to save memory), so `embed_text()` was returning an empty list `[]`, causing the embedding to fail.

## ✅ The Fix

I've updated the embedding service to:
1. **Use OpenAI embeddings as fallback** when `sentence-transformers` is not available
2. **Support both embedding dimensions:**
   - 768 dimensions (nomic models)
   - 1536 dimensions (OpenAI embeddings)
3. **Auto-detect dimension** based on the embedding model used

## ✅ Next Steps

### Step 1: Verify OpenAI API Key in Render

Make sure `OPENAI_API_KEY` is set in Render:

1. **Render Dashboard** → Your service → **Environment**
2. Verify `OPENAI_API_KEY` exists and is correct
3. If missing, add it

### Step 2: Push the Fix

```powershell
git push origin merwin
```

### Step 3: Redeploy

Render will auto-deploy when you push, OR:

1. **Render Dashboard** → Your service
2. **Manual Deploy** tab
3. **Clear build cache & deploy**

### Step 4: Test

After redeploy:
- Send a message in the frontend
- Should work! ✅
- Embeddings will use OpenAI API (requires API key)

## 🎯 What Changed

**Updated `app/services/embedding_service.py`:**
- `embed_text()` now falls back to OpenAI embeddings if `sentence-transformers` is not available
- `embed_batch()` also falls back to OpenAI embeddings
- Both methods normalize embeddings for cosine similarity

**Updated `app/services/faiss_store.py`:**
- Made embedding dimension configurable (768 for nomic, 1536 for OpenAI)
- Auto-detects dimension based on model type

## ⚠️ Important Notes

- **OpenAI embeddings cost money** (very cheap, ~$0.0001 per 1K tokens)
- **Dimension mismatch:** If you have existing FAISS indices with 768-dim embeddings, they won't work with new 1536-dim OpenAI embeddings
- **Solution:** For new deployments, this works fine. For existing indices, you'd need to re-embed all documents with OpenAI

## 📋 Quick Checklist

- [ ] Verified `OPENAI_API_KEY` in Render
- [ ] Pushed the fix
- [ ] Render redeployed
- [ ] Tested - embeddings work! ✅

---

**The fix is committed. Push and redeploy!**
