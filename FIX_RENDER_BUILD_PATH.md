# 🔧 Fix Render Build Path Issue

## 🚨 The Problem

Render is running the build command from the **repo root**, not from the `rag-backend` directory, even though `rootDir` is set. The build command can't find `requirements-railway.txt`.

## ✅ The Fix

I've updated the build command to explicitly `cd` into the directory first:

**Before:**
```yaml
buildCommand: pip install -r requirements-railway.txt
```

**After:**
```yaml
buildCommand: cd rag-backend && pip install -r requirements-railway.txt
```

## ✅ Next Steps

### Step 1: Push the Fix

```powershell
git push origin merwin
```

### Step 2: Update Render Settings (If Not Auto-Updated)

**Option A: Let Render Auto-Update**
- Render should detect the new commit
- Auto-deploy with new settings

**Option B: Update Manually**
1. **Render Dashboard** → Your service → **Settings**
2. **Build Command:** `cd rag-backend && pip install -r requirements-railway.txt`
3. **Root Directory:** `rag-backend` (should already be set)
4. **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. **Save Changes**
6. **Manual Deploy** → **Clear build cache & deploy**

### Step 3: Wait for Deployment

- Build should now succeed
- Usually takes 3-5 minutes

## 🎯 Why This Works

- **`cd rag-backend`** - Changes into the correct directory first
- **`&&`** - Runs the next command only if cd succeeds
- **`pip install -r requirements-railway.txt`** - Now finds the file in the correct location

## 📋 Quick Checklist

- [ ] Pushed the fix
- [ ] Render settings updated (or auto-updated)
- [ ] Build command: `cd rag-backend && pip install -r requirements-railway.txt`
- [ ] Root Directory: `rag-backend`
- [ ] Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- [ ] Build successful
- [ ] Service is Live! ✅

---

**Push the fix and Render should build successfully now!**
