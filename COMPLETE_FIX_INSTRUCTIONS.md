# ✅ Complete Fix Instructions - Do This Now!

Your frontend shows "Failed to fetch" because it's trying to connect to localhost. Here's the complete fix:

## 🎯 The Problem

- Frontend deployed: ✅
- Backend not connected: ❌
- Frontend trying: `http://127.0.0.1:8000` (local - won't work!)

## ✅ Complete Solution

### Part 1: Add Environment Variables in Vercel (MUST DO THIS!)

1. **Go to Vercel Dashboard:**
   - https://vercel.com/dashboard
   - Open your project

2. **Settings → Environment Variables**

3. **Add ALL These Variables:**

   **Backend Variables (for serverless functions):**
   ```
   SUPABASE_URL = your_supabase_url
   SUPABASE_KEY = your_supabase_anon_key
   SUPABASE_SERVICE_ROLE_KEY = your_service_role_key
   OPENAI_API_KEY = your_openai_key
   ```

   **Frontend Variable (CRITICAL!):**
   ```
   VITE_RAG_API_URL = https://founderai-workspace-ow964rq32-atman-artwork-llps-projects.vercel.app/api
   ```
   
   **Important:** Use your actual Vercel project URL!

4. **For Each Variable:**
   - Check ✅ Production
   - Check ✅ Preview  
   - Check ✅ Development
   - Click **Save**

### Part 2: Push Backend Code

The backend files are ready. Push them:

```powershell
git push origin merwin
```

This will:
- Push `api/` directory (backend serverless functions)
- Push updated `vercel.json` (Python runtime config)
- Trigger Vercel to deploy backend automatically

### Part 3: Wait for Deployment

1. **Go to Vercel → Deployments tab**
2. **Watch for new deployment:**
   - Frontend builds
   - Backend Python functions build
   - Both deploy

3. **Check build logs:**
   - Look for Python function deployment
   - Should see "api/index.py" being processed

### Part 4: Redeploy Frontend (After Backend is Live)

1. **Go to Deployments tab**
2. **Click "Redeploy"** on latest deployment
3. **This ensures frontend has the new `VITE_RAG_API_URL`**

### Part 5: Test

1. **Visit your site**
2. **Try sending a message**
3. **Should connect to backend!** ✅

## 📋 Quick Action Items

**In Vercel Dashboard (Do This First):**
- [ ] Add `SUPABASE_URL`
- [ ] Add `SUPABASE_KEY`
- [ ] Add `SUPABASE_SERVICE_ROLE_KEY`
- [ ] Add `OPENAI_API_KEY`
- [ ] Add `VITE_RAG_API_URL` = `https://your-project.vercel.app/api`
- [ ] All set for Production, Preview, Development

**Then Push Code:**
- [ ] `git push origin merwin`
- [ ] Wait for Vercel deployment
- [ ] Redeploy frontend
- [ ] Test!

## 🎯 Your Vercel URL

From your error, your project URL is:
`https://founderai-workspace-ow964rq32-atman-artwork-llps-projects.vercel.app`

So set:
`VITE_RAG_API_URL` = `https://founderai-workspace-ow964rq32-atman-artwork-llps-projects.vercel.app/api`

---

**Start with Part 1 (add env vars in Vercel), then push the code!**
