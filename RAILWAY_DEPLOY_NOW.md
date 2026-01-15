# 🚂 Deploy to Railway - Do This Now!

I've prepared everything for Railway deployment. Here's what to do:

## ✅ Files Created

- ✅ `railway.json` - Railway configuration
- ✅ `rag-backend/Procfile` - Start command for Railway
- ✅ `RAILWAY_QUICK_START.md` - Detailed guide

## ✅ Quick Steps (5 Minutes)

### Step 1: Sign Up on Railway

1. Go to: **https://railway.app**
2. Click **"Start a New Project"**
3. **Login with GitHub**
4. Authorize Railway

### Step 2: Deploy from GitHub

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose: `atmanartworks/founderai_workspace` (your repo)
4. Click **"Deploy Now"**

### Step 3: Configure

1. **Click on the service** that was created
2. **Settings** → **Root Directory** → Set to: `rag-backend`
3. **Variables** tab → Add:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `SUPABASE_SERVICE_ROLE_KEY`
   - `OPENAI_API_KEY`

### Step 4: Get URL

1. After deployment, go to **Settings** → **Domains**
2. **Copy the URL** (e.g., `https://your-project.up.railway.app`)

### Step 5: Update Frontend

1. **Vercel** → Frontend project → **Settings** → **Environment Variables**
2. **Update `VITE_RAG_API_URL`** to your Railway URL
3. **Redeploy frontend**

### Step 6: Test!

- Visit frontend
- Send a message
- **Should work!** ✅

## 🎯 Why Railway Works

- ✅ **No CORS blocking** - Full server control
- ✅ **Auto-detects FastAPI** - No complex config
- ✅ **Free tier** - $5 credit/month
- ✅ **Easy deployment** - From GitHub
- ✅ **Automatic HTTPS** - No setup needed

## 📋 What You Need

**Before starting:**
- [ ] GitHub repo is pushed (we just committed Railway config)
- [ ] Have your environment variable values ready:
  - Supabase URL
  - Supabase keys
  - OpenAI API key

**After deployment:**
- [ ] Railway backend URL
- [ ] Update frontend `VITE_RAG_API_URL`
- [ ] Test!

## ⚡ Quick Command Reference

**If you need to push the Railway config first:**

```powershell
git push origin merwin
```

**Then follow the steps above!**

---

**Start now: Go to railway.app and sign up!**
