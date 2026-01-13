# ✅ Backend on Vercel - Quick Setup Guide

I've set up the backend for Vercel deployment! Here's what's ready:

## ✅ What's Been Created

1. **`api/index.py`** - Vercel serverless function handler
2. **`api/requirements.txt`** - Python dependencies (without sentence-transformers)
3. **Updated `vercel.json`** - Added Python runtime configuration

## 🚀 Next Steps

### Step 1: Add Environment Variables in Vercel

1. **Go to your Vercel project:**
   - Open your project dashboard
   - Go to **Settings** → **Environment Variables**

2. **Add Backend Variables:**
   - `SUPABASE_URL` = your Supabase URL
   - `SUPABASE_KEY` = your Supabase anon key
   - `SUPABASE_SERVICE_ROLE_KEY` = your service role key
   - `OPENAI_API_KEY` = your OpenAI key

3. **Set for:** Production, Preview, Development
4. **Click Save** for each

### Step 2: Push to GitHub

```powershell
git add .
git commit -m "Add Vercel serverless backend support"
git push origin merwin
```

### Step 3: Watch Deployment

1. **Go to Vercel Deployments tab**
2. **New deployment starts automatically**
3. **Watch build logs:**
   - Frontend builds first
   - Backend Python functions build
   - Both deploy together

### Step 4: Test Backend

Once deployed, test your endpoints:

- **Health:** `https://your-project.vercel.app/api/health`
- **Chat:** `https://your-project.vercel.app/api/api/chat/message`

**Note:** Routes are at `/api/api/...` because:
- Vercel adds `/api` prefix for serverless functions
- Your FastAPI routes have `/api` prefix
- Result: `/api` + `/api/chat` = `/api/api/chat`

### Step 5: Update Frontend

1. **In Vercel → Environment Variables:**
   - Add: `VITE_RAG_API_URL` = `https://your-project.vercel.app/api`
   - Set for: Production, Preview, Development

2. **Redeploy:**
   - Go to Deployments
   - Click "Redeploy"

## 🎯 API URL Structure

**Local Development:**
- Backend: `http://127.0.0.1:8000`
- Frontend uses: `VITE_RAG_API_URL` or defaults to `http://127.0.0.1:8000`

**Production (Vercel):**
- Backend: `https://your-project.vercel.app/api`
- Frontend uses: `VITE_RAG_API_URL` = `https://your-project.vercel.app/api`

## ⚠️ Important Notes

### Memory:
- ✅ Vercel free tier: 1024MB (better than Render!)
- ✅ No sentence-transformers = no memory issues
- ✅ Using OpenAI embeddings = lighter

### Execution Time:
- Free tier: 10 seconds max per request
- Should be enough for API calls
- For long operations, consider async processing

### Routes:
Your backend routes will be:
- `/api/health` → `https://your-project.vercel.app/api/health`
- `/api/api/chat/message` → `https://your-project.vercel.app/api/api/chat/message`

**To fix the double `/api/api`:**
- Option 1: Remove `/api` prefix from FastAPI routes
- Option 2: Use `/api` in frontend URL (current setup)

## 📋 Quick Checklist

- [ ] Added backend env vars to Vercel
- [ ] Pushed code to GitHub
- [ ] Vercel deployment completed
- [ ] Tested `/api/health` endpoint
- [ ] Added `VITE_RAG_API_URL` to frontend
- [ ] Redeployed frontend
- [ ] Tested full stack connection

---

**Ready to deploy!** Just push to GitHub and Vercel will handle everything! 🚀
