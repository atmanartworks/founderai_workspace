# 🚀 Deployment Guide: GitHub, Vercel & Render

This guide will walk you through deploying your Founder AI application to GitHub, Vercel (frontend), and Render (backend).

## 📋 Prerequisites

- Git installed and configured
- GitHub account
- Vercel account (free tier available)
- Render account (free tier available)
- Node.js and npm installed (for local testing)

---

## Step 1: Prepare Your Repository

### 1.1 Update .gitignore

The `.gitignore` file has been updated to exclude:
- Python virtual environments (`venv/`, `.venv/`)
- Python cache files (`__pycache__/`, `*.pyc`)
- Large files (`.index`, `.pkl`, model files)
- Environment variables (`.env` files)
- Supabase temp files

### 1.2 Remove Large Files from Git History (if already committed)

If you've already committed large files, remove them:

```powershell
# Remove virtual environments from git tracking
git rm -r --cached rag-backend/venv
git rm -r --cached rag-backend/.venv

# Remove cache files
git rm -r --cached rag-backend/**/__pycache__

# Commit the removal
git commit -m "Remove large files and virtual environments"
```

### 1.3 Check for Large Files

Before pushing, verify no large files are tracked:

```powershell
# Check file sizes
git ls-files | ForEach-Object { Get-Item $_ | Select-Object Name, @{Name="Size(MB)";Expression={[math]::Round($_.Length/1MB,2)}} } | Where-Object { $_.'Size(MB)' -gt 50 } | Format-Table -AutoSize
```

---

## Step 2: Push to GitHub

### 2.1 Stage Your Changes

```powershell
# Add all files (respecting .gitignore)
git add .

# Check what will be committed
git status
```

### 2.2 Commit Your Changes

```powershell
git commit -m "Prepare for deployment: Add deployment configs and update .gitignore"
```

### 2.3 Push to GitHub

```powershell
# If this is your first push to a new repository
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main

# If you already have a remote (like 'merwin' branch)
git push origin merwin

# Or push to main branch
git checkout -b main
git push -u origin main
```

**Note:** GitHub has a 100MB file size limit. If you encounter errors:
- Files over 100MB cannot be pushed
- Use Git LFS for large files (if needed)
- Or exclude them using `.gitignore`

---

## Step 3: Deploy Frontend to Vercel

### 3.1 Connect Repository to Vercel

1. Go to [vercel.com](https://vercel.com) and sign in
2. Click **"Add New Project"**
3. Import your GitHub repository
4. Vercel will auto-detect it's a Vite project

### 3.2 Configure Environment Variables

In Vercel project settings, add these environment variables:

```
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
VITE_RAG_API_URL=https://your-backend.onrender.com
```

**Note:** You'll add `VITE_RAG_API_URL` after deploying the backend in Step 4.

**To add environment variables:**
1. Go to your project → **Settings** → **Environment Variables**
2. Add each variable for **Production**, **Preview**, and **Development**
3. Click **Save**

### 3.3 Configure Build Settings

Vercel should auto-detect from `vercel.json`, but verify:
- **Framework Preset:** Vite
- **Build Command:** `npm run build`
- **Output Directory:** `dist`
- **Install Command:** `npm install`

### 3.4 Deploy

1. Click **"Deploy"**
2. Wait for build to complete
3. Your app will be live at `https://your-project.vercel.app`

---

## Step 4: Deploy Backend to Render

### 4.1 Create a New Web Service

1. Go to [render.com](https://render.com) and sign in
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Select your repository

### 4.2 Configure Service Settings

**Basic Settings:**
- **Name:** `rag-backend` (or your preferred name)
- **Environment:** `Python 3`
- **Region:** Choose closest to your users
- **Branch:** `main` (or your branch)

**Build & Deploy:**
- **Build Command:** `pip install -r rag-backend/requirements.txt`
- **Start Command:** `cd rag-backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

**Plan:** Choose **Starter** (free tier) or **Standard** (paid)

### 4.3 Add Environment Variables

In Render dashboard, go to **Environment** tab and add:

```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
OPENAI_API_KEY=your_openai_api_key
PYTHON_VERSION=3.12.0
PORT=10000
```

### 4.4 Health Check (Optional but Recommended)

Add a health check endpoint in your FastAPI app:

```python
# In rag-backend/app/main.py
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

### 4.5 Deploy

1. Click **"Create Web Service"**
2. Render will build and deploy your backend
3. Your API will be available at `https://your-service.onrender.com`

---

## Step 5: Update Frontend API URLs

### 5.1 Add Environment Variable in Vercel

The frontend already uses `VITE_RAG_API_URL` environment variable. Add it to Vercel:

```
VITE_RAG_API_URL=https://your-backend.onrender.com
```

**Note:** The frontend code in `src/services/ragApi.ts` already handles this - it will use `VITE_RAG_API_URL` if set, otherwise defaults to `http://127.0.0.1:8000` for local development.

### 5.3 Redeploy Frontend

After updating, Vercel will auto-redeploy on next push, or manually trigger a redeploy.

---

## Step 6: Configure CORS (Important!)

### 6.1 Verify Backend CORS Settings

Your FastAPI backend already has CORS configured in `rag-backend/app/main.py`. Currently it allows all origins (`allow_origins=["*"]`), which works but you can make it more secure:

```python
# Optional: Update rag-backend/app/main.py for better security
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",  # Local dev
        "https://your-frontend.vercel.app",  # Production
        "https://*.vercel.app",  # Preview deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Note:** The current `allow_origins=["*"]` will work fine for deployment, but restricting to specific domains is more secure.

---

## 🔧 Troubleshooting

### Issue: Large Files Rejected by GitHub

**Solution:**
1. Check `.gitignore` includes the file patterns
2. Remove from git: `git rm --cached <file>`
3. Commit the removal
4. Push again

### Issue: Build Fails on Vercel

**Solutions:**
- Check build logs in Vercel dashboard
- Verify `package.json` has correct build script
- Ensure all dependencies are in `package.json`
- Check Node.js version compatibility
- Test build locally first: `npm run build`
- See **[VERCEL_TROUBLESHOOTING.md](./VERCEL_TROUBLESHOOTING.md)** for detailed fixes

### Issue: "404: DEPLOYMENT_NOT_FOUND" Error

**Solutions:**
- Check deployment status in Vercel dashboard
- Review build logs for errors
- Verify environment variables are set
- Clear build cache and redeploy
- Ensure `vercel.json` is in root directory
- See **[VERCEL_TROUBLESHOOTING.md](./VERCEL_TROUBLESHOOTING.md)** for complete troubleshooting guide

### Issue: Backend Not Starting on Render

**Solutions:**
- Check Render logs for errors
- Verify `requirements.txt` is correct
- Ensure `startCommand` is correct
- Check environment variables are set
- Verify Python version matches

### Issue: CORS Errors

**Solution:**
- Update CORS settings in backend to include your Vercel domain
- Check browser console for specific error
- Verify API URL is correct in frontend

### Issue: Environment Variables Not Working

**Solutions:**
- Restart services after adding env vars
- Verify variable names match exactly (case-sensitive)
- Check for typos in variable values
- Ensure variables are set for correct environment (Production/Preview)

---

## 📝 Quick Reference

### Git Commands
```powershell
git add .
git commit -m "Your message"
git push origin main
```

### Check Large Files
```powershell
git ls-files | ForEach-Object { Get-Item $_ | Select-Object Name, @{Name="Size(MB)";Expression={[math]::Round($_.Length/1MB,2)}} } | Where-Object { $_.'Size(MB)' -gt 50 }
```

### Remove Large Files from Git
```powershell
git rm --cached <file_or_directory>
git commit -m "Remove large files"
```

---

## 🎉 Next Steps

1. ✅ Push code to GitHub
2. ✅ Deploy frontend to Vercel
3. ✅ Deploy backend to Render
4. ✅ Configure environment variables
5. ✅ Update API URLs
6. ✅ Test your deployed application
7. ✅ Set up custom domains (optional)

---

## 📚 Additional Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Render Documentation](https://render.com/docs)
- [GitHub Large Files Guide](https://docs.github.com/en/repositories/working-with-files/managing-large-files)
- [Git LFS (for very large files)](https://git-lfs.github.com/)

---

**Need Help?** Check the logs in Vercel and Render dashboards for detailed error messages.
