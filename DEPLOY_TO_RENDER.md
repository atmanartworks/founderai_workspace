# 🚀 Deploy Backend to Render - Complete Guide

Your Vercel frontend is deployed! Now let's deploy the backend to Render.

## ✅ Step 1: Sign Up / Sign In to Render

1. **Go to Render:**
   - Visit: https://render.com

2. **Sign In or Sign Up:**
   - Use your email (or create account if needed)
   - Free tier is available

3. **Verify Account:**
   - Make sure you're logged in
   - You'll see the Render dashboard

## 🎯 Step 2: Create New Web Service

1. **Go to Dashboard:**
   - Click **"New +"** button (top right)
   - Select **"Web Service"**

2. **Connect GitHub:**
   - Click **"Connect GitHub"** or **"Connect account"**
   - Authorize Render to access your repositories
   - Make sure it can access `atmanartworks/founderai_workspace`

3. **Select Repository:**
   - Find: `atmanartworks/founderai_workspace`
   - Click **"Connect"**

## ⚙️ Step 3: Configure Service Settings

### Basic Settings:

- **Name:** `rag-backend` (or your preferred name)
- **Region:** Choose closest to your users (e.g., US East, US West, Europe)
- **Branch:** `merwin` (or your branch name)
- **Root Directory:** Leave empty (or set to `.`)

### Build & Deploy Settings:

- **Environment:** `Python 3`
- **Build Command:** `pip install -r rag-backend/requirements.txt`
- **Start Command:** `cd rag-backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

**Important:** Render automatically sets `$PORT`, so use it in the start command.

### Plan:

- **Starter** (Free tier) - Good for testing
- **Standard** (Paid) - Better performance, no sleep

## 🔑 Step 4: Add Environment Variables

Go to the **Environment** tab and add these variables:

### Required Variables:

1. **PYTHON_VERSION**
   - Value: `3.12.0`

2. **SUPABASE_URL**
   - Value: Your Supabase project URL
   - Example: `https://xxxxx.supabase.co`

3. **SUPABASE_KEY**
   - Value: Your Supabase anon/public key
   - Get from: Supabase Dashboard → Settings → API → anon public

4. **SUPABASE_SERVICE_ROLE_KEY**
   - Value: Your Supabase service role key
   - Get from: Supabase Dashboard → Settings → API → service_role
   - ⚠️ Keep this secret!

5. **OPENAI_API_KEY**
   - Value: Your OpenAI API key
   - Get from: https://platform.openai.com/api-keys

6. **PORT** (Optional - Render sets this automatically)
   - Value: `10000` (or leave Render to set it)

### How to Add:

1. Click **"Add Environment Variable"**
2. Enter **Key** and **Value**
3. Click **"Save Changes"**
4. Repeat for each variable

## 📊 Step 5: Deploy

1. **Review Settings:**
   - Double-check all settings
   - Verify environment variables are added

2. **Create Service:**
   - Click **"Create Web Service"** button
   - Render will start building immediately

3. **Monitor Build:**
   - Watch the build logs in real-time
   - First build takes 5-10 minutes (installing dependencies)
   - Subsequent builds are faster

## 🔍 Step 6: Verify Deployment

### Check Health Endpoint:

Once deployed, test the health check:

```
https://your-service-name.onrender.com/health
```

Should return: `{"status": "healthy"}`

### Check Logs:

1. Go to your service in Render
2. Click **"Logs"** tab
3. Look for:
   - ✅ "Application startup complete"
   - ✅ "Uvicorn running on..."
   - ❌ Any error messages

## 🎯 Step 7: Get Your Backend URL

Once deployment succeeds:

1. **Your backend URL:**
   - Format: `https://your-service-name.onrender.com`
   - Find it in the Render dashboard (top of service page)

2. **Save This URL:**
   - You'll need it for the frontend
   - Example: `https://rag-backend.onrender.com`

## 🔗 Step 8: Connect Frontend to Backend

Now update your Vercel frontend to use the Render backend:

1. **Go to Vercel:**
   - Open your project
   - Go to **Settings** → **Environment Variables**

2. **Add Backend URL:**
   - Variable: `VITE_RAG_API_URL`
   - Value: `https://your-backend.onrender.com` (your Render URL)
   - Set for: Production, Preview, Development
   - Click **Save**

3. **Redeploy Frontend:**
   - Go to **Deployments** tab
   - Click **"Redeploy"** on latest deployment
   - Wait for completion

## ⚠️ Important Notes

### Free Tier Limitations:

- **Sleeps after 15 minutes** of inactivity
- **First request** after sleep takes 30-60 seconds (cold start)
- **Consider upgrading** to Standard plan for production

### Build Time:

- **First build:** 5-10 minutes (installing Python packages)
- **Subsequent builds:** 2-5 minutes
- **sentence-transformers** takes time to download models

### Environment Variables:

- **Never commit** `.env` files to git
- **Add all variables** in Render dashboard
- **Restart service** after adding new variables

## 🐛 Troubleshooting

### Build Fails:

1. **Check Build Logs:**
   - Look for error messages
   - Common: Missing dependencies, Python version mismatch

2. **Verify requirements.txt:**
   - All packages listed correctly
   - No syntax errors

3. **Check Start Command:**
   - Should be: `cd rag-backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Make sure path is correct

### Service Won't Start:

1. **Check Logs:**
   - Look for startup errors
   - Check environment variables are set

2. **Verify Health Check:**
   - Test: `https://your-service.onrender.com/health`
   - Should return JSON

3. **Check Port:**
   - Make sure using `$PORT` in start command
   - Render sets this automatically

### Environment Variables Not Working:

1. **Verify Variables:**
   - Check all are added in Render
   - No typos in variable names
   - Values are correct

2. **Restart Service:**
   - Go to **Manual Deploy** → **Clear build cache & deploy**
   - Or restart from dashboard

## 📋 Quick Checklist

- [ ] Signed into Render
- [ ] Created new Web Service
- [ ] Connected GitHub repository
- [ ] Configured build settings
- [ ] Added all environment variables
- [ ] Created service
- [ ] Build completed successfully
- [ ] Health check works: `/health`
- [ ] Got backend URL
- [ ] Added `VITE_RAG_API_URL` to Vercel
- [ ] Redeployed frontend
- [ ] Tested full stack connection

## 🎯 Next Steps After Deployment

1. ✅ Test backend API endpoints
2. ✅ Test frontend-backend connection
3. ✅ Monitor Render logs for errors
4. ✅ Set up custom domain (optional)
5. ✅ Consider upgrading to Standard plan for production

---

**Ready?** Go to Render and create your Web Service! 🚀
