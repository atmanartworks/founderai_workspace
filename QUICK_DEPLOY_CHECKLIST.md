# ✅ Quick Deployment Checklist

Use this checklist to ensure everything is ready for deployment.

## Pre-Deployment

- [ ] `.gitignore` updated (excludes venv, __pycache__, large files)
- [ ] Large files removed from git tracking (if any)
- [ ] Environment variables documented
- [ ] No sensitive data in code (API keys, passwords, etc.)

## GitHub Setup

- [ ] Repository created on GitHub
- [ ] Remote added: `git remote add origin <your-repo-url>`
- [ ] All changes committed
- [ ] Code pushed to GitHub: `git push origin main`
- [ ] Verified no large files (>100MB) in repository

## Vercel (Frontend) Setup

- [ ] Vercel account created
- [ ] GitHub repository connected
- [ ] Environment variables added:
  - [ ] `VITE_SUPABASE_URL`
  - [ ] `VITE_SUPABASE_ANON_KEY`
  - [ ] `VITE_RAG_API_URL` (your Render backend URL - add after backend is deployed)
- [ ] Build settings verified
- [ ] First deployment successful
- [ ] Frontend URL saved: `https://your-app.vercel.app`

## Render (Backend) Setup

- [ ] Render account created
- [ ] GitHub repository connected
- [ ] Web service created
- [ ] Environment variables added:
  - [ ] `SUPABASE_URL`
  - [ ] `SUPABASE_KEY`
  - [ ] `SUPABASE_SERVICE_ROLE_KEY`
  - [ ] `OPENAI_API_KEY`
  - [ ] `PYTHON_VERSION=3.12.0`
- [ ] Build command set: `pip install -r rag-backend/requirements.txt`
- [ ] Start command set: `cd rag-backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- [ ] Health check endpoint working: `/health`
- [ ] First deployment successful
- [ ] Backend URL saved: `https://your-backend.onrender.com`

## Post-Deployment

- [ ] Frontend can connect to backend (check browser console)
- [ ] API calls working (test a feature)
- [ ] CORS configured correctly
- [ ] Environment variables working in production
- [ ] Health check endpoint accessible
- [ ] Error handling working
- [ ] Logs checked for errors

## Testing

- [ ] Login/Signup works
- [ ] Chat functionality works
- [ ] Document upload works
- [ ] All API endpoints responding
- [ ] No console errors in browser
- [ ] No errors in Vercel/Render logs

---

**Quick Commands:**

```powershell
# Check git status
git status

# Add and commit
git add .
git commit -m "Ready for deployment"

# Push to GitHub
git push origin main

# Check for large files
git ls-files | ForEach-Object { Get-Item $_ | Select-Object Name, @{Name="Size(MB)";Expression={[math]::Round($_.Length/1MB,2)}} } | Where-Object { $_.'Size(MB)' -gt 50 }
```

---

**Need Help?** See `DEPLOYMENT_GUIDE.md` for detailed instructions.
