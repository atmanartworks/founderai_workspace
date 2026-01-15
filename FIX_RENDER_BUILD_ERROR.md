# 🔧 Fix Render Build Error

## 🚨 The Problem

Render couldn't find `rag-backend/requirements.txt` because:
- Root directory wasn't set correctly
- Build command path was wrong

## ✅ The Fix

I've updated `render.yaml` to:
1. **Set `rootDir: rag-backend`** - Tells Render where the code is
2. **Use `requirements-railway.txt`** - Lighter requirements (no sentence-transformers, avoids memory issues)
3. **Fixed start command** - No need for `cd` since rootDir is set
4. **Changed plan to `starter`** - Better than free tier (but you can change to `free` if you want)

## ✅ Next Steps

### Step 1: Push the Fix

```powershell
git push origin merwin
```

### Step 2: Redeploy on Render

1. **Go to Render Dashboard**
2. **Your service** → **Manual Deploy** tab
3. **Click "Clear build cache & deploy"**
4. **Wait for deployment** (3-5 minutes)

**OR** Render will auto-deploy when you push!

### Step 3: Verify

After deployment:
- Check build logs - should see requirements installing
- Check service status - should be "Live"
- Test health endpoint: `https://your-service.onrender.com/health`

## 🎯 What Changed

**Before:**
```yaml
buildCommand: pip install -r rag-backend/requirements.txt
startCommand: cd rag-backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**After:**
```yaml
rootDir: rag-backend
buildCommand: pip install -r requirements-railway.txt
startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## 📋 Quick Checklist

- [ ] Pushed the fix
- [ ] Render redeployed (or auto-deployed)
- [ ] Build successful
- [ ] Service is Live
- [ ] Health check works
- [ ] Ready to connect frontend! ✅

---

**Push the fix and Render will redeploy automatically!**
