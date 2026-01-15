# 🔧 Fix: ERR_CONNECTION_REFUSED Error

## 🚨 The Problem

Your frontend is getting:
- `ERR_CONNECTION_REFUSED`
- `Failed to fetch`

This means the frontend can't reach the backend.

## ✅ Solution Steps

### Step 1: Verify Backend URL

From your image, your backend URL is:
```
https://founderai-workspace-backend-dc090ufif.vercel.app
```

**Test it directly:**
1. Open in browser: `https://founderai-workspace-backend-dc090ufif.vercel.app/health`
2. Should return: `{"status":"healthy"}`
3. If it works: ✅ Backend is running
4. If it doesn't: Check backend deployment logs

### Step 2: Check Frontend Environment Variable

1. **Go to Vercel Dashboard:**
   - Open your **frontend project**
   - Go to **Settings** → **Environment Variables**

2. **Verify `VITE_RAG_API_URL`:**
   - Should be: `https://founderai-workspace-backend-dc090ufif.vercel.app`
   - **No trailing slash** (no `/` at the end)
   - Must include `https://`
   - Set for: **Production**, **Preview**, **Development**

3. **If missing or wrong:**
   - Add/Update: `VITE_RAG_API_URL`
   - Value: `https://founderai-workspace-backend-dc090ufif.vercel.app`
   - Set for all environments
   - Click **Save**

### Step 3: Redeploy Frontend (CRITICAL!)

**After updating environment variable, you MUST redeploy:**

1. **Go to Deployments tab**
2. **Click "Redeploy"** on latest deployment
3. **Or push a commit:**
   ```powershell
   git commit --allow-empty -m "Redeploy frontend with backend URL"
   git push origin merwin
   ```

**Important:** Environment variables are only available at build time. You must redeploy for changes to take effect!

### Step 4: Clear Browser Cache

After redeploy:
1. **Hard refresh:** `Ctrl + Shift + R` (Windows) or `Cmd + Shift + R` (Mac)
2. **Or clear cache:** DevTools → Application → Clear Storage

### Step 5: Verify in Browser

1. **Open DevTools (F12)**
2. **Go to Console tab**
3. **Check what URL it's trying:**
   - Look for fetch requests
   - Should see: `https://founderai-workspace-backend-dc090ufif.vercel.app/api/chat/message`
   - If you see `http://127.0.0.1:8000`: ❌ Environment variable not set/loaded

## 🎯 Quick Checklist

- [ ] Backend health check works: `/health` endpoint
- [ ] `VITE_RAG_API_URL` is set in frontend project
- [ ] Value is: `https://founderai-workspace-backend-dc090ufif.vercel.app`
- [ ] Set for Production, Preview, Development
- [ ] **Redeployed frontend** (CRITICAL!)
- [ ] Cleared browser cache
- [ ] Tested - works! ✅

## ⚠️ Common Issues

### Issue 1: Still seeing `127.0.0.1:8000`

**Cause:** Environment variable not loaded or frontend not redeployed.

**Fix:**
1. Verify `VITE_RAG_API_URL` in Vercel
2. **Redeploy frontend** (most important!)
3. Clear browser cache

### Issue 2: CORS Error

**Cause:** Backend CORS not configured correctly.

**Fix:** Backend should already have CORS configured. If not, check `rag-backend/app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue 3: 404 Not Found

**Cause:** Backend routes not working.

**Fix:**
1. Test backend directly: `/health` should work
2. Check backend deployment logs
3. Verify `api/index.py` is correct

### Issue 4: Environment Variable Not Found

**Cause:** Variable name wrong or not set for correct environment.

**Fix:**
- Must be exactly: `VITE_RAG_API_URL` (case-sensitive)
- Must be set for **Production** environment
- Must redeploy after adding

## 🔍 Debug Steps

1. **Check what URL frontend is using:**
   - Open browser DevTools (F12)
   - Go to Network tab
   - Try sending a message
   - Look at the failed request URL
   - Should be: `https://founderai-workspace-backend-dc090ufif.vercel.app/api/chat/message`

2. **Check backend logs:**
   - Go to backend project → Deployments
   - Click on latest deployment
   - Check Function Logs
   - Look for incoming requests

3. **Test backend directly:**
   ```bash
   curl https://founderai-workspace-backend-dc090ufif.vercel.app/health
   ```
   Should return: `{"status":"healthy"}`

## 📝 Your Backend URL

Based on your image:
```
https://founderai-workspace-backend-dc090ufif.vercel.app
```

**Set this in frontend:**
```
VITE_RAG_API_URL = https://founderai-workspace-backend-dc090ufif.vercel.app
```

---

**Most likely fix: Redeploy the frontend after setting the environment variable!**
