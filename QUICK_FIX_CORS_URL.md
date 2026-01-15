# ⚡ Quick Fix: CORS Error + Wrong URL

## 🚨 The Problems

1. **Wrong Backend URL:** Using Vercel dashboard URL instead of deployment URL
2. **CORS Error:** `content-type` header not allowed

## ✅ Quick Fix (2 Steps)

### Step 1: Push CORS Fix (Backend)

I've fixed the CORS configuration. Push it:

```powershell
git push origin merwin
```

This will redeploy the backend with fixed CORS.

### Step 2: Fix Frontend Backend URL

1. **Get Your Backend URL:**
   - Go to Vercel → Backend project → **Settings** → **Domains**
   - Copy the production domain
   - **OR** Go to **Deployments** → Click latest → Copy URL
   - Should be like: `https://founderai-workspace-backend-dc090ufif.vercel.app`

2. **Update Frontend:**
   - Frontend project → **Settings** → **Environment Variables**
   - Find `VITE_RAG_API_URL`
   - **Delete current value** (it's wrong!)
   - Set to: `https://your-actual-backend-domain.vercel.app`
   - **NOT** `https://vercel.com/...` (that's wrong!)
   - Set for: Production, Preview, Development
   - Click **Save**

3. **Redeploy Frontend:**
   - **Deployments** tab → **Redeploy**

## 🎯 URL Examples

**❌ Wrong:**
```
https://vercel.com/atman-artwork-llps-projects/founderai-workspace-backend/4v2ise6ocu7VAAZHgRfmmyT
```

**✅ Correct:**
```
https://founderai-workspace-backend-dc090ufif.vercel.app
```

## 🔍 How to Find Your Backend URL

**Easiest way:**
1. Backend project → **Deployments**
2. Click latest deployment
3. Copy URL from browser address bar
4. Should end with `.vercel.app`

**Or test:**
- Try: `https://founderai-workspace-backend-dc090ufif.vercel.app/health`
- If it returns `{"status":"healthy"}`, that's your URL!

---

**Do both: Push CORS fix + Fix frontend URL!**
