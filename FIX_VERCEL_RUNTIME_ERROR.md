# 🔧 Fix: "Function Runtimes must have a valid version" Error

## 🚨 The Problem

Vercel was showing this error:
```
Error: Function Runtimes must have a valid version, for example `now-php@1.0.0`.
```

This happened because the `vercel.json` had an invalid Python runtime specification.

## ✅ The Fix

I've fixed it by:

1. **Removed invalid runtime from `vercel.json`:**
   - Removed the `functions` section with `"runtime": "python3.9"`
   - Vercel auto-detects Python from the file structure

2. **Added `runtime.txt`:**
   - Created `rag-backend/runtime.txt` with `python-3.12`
   - This tells Vercel which Python version to use

3. **Updated build command:**
   - Changed to use `api/requirements.txt` for dependencies

## 📋 What Changed

**Before (❌ Error):**
```json
{
  "functions": {
    "api/**/*.py": {
      "runtime": "python3.9"  // ❌ Invalid format
    }
  }
}
```

**After (✅ Fixed):**
```json
{
  "buildCommand": "pip install -r api/requirements.txt",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/api/index.py"
    }
  ]
}
```

Plus `runtime.txt`:
```
python-3.12
```

## ✅ Next Steps

1. **Push the fix:**
   ```powershell
   git push origin merwin
   ```

2. **Redeploy in Vercel:**
   - Go to your backend project
   - Click **"Redeploy"** on the failed deployment
   - Or push will trigger automatic redeploy

3. **Should work now!** ✅

## 🎯 Why This Works

- Vercel auto-detects Python functions from `.py` files in `api/` directory
- `runtime.txt` specifies Python version (3.12)
- No need to specify runtime in `vercel.json` for Python
- Vercel handles Python serverless functions automatically

---

**Push the fix and redeploy!**
