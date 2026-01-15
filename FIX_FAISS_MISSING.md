# 🔧 Fix: Missing faiss Module

## 🚨 The Problem

Error: `ModuleNotFoundError: No module named 'faiss'`

The code imports `faiss` for vector search but it's not in `requirements-railway.txt`!

## ✅ The Fix

I've added `faiss-cpu>=1.7.4` to `requirements-railway.txt`.

**Why `faiss-cpu`?**
- Required for vector search functionality
- Lighter than `faiss` (CPU-only, no GPU dependencies)
- Needed for RAG search operations

## ✅ Next Steps

### Step 1: Push the Fix

```powershell
git push origin merwin
```

### Step 2: Redeploy on Render

Render will auto-deploy when you push, OR:

1. **Render Dashboard** → Your service
2. **Manual Deploy** tab
3. **Clear build cache & deploy**
4. Wait for deployment (faiss-cpu may take a few minutes to install)

### Step 3: Verify

After deployment:
- Check build logs - should see `faiss-cpu` installing
- Check service status - should be "Live"
- Test: `https://your-service.onrender.com/health`

## 🎯 What Changed

**Added to `requirements-railway.txt`:**
```
faiss-cpu>=1.7.4
```

This is needed because:
- `app/services/faiss_store.py` imports `faiss`
- `app/routes/embeddings.py` uses FAISS for storing embeddings
- `app/routes/chat.py` uses FAISS for vector search
- `app/routes/vault.py` uses FAISS for deleting chunks

## ⚠️ Note

- `faiss-cpu` is lighter than `sentence-transformers` (which we excluded)
- It's required for the RAG vector search to work
- Installation may take 2-3 minutes during build

## 📋 Quick Checklist

- [ ] Pushed the fix
- [ ] Render redeployed (or auto-deployed)
- [ ] Build successful
- [ ] faiss-cpu installed
- [ ] App starts successfully
- [ ] Health check works! ✅

---

**Push the fix and Render will redeploy automatically!**
