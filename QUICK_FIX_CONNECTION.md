# ⚡ Quick Fix: ERR_CONNECTION_REFUSED

## 🚨 The Problem

Frontend is trying to connect to `http://127.0.0.1:8000` (local) instead of your Vercel backend.

## ✅ Quick Fix (3 Steps)

### Step 1: Add Environment Variable in Vercel

1. **Go to Vercel Dashboard:**
   - Open your **frontend project** (not backend)
   - Go to **Settings** → **Environment Variables**

2. **Add Variable:**
   - Click **"Add New"**
   - **Key:** `VITE_RAG_API_URL`
   - **Value:** `https://founderai-workspace-backend-dc090ufif.vercel.app`
   - **Important:** Use your exact backend URL (from the image)
   - Check ✅ **Production**
   - Check ✅ **Preview**
   - Check ✅ **Development**
   - Click **Save**

### Step 2: Redeploy Frontend (MUST DO THIS!)

**CRITICAL:** Environment variables are only available at build time!

1. **Go to Deployments tab**
2. **Click "Redeploy"** on the latest deployment
3. **Wait for deployment** to complete (~1-2 minutes)

**OR** push a commit:
```powershell
git commit --allow-empty -m "Redeploy with backend URL"
git push origin merwin
```

### Step 3: Test

1. **Visit your frontend site**
2. **Hard refresh:** `Ctrl + Shift + R`
3. **Try sending a message**
4. **Should work!** ✅

## 🎯 Your Backend URL

From your image:
```
https://founderai-workspace-backend-dc090ufif.vercel.app
```

**Set this exactly in `VITE_RAG_API_URL`**

## ⚠️ Why This Happens

Vite environment variables (`VITE_*`) are **build-time only**. If you:
- Set the variable but don't redeploy → Still uses old build
- Don't set the variable → Uses default `http://127.0.0.1:8000`

**Solution:** Set variable + Redeploy = Fixed! ✅

---

**Do Step 1 and Step 2 now - that's all you need!**
