# 🚀 Create Separate Backend Project in Vercel

This guide will help you create a **new separate Vercel project** for your backend, so frontend and backend are deployed independently.

## 📋 What We're Doing

- **Frontend Project:** `founderai-workspace` (already exists)
- **Backend Project:** `founderai-workspace-backend` (new - we'll create this)

## ✅ Step 1: Prepare Backend Files

I've created the necessary files:
- ✅ `rag-backend/vercel.json` - Backend Vercel config
- ✅ `rag-backend/api/index.py` - Serverless function handler
- ✅ `rag-backend/api/requirements.txt` - Python dependencies

## ✅ Step 2: Push Backend Files to GitHub

First, commit and push the backend configuration:

```powershell
git add rag-backend/vercel.json rag-backend/api/
git commit -m "Add Vercel config for separate backend project"
git push origin merwin
```

## ✅ Step 3: Create New Vercel Project for Backend

1. **Go to Vercel Dashboard:**
   - https://vercel.com/dashboard
   - Click **"Add New..."** → **"Project"**

2. **Import Repository:**
   - Select your GitHub repository: `atmanartworks/founderai_workspace` (or your repo name)
   - Click **"Import"**

3. **Configure Project:**
   - **Project Name:** `founderai-workspace-backend` (or any name you prefer)
   - **Root Directory:** Click **"Edit"** → Set to: `rag-backend`
   - **Framework Preset:** Leave as "Other" or "None"
   - **Build Command:** Leave empty (Vercel will use `vercel.json`)
   - **Output Directory:** Leave empty (Vercel will use `vercel.json`)
   - **Install Command:** Leave empty

4. **Environment Variables:**
   Add these variables:
   - `SUPABASE_URL` = your Supabase URL
   - `SUPABASE_KEY` = your Supabase anon key
   - `SUPABASE_SERVICE_ROLE_KEY` = your service role key
   - `OPENAI_API_KEY` = your OpenAI API key
   - `LOCAL_EMBEDDING_MODEL` = `all-MiniLM-L6-v2` (optional, for lighter model)

   **Set for:** Production, Preview, Development (check all)

5. **Click "Deploy"**

## ✅ Step 4: Wait for Deployment

- Vercel will:
  - Install Python dependencies
  - Build serverless functions
  - Deploy backend

- **Note:** First deployment may take 3-5 minutes

## ✅ Step 5: Get Backend URL

After deployment completes:

1. **Go to Deployments tab**
2. **Click on the latest deployment**
3. **Copy the URL** (e.g., `https://founderai-workspace-backend.vercel.app`)

This is your **backend URL**!

## ✅ Step 6: Update Frontend to Use New Backend

1. **Go to Frontend Project:**
   - Open `founderai-workspace` project in Vercel
   - Go to **Settings** → **Environment Variables**

2. **Update `VITE_RAG_API_URL`:**
   - Find `VITE_RAG_API_URL`
   - Update value to: `https://your-backend-project.vercel.app`
   - (Replace with your actual backend URL from Step 5)
   - Click **Save**

3. **Redeploy Frontend:**
   - Go to **Deployments** tab
   - Click **"Redeploy"** on latest deployment
   - Wait for completion

## ✅ Step 7: Test

1. **Visit your frontend:** `https://your-frontend.vercel.app`
2. **Try sending a message**
3. **Should connect to backend!** ✅

## 🎯 Quick Checklist

- [ ] Pushed backend files to GitHub
- [ ] Created new Vercel project for backend
- [ ] Set root directory to `rag-backend`
- [ ] Added backend environment variables
- [ ] Deployed backend project
- [ ] Got backend URL
- [ ] Updated `VITE_RAG_API_URL` in frontend project
- [ ] Redeployed frontend
- [ ] Tested - works! ✅

## 📝 Important Notes

### Backend Routes

Your backend will be available at:
- Health: `https://your-backend.vercel.app/health`
- Chat: `https://your-backend.vercel.app/api/chat/message`
- Vault: `https://your-backend.vercel.app/api/vault/*`
- Embeddings: `https://your-backend.vercel.app/api/embeddings/*`

### Root Directory Setting

**CRITICAL:** Make sure to set **Root Directory** to `rag-backend` in the Vercel project settings. This tells Vercel where your backend code is located.

### Environment Variables

Both projects need their own environment variables:
- **Backend project:** Needs `SUPABASE_URL`, `SUPABASE_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `OPENAI_API_KEY`
- **Frontend project:** Needs `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`, `VITE_RAG_API_URL`

---

**Ready? Start with Step 2 (push files), then create the new project in Vercel!**
