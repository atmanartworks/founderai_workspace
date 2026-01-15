# 🔧 Fix: CORS Error + Wrong Backend URL

## 🚨 Two Problems

1. **Wrong Backend URL:** 
   - Currently: `https://vercel.com/atman-artwork-llps-projects/founderai-workspace-backend/...`
   - Should be: `https://founderai-workspace-backend-dc090ufif.vercel.app` (or your actual backend domain)

2. **CORS Error:**
   - "Request header field content-type is not allowed"
   - Backend CORS needs to be more explicit

## ✅ Fix 1: Update Backend CORS (Code Fix)

I've updated the CORS configuration in `rag-backend/app/main.py` to be more explicit. Now push this fix:

```powershell
git add rag-backend/app/main.py
git commit -m "Fix CORS configuration for Vercel"
git push origin merwin
```

This will trigger a backend redeploy with the fixed CORS.

## ✅ Fix 2: Fix Frontend Backend URL

The frontend is using the wrong backend URL. Fix it:

### Step 1: Get Correct Backend URL

1. **Go to Vercel Dashboard:**
   - Open your **backend project**
   - Go to **Settings** → **Domains**
   - Copy the **production domain** (e.g., `founderai-workspace-backend-dc090ufif.vercel.app`)

   **OR**

   - Go to **Deployments** tab
   - Click on latest deployment
   - Copy the URL from the address bar

### Step 2: Update Frontend Environment Variable

1. **Go to Frontend Project:**
   - Open your **frontend project** in Vercel
   - Go to **Settings** → **Environment Variables**

2. **Update `VITE_RAG_API_URL`:**
   - Find `VITE_RAG_API_URL`
   - **Delete the current value** (it's wrong)
   - Set to: `https://founderai-workspace-backend-dc090ufif.vercel.app`
   - **Use your actual backend domain** (not the vercel.com URL!)
   - Set for: Production, Preview, Development
   - Click **Save**

### Step 3: Redeploy Both

1. **Backend:** Will auto-redeploy after you push the CORS fix
2. **Frontend:** 
   - Go to **Deployments** tab
   - Click **"Redeploy"** on latest deployment
   - Wait for completion

## 🎯 Correct URL Format

**Wrong (❌):**
```
https://vercel.com/atman-artwork-llps-projects/founderai-workspace-backend/4v2ise6ocu7VAAZHgRfmmyT
```

**Correct (✅):**
```
https://founderai-workspace-backend-dc090ufif.vercel.app
```

**Or your custom domain:**
```
https://api.yourdomain.com
```

## 📋 Quick Checklist

- [ ] Pushed CORS fix to backend
- [ ] Backend redeployed
- [ ] Got correct backend URL from Vercel
- [ ] Updated `VITE_RAG_API_URL` in frontend
- [ ] Set correct URL (not vercel.com URL!)
- [ ] Redeployed frontend
- [ ] Tested - works! ✅

## ⚠️ How to Find Your Backend URL

**Method 1: From Deployments**
1. Backend project → Deployments
2. Click latest deployment
3. Copy URL from browser address bar

**Method 2: From Settings**
1. Backend project → Settings → Domains
2. Copy the production domain

**Method 3: Test Health Endpoint**
Try these URLs in browser:
- `https://founderai-workspace-backend-dc090ufif.vercel.app/health`
- `https://founderai-workspace-backend.vercel.app/health`
- `https://founderai-workspace-backend-[random].vercel.app/health`

Whichever returns `{"status":"healthy"}` is your correct URL!

---

**Do both fixes: Push CORS fix + Update frontend URL!**
