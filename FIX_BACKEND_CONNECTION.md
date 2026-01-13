# 🔧 Fix "Failed to fetch" Error - Complete Solution

Your frontend is deployed but can't connect to the backend. Here's how to fix it:

## 🚨 The Problem

- ✅ Frontend is deployed on Vercel
- ❌ Frontend is trying to connect to `http://127.0.0.1:8000` (local)
- ❌ Backend isn't deployed or connected yet

## ✅ Solution: Deploy Backend to Vercel (Recommended)

Since Render has memory issues, let's use Vercel for backend too!

### Step 1: Add Backend Environment Variables in Vercel

1. **Go to Vercel Dashboard:**
   - Open your project: `founderai-workspace` (or your project name)
   - Go to **Settings** → **Environment Variables**

2. **Add Backend Variables:**
   - `SUPABASE_URL` = your Supabase project URL
   - `SUPABASE_KEY` = your Supabase anon key
   - `SUPABASE_SERVICE_ROLE_KEY` = your Supabase service role key
   - `OPENAI_API_KEY` = your OpenAI API key

3. **Set for:** Production, Preview, Development
4. **Click Save** for each variable

### Step 2: Push Backend Code to GitHub

The backend files are ready. Push them:

```powershell
git add .
git commit -m "Add Vercel serverless backend"
git push origin merwin
```

### Step 3: Vercel Auto-Deploys

- Vercel detects the `api/` directory
- Automatically creates serverless functions
- Backend will be available at `/api/*` routes

### Step 4: Get Your Backend URL

Once deployed, your backend will be at:
- `https://your-project.vercel.app/api`

### Step 5: Update Frontend Environment Variable

1. **In Vercel → Environment Variables:**
   - Add: `VITE_RAG_API_URL` = `https://your-project.vercel.app/api`
   - **Replace `your-project` with your actual Vercel project name**
   - Set for: Production, Preview, Development
   - Click **Save**

2. **Redeploy Frontend:**
   - Go to **Deployments** tab
   - Click **"Redeploy"** on latest deployment
   - Wait for completion

### Step 6: Test

After redeploy:
- Visit your Vercel site
- Try sending a message
- Should connect to backend! ✅

## 🎯 Quick Steps Summary

1. ✅ Add backend env vars to Vercel (SUPABASE_URL, SUPABASE_KEY, etc.)
2. ✅ Push code: `git push origin merwin`
3. ✅ Wait for Vercel to deploy backend
4. ✅ Add `VITE_RAG_API_URL` = `https://your-project.vercel.app/api`
5. ✅ Redeploy frontend
6. ✅ Test!

## ⚠️ Important: Get Your Vercel Project URL

To find your exact Vercel URL:
1. Go to Vercel Dashboard
2. Open your project
3. Check the **"Domains"** section or **"Deployments"** tab
4. Your URL will be: `https://your-project-name.vercel.app`
5. Use this in `VITE_RAG_API_URL`

## 📋 What I've Prepared

- ✅ `api/index.py` - Backend serverless function
- ✅ `api/requirements.txt` - Python dependencies
- ✅ `vercel.json` - Updated with Python runtime
- ✅ Code is ready to deploy!

---

**Next:** Add environment variables in Vercel and push the code!
