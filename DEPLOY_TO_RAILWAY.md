# 🚂 Deploy Backend to Railway - Step by Step

Railway is the easiest alternative to Vercel. No CORS issues!

## ✅ Step 1: Sign Up

1. Go to: https://railway.app
2. Click **"Start a New Project"**
3. Sign up with **GitHub** (easiest)
4. Authorize Railway to access your repos

## ✅ Step 2: Create New Project

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose your repository: `atmanartworks/founderai_workspace` (or your repo name)
4. Click **"Deploy Now"**

## ✅ Step 3: Configure Service

1. **Railway will detect Python automatically**
2. **Set Root Directory:**
   - Click on the service
   - Go to **Settings**
   - Set **Root Directory** to: `rag-backend`

3. **Set Start Command:**
   - In Settings → **Deploy**
   - Start Command: `cd rag-backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

4. **Or use the default** (Railway auto-detects FastAPI)

## ✅ Step 4: Add Environment Variables

1. Go to **Variables** tab
2. Add these variables:
   - `SUPABASE_URL` = your Supabase URL
   - `SUPABASE_KEY` = your Supabase anon key
   - `SUPABASE_SERVICE_ROLE_KEY` = your service role key
   - `OPENAI_API_KEY` = your OpenAI key
   - `PORT` = `8000` (Railway sets this automatically, but good to have)

## ✅ Step 5: Deploy

1. Railway will automatically:
   - Install dependencies from `rag-backend/requirements.txt`
   - Start your FastAPI app
   - Assign a public URL

2. **Wait for deployment** (usually 2-3 minutes)

## ✅ Step 6: Get Backend URL

1. After deployment, Railway gives you a URL like:
   - `https://your-project.up.railway.app`

2. **Copy this URL** - this is your backend URL!

## ✅ Step 7: Update Frontend

1. **Go to Vercel** → Frontend project
2. **Settings** → **Environment Variables**
3. **Update `VITE_RAG_API_URL`:**
   - Set to: `https://your-project.up.railway.app`
   - (Use the Railway URL from Step 6)
4. **Save**
5. **Redeploy frontend**

## ✅ Step 8: Test

1. **Visit your frontend**
2. **Try sending a message**
3. **Should work!** ✅ (No CORS issues!)

## 🎯 Why Railway Works

- ✅ Full control over server
- ✅ No platform-level CORS blocking
- ✅ FastAPI CORS middleware works perfectly
- ✅ Easy deployment from GitHub
- ✅ Free tier available

## 📋 Quick Checklist

- [ ] Signed up on Railway
- [ ] Created project from GitHub
- [ ] Set root directory to `rag-backend`
- [ ] Added environment variables
- [ ] Deployed successfully
- [ ] Got Railway backend URL
- [ ] Updated `VITE_RAG_API_URL` in Vercel frontend
- [ ] Redeployed frontend
- [ ] Tested - works! ✅

---

**Railway is the fastest way to get your backend working without CORS issues!**
