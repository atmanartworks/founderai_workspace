# 🔧 Fix: FAISS Dimension Mismatch

## 🚨 The Problem

Error: `Failed adding chunks to FAISS`

**Root Cause:** Dimension mismatch between FAISS index and embeddings:
- FAISS index was created with **768 dimensions** (for nomic embeddings)
- OpenAI embeddings are **1536 dimensions**
- When trying to add 1536-dim embeddings to a 768-dim index, FAISS fails

## ✅ The Fix

I've updated FAISS to:
1. **Auto-detect embedding dimension** from the actual embeddings array
2. **Check if index dimension matches** embedding dimension
3. **Automatically recreate index** with correct dimension if mismatch detected
4. **Remove old index files** to start fresh

## ✅ Next Steps

### Step 1: Push the Fix

```powershell
git push origin merwin
```

### Step 2: Redeploy

Render will auto-deploy when you push, OR:

1. **Render Dashboard** → Your service
2. **Manual Deploy** tab
3. **Clear build cache & deploy**

### Step 3: Re-upload Documents

After redeploy:
1. **Delete old documents** from vault (if any)
2. **Re-upload documents** - they will be embedded with correct dimension
3. **Test** - should work now! ✅

## 🎯 What Changed

**Updated `app/services/faiss_store.py`:**
- `add_chunks()` now detects embedding dimension from actual embeddings
- Checks if index dimension matches
- Automatically recreates index with correct dimension if mismatch
- Removes old index files to prevent confusion

## ⚠️ Important Notes

- **Existing indices will be recreated** if dimension mismatch is detected
- **Old chunks will be lost** - you'll need to re-embed documents
- **This is expected** - can't mix 768-dim and 1536-dim embeddings in same index

## 📋 Quick Checklist

- [ ] Pushed the fix
- [ ] Render redeployed
- [ ] Re-uploaded documents
- [ ] Documents embedded successfully
- [ ] Tested - works! ✅

---

**The fix is committed. Push and redeploy, then re-upload your documents!**
