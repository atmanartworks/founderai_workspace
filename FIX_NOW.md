# ⚡ Fix "Failed to fetch" Error - Do This Now!

Your frontend is deployed but can't connect to backend. Here's the exact fix:

## 🚨 Current Problem

- ✅ Frontend deployed: `founderai-workspace-ow964rq32-atman-artwork-llps-projects.vercel.app`
- ❌ Trying to connect to: `http://127.0.0.1:8000` (local - doesn't work!)
- ❌ Backend not deployed yet

## ✅ Solution: Deploy Backend to Vercel

### Step 1: Add Environment Variables in Vercel (Do This First!)

1. **Go to Vercel:**
   - Open: https://vercel.com/dashboard
   - Click on your project: `founderai-workspace` (or similar)

2. **Go to Settings → Environment Variables**

3. **Add These Variables:**
   
   **Backend Variables:**
   - `SUPABASE_URL` = (your Supabase URL)
   - `SUPABASE_KEY` = (your Supabase anon key)
   - `SUPABASE_SERVICE_ROLE_KEY` = (your service role key)
   - `OPENAI_API_KEY` = (your OpenAI key)
   
   **Frontend Variable (IMPORTANT!):**
   - `VITE_RAG_API_URL` = `https://founderai-workspace-ow964rq32-atman-artwork-llps-projects.vercel.app/api`
   
   **Note:** Replace with your actual Vercel project URL if different!

4. **Set for:** Production, Preview, Development (check all)
5. **Click Save** for each

### Step 2: Push Backend Code

I've prepared the backend files. Push them:

```powershell
git add .
git commit -m "Add Vercel serverless backend"
git push origin merwin
```

### Step 3: Wait for Deployment

- Vercel will automatically:
  - Detect `api/` directory
  - Build Python serverless functions
  - Deploy backend at `/api/*` routes

### Step 4: Redeploy Frontend

After backend is deployed:

1. **Go to Deployments tab**
2. **Click "Redeploy"** on latest deployment
3. **Wait for completion**

### Step 5: Test!

- Visit your site
- Try sending a message
- Should work! ✅

## 🎯 Quick Checklist

- [ ] Added backend env vars in Vercel (SUPABASE_URL, SUPABASE_KEY, etc.)
- [ ] Added `VITE_RAG_API_URL` in Vercel
- [ ] Pushed code to GitHub
- [ ] Vercel deployed backend
- [ ] Redeployed frontend
- [ ] Tested - works! ✅

## 📝 Your Vercel Project URL

From the error, your URL is:
`https://founderai-workspace-ow964rq32-atman-artwork-llps-projects.vercel.app`

So set:
`VITE_RAG_API_URL` = `https://founderai-workspace-ow964rq32-atman-artwork-llps-projects.vercel.app/api`

---

**Do Step 1 first (add env vars in Vercel), then push the code!**
