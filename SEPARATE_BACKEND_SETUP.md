# 🚀 Setup Separate Backend Project - Complete Guide

You want to deploy the backend as a **separate Vercel project**. This is a great approach! Here's everything you need to do:

## 📋 Overview

- **Frontend Project:** `founderai-workspace` (already deployed)
- **Backend Project:** `founderai-workspace-backend` (new - we'll create)

## ✅ Step 1: Files Are Ready!

I've created:
- ✅ `rag-backend/vercel.json` - Backend Vercel configuration
- ✅ `rag-backend/api/index.py` - Serverless function handler
- ✅ `rag-backend/api/requirements.txt` - Python dependencies (lightweight, no sentence-transformers)

## ✅ Step 2: Push Files to GitHub

Commit and push the backend configuration:

```powershell
git add rag-backend/vercel.json rag-backend/api/ vercel.json
git commit -m "Add separate backend project configuration"
git push origin merwin
```

## ✅ Step 3: Create New Vercel Project for Backend

### 3.1 Go to Vercel Dashboard

1. Open: https://vercel.com/dashboard
2. Click **"Add New..."** → **"Project"**

### 3.2 Import Repository

1. Select your repository: `atmanartworks/founderai_workspace` (or your repo name)
2. Click **"Import"**

### 3.3 Configure Project Settings

**IMPORTANT - Set Root Directory:**

1. Click **"Edit"** next to "Root Directory"
2. Set to: `rag-backend`
3. This tells Vercel where your backend code is!

**Other Settings:**
- **Project Name:** `founderai-workspace-backend` (or any name)
- **Framework Preset:** Leave as "Other" or "None"
- **Build Command:** Leave empty (uses `vercel.json`)
- **Output Directory:** Leave empty (uses `vercel.json`)
- **Install Command:** Leave empty

### 3.4 Add Environment Variables

Click **"Environment Variables"** and add:

```
SUPABASE_URL = your_supabase_url
SUPABASE_KEY = your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY = your_service_role_key
OPENAI_API_KEY = your_openai_key
```

**For each variable:**
- Check ✅ Production
- Check ✅ Preview
- Check ✅ Development
- Click **Save**

### 3.5 Deploy

Click **"Deploy"** and wait for deployment (3-5 minutes first time).

## ✅ Step 4: Get Backend URL

After deployment:

1. Go to **Deployments** tab
2. Click on the latest deployment
3. **Copy the URL** (e.g., `https://founderai-workspace-backend.vercel.app`)

This is your **backend URL**!

## ✅ Step 5: Update Frontend Environment Variable

1. **Go to Frontend Project:**
   - Open `founderai-workspace` project in Vercel
   - Go to **Settings** → **Environment Variables**

2. **Update `VITE_RAG_API_URL`:**
   - Find or add: `VITE_RAG_API_URL`
   - Set value to: `https://your-backend-project.vercel.app`
   - (Use the URL from Step 4)
   - Set for: Production, Preview, Development
   - Click **Save**

3. **Redeploy Frontend:**
   - Go to **Deployments** tab
   - Click **"Redeploy"** on latest deployment
   - Wait for completion

## ✅ Step 6: Test Backend

Test the backend directly:

1. **Health Check:**
   ```
   https://your-backend.vercel.app/health
   ```
   Should return: `{"status":"healthy"}`

2. **Test from Frontend:**
   - Visit your frontend site
   - Try sending a message
   - Should connect to backend! ✅

## 🎯 Quick Checklist

- [ ] Pushed backend files to GitHub
- [ ] Created new Vercel project for backend
- [ ] **Set root directory to `rag-backend`** (CRITICAL!)
- [ ] Added backend environment variables
- [ ] Deployed backend project
- [ ] Got backend URL
- [ ] Updated `VITE_RAG_API_URL` in frontend project
- [ ] Redeployed frontend
- [ ] Tested backend health endpoint
- [ ] Tested from frontend - works! ✅

## 📝 Important Notes

### Backend Routes

Your backend will be available at:
- Health: `https://your-backend.vercel.app/health`
- Chat: `https://your-backend.vercel.app/api/chat/message`
- Vault: `https://your-backend.vercel.app/api/vault/*`
- Embeddings: `https://your-backend.vercel.app/api/embeddings/*`

### Root Directory Setting

**CRITICAL:** The **Root Directory** must be set to `rag-backend` in Vercel project settings. This is the most important step!

### Memory Considerations

The `api/requirements.txt` I created excludes `sentence-transformers` to avoid memory issues. If you need local embeddings:
- Use OpenAI embeddings (recommended)
- Or upgrade Vercel plan if needed

### Environment Variables

**Backend Project Needs:**
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`
- `OPENAI_API_KEY`

**Frontend Project Needs:**
- `VITE_SUPABASE_URL`
- `VITE_SUPABASE_ANON_KEY`
- `VITE_RAG_API_URL` (points to backend)

---

**Ready? Start with Step 2 (push files), then create the new backend project in Vercel!**
