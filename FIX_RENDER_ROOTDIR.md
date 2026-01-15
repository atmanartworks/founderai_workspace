# 🔧 Fix Render rootDir Issue

## 🚨 The Problem

Render is using `rootDir: rag-backend`, which means it **already changes into that directory** before running the build command. So when we do `cd rag-backend`, it tries to go into `rag-backend/rag-backend` which doesn't exist!

## ✅ The Fix

Since `rootDir` is set, the build command runs **from within** the `rag-backend` directory. So we don't need `cd`:

**Before:**
```yaml
rootDir: rag-backend
buildCommand: cd rag-backend && pip install -r requirements-railway.txt
```

**After:**
```yaml
rootDir: rag-backend
buildCommand: pip install -r requirements-railway.txt
```

## ✅ Next Steps

### Step 1: Push the Fix

```powershell
git push origin merwin
```

### Step 2: Update Render Settings

1. **Render Dashboard** → Your service → **Settings**
2. **Build Command:** `pip install -r requirements-railway.txt`
3. **Root Directory:** `rag-backend` (should already be set)
4. **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. **Save Changes**

### Step 3: Redeploy

1. **Manual Deploy** tab
2. **Clear build cache & deploy**
3. Wait for deployment

## 🎯 How rootDir Works

- **`rootDir: rag-backend`** tells Render to change into that directory first
- Build command runs **from within** `rag-backend/`
- So `requirements-railway.txt` is in the current directory
- No need for `cd`!

## 📋 Quick Checklist

- [ ] Pushed the fix
- [ ] Updated Render settings
- [ ] Build Command: `pip install -r requirements-railway.txt` (no cd!)
- [ ] Root Directory: `rag-backend`
- [ ] Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- [ ] Cleared cache & redeployed
- [ ] Build successful! ✅

---

**Push the fix and update Render settings - should work now!**
