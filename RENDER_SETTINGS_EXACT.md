# 📋 Exact Render Settings to Use

Copy these exact settings into your Render service:

## ✅ Service Settings

**Name:** `rag-backend`

**Region:** Choose closest to you

**Branch:** `merwin` (or your branch name)

**Root Directory:** `rag-backend`

**Environment:** `Python 3`

**Build Command:**
```
pip install -r requirements-railway.txt
```

**Start Command:**
```
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**Python Version:** `3.12.0` (or leave default)

**Plan:** `Starter` ($7/month) or `Free` (for testing)

## ✅ Environment Variables

Add these in **Environment** section:

```
SUPABASE_URL = your_supabase_url
SUPABASE_KEY = your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY = your_service_role_key
OPENAI_API_KEY = your_openai_key
PYTHON_VERSION = 3.12.0
PORT = 10000
```

## ✅ Health Check

**Health Check Path:** `/health`

## 🎯 Where to Find These Settings

1. **Render Dashboard** → Your service
2. **Settings** tab
3. Scroll to **Build & Deploy**
4. Update the fields above
5. **Save Changes**

---

**Copy these exact settings into Render!**
