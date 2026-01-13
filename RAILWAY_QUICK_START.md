# 🚂 Railway Quick Start - Deploy in 5 Minutes

## ✅ Step 1: Sign Up (1 minute)

1. Go to: **https://railway.app**
2. Click **"Start a New Project"**
3. Sign up with **GitHub** (click "Login with GitHub")
4. Authorize Railway to access your repositories

## ✅ Step 2: Create Project (1 minute)

1. Click **"New Project"** (top right)
2. Select **"Deploy from GitHub repo"**
3. Find and select: `atmanartworks/founderai_workspace` (or your repo name)
4. Click **"Deploy Now"**

**Railway will automatically:**
- Detect Python
- Start building
- Create a service

## ✅ Step 3: Configure Service (2 minutes)

### 3.1 Set Root Directory

1. Click on the **service** that was created
2. Go to **Settings** tab
3. Scroll to **"Root Directory"**
4. Click **"Edit"**
5. Set to: `rag-backend`
6. Click **"Save"**

### 3.2 Set Start Command (Optional - Railway auto-detects)

Railway should auto-detect FastAPI, but if needed:

1. **Settings** → **Deploy**
2. **Start Command:** `cd rag-backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. **Save**

## ✅ Step 4: Add Environment Variables (1 minute)

1. Go to **Variables** tab
2. Click **"New Variable"** for each:

   **Add these:**
   - `SUPABASE_URL` = your Supabase URL
   - `SUPABASE_KEY` = your Supabase anon key
   - `SUPABASE_SERVICE_ROLE_KEY` = your service role key
   - `OPENAI_API_KEY` = your OpenAI API key

3. **Click "Add"** for each variable

## ✅ Step 5: Wait for Deployment

1. Go to **Deployments** tab
2. Watch the build progress
3. Wait for **"Deploy Successful"** (usually 2-3 minutes)

## ✅ Step 6: Get Your Backend URL

1. After deployment, go to **Settings** tab
2. Scroll to **"Domains"**
3. You'll see a URL like: `https://your-project.up.railway.app`
4. **Copy this URL** - this is your backend URL!

**Or:**
- Click **"Generate Domain"** if you want a custom name
- Railway will give you a URL

## ✅ Step 7: Update Frontend

1. **Go to Vercel** → Frontend project
2. **Settings** → **Environment Variables**
3. **Update `VITE_RAG_API_URL`:**
   - Find `VITE_RAG_API_URL`
   - Update value to: `https://your-project.up.railway.app`
   - (Use the Railway URL from Step 6)
   - Set for: Production, Preview, Development
   - Click **Save**

4. **Redeploy Frontend:**
   - Go to **Deployments** tab
   - Click **"Redeploy"** on latest deployment

## ✅ Step 8: Test!

1. **Visit your frontend site**
2. **Try sending a message**
3. **Should work!** ✅ (No CORS issues!)

## 🎯 Quick Checklist

- [ ] Signed up on Railway with GitHub
- [ ] Created project from GitHub repo
- [ ] Set root directory to `rag-backend`
- [ ] Added all environment variables
- [ ] Deployment successful
- [ ] Got Railway backend URL
- [ ] Updated `VITE_RAG_API_URL` in Vercel frontend
- [ ] Redeployed frontend
- [ ] Tested - works! ✅

## 💡 Tips

- **Railway auto-detects** Python and FastAPI
- **No Docker needed** - Railway handles it
- **Free tier** includes $5 credit/month
- **Automatic HTTPS** - no configuration needed
- **No CORS issues** - full server control

## ⚠️ If You Get Errors

**Build fails?**
- Check that root directory is set to `rag-backend`
- Check that `requirements.txt` exists in `rag-backend/`

**App won't start?**
- Check environment variables are set
- Check start command is correct
- Check logs in Railway dashboard

**CORS still issues?**
- Railway doesn't block OPTIONS - should work automatically
- Check backend logs if needed

---

**Start with Step 1 - sign up on Railway!**
