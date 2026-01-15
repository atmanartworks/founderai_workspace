# 🐳 Deploy Backend with Docker - Complete Guide

If you want to use Docker, here's how to set it up for **Fly.io** (best Docker platform).

## ✅ Step 1: Create Dockerfile

**File:** `rag-backend/Dockerfile`

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Copy requirements
COPY api/requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app

# Expose port
EXPOSE 8000

# Run FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## ✅ Step 2: Create .dockerignore

**File:** `rag-backend/.dockerignore`

```
__pycache__
*.pyc
*.pyo
*.pyd
.Python
venv/
.venv/
.env
*.log
.git
.gitignore
README.md
```

## ✅ Step 3: Deploy to Fly.io

### 3.1 Install Fly CLI

**Windows (PowerShell):**
```powershell
iwr https://fly.io/install.ps1 -useb | iex
```

**Or download from:** https://fly.io/docs/hands-on/install-flyctl/

### 3.2 Login

```powershell
flyctl auth login
```

### 3.3 Create Fly App

```powershell
cd rag-backend
flyctl launch
```

**Answer prompts:**
- App name: `founderai-backend` (or any name)
- Region: Choose closest to you
- PostgreSQL: No (we use Supabase)
- Redis: No

### 3.4 Set Environment Variables

```powershell
flyctl secrets set SUPABASE_URL=your_supabase_url
flyctl secrets set SUPABASE_KEY=your_supabase_key
flyctl secrets set SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
flyctl secrets set OPENAI_API_KEY=your_openai_key
```

### 3.5 Deploy

```powershell
flyctl deploy
```

### 3.6 Get URL

```powershell
flyctl status
```

**Copy the URL** (e.g., `https://founderai-backend.fly.dev`)

## ✅ Step 4: Update Frontend

1. **Vercel** → Frontend project → **Settings** → **Environment Variables**
2. **Update `VITE_RAG_API_URL`** to your Fly.io URL
3. **Redeploy frontend**

## 🎯 Alternative: Railway with Docker

Railway also supports Docker:

1. **Create `Dockerfile`** (same as above)
2. **Railway** → New Project → Deploy from GitHub
3. **Railway auto-detects Dockerfile**
4. **Add environment variables**
5. **Deploy!**

## 📋 Quick Comparison

| Platform | Docker Support | Ease | Free Tier |
|----------|---------------|------|-----------|
| **Fly.io** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ✅ |
| **Railway** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ |
| **Render** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ |

---

**For Docker, I recommend Fly.io. For easiest setup, use Railway without Docker!**
