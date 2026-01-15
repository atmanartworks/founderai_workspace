# 🚀 Use Render Instead - Free & Ready!

Since Railway requires a paid plan, let's use **Render** - it's free and we already have the config!

## ✅ Why Render

- ✅ **Free tier available**
- ✅ **We have `render.yaml` already configured!**
- ✅ **No CORS issues**
- ✅ **Easy deployment from GitHub**

## ✅ Quick Steps

### Step 1: Go to Render

1. Go to: **https://render.com**
2. Click **"Get Started for Free"**
3. **Sign up with GitHub**
4. Authorize Render

### Step 2: Create Web Service

1. Click **"New +"** → **"Web Service"**
2. **Connect your GitHub repository:**
   - Select: `atmanartworks/founderai_workspace` (your repo)
   - Click **"Connect"**

### Step 3: Configure Service

**Render will auto-detect `render.yaml`!**

But verify these settings:

1. **Name:** `rag-backend` (or any name)
2. **Region:** Choose closest to you
3. **Branch:** `merwin` (or your branch)
4. **Root Directory:** `rag-backend`
5. **Environment:** `Python 3`
6. **Build Command:** `pip install -r rag-backend/requirements.txt`
   - **OR** use: `pip install -r rag-backend/requirements-railway.txt` (lighter, no sentence-transformers)
7. **Start Command:** `cd rag-backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Step 4: Add Environment Variables

1. Scroll to **"Environment Variables"**
2. Click **"Add Environment Variable"**
3. Add these:
   - `SUPABASE_URL` = your Supabase URL
   - `SUPABASE_KEY` = your Supabase anon key
   - `SUPABASE_SERVICE_ROLE_KEY` = your service role key
   - `OPENAI_API_KEY` = your OpenAI key
   - `PYTHON_VERSION` = `3.12.0`

### Step 5: Choose Plan

1. **Free Plan** (for testing):
   - ✅ Free
   - ⚠️ Sleeps after 15 min inactivity
   - ⚠️ Limited memory (512MB)

2. **Starter Plan** ($7/month):
   - ✅ Always on
   - ✅ More memory (512MB)
   - ✅ Better for production

**For now, choose Free to test!**

### Step 6: Deploy

1. Click **"Create Web Service"**
2. Wait for deployment (3-5 minutes)
3. Render will give you a URL like: `https://rag-backend.onrender.com`

### Step 7: Update Frontend

1. **Vercel** → Frontend project → **Settings** → **Environment Variables**
2. **Update `VITE_RAG_API_URL`** to your Render URL
3. **Redeploy frontend**

### Step 8: Test!

- Visit frontend
- Send a message
- **Should work!** ✅

## 🎯 Memory Issue Fix

**If you get "out of memory" error:**

1. **Use lighter requirements:**
   - Use `requirements-railway.txt` (I created this - no sentence-transformers)
   - Update build command to: `pip install -r rag-backend/requirements-railway.txt`

2. **Or upgrade to Starter plan** ($7/month) for more memory

## 📋 Quick Checklist

- [ ] Signed up on Render
- [ ] Created Web Service from GitHub
- [ ] Configured settings (or use render.yaml)
- [ ] Added environment variables
- [ ] Chose plan (Free for testing)
- [ ] Deployed successfully
- [ ] Got Render backend URL
- [ ] Updated `VITE_RAG_API_URL` in Vercel
- [ ] Redeployed frontend
- [ ] Tested - works! ✅

---

**Start now: Go to render.com and create a Web Service!**
