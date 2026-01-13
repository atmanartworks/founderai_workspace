# 🚀 Deploy Backend to Vercel (Serverless Functions)

Your friend is right! You can deploy the backend to Vercel as serverless functions. This is often better than Render for Python apps.

## ✅ Why Vercel for Backend?

- ✅ **Better free tier** - More generous limits
- ✅ **No sleep** - Always available
- ✅ **Serverless** - Scales automatically
- ✅ **Same account** - Frontend and backend together
- ✅ **Better performance** - Faster cold starts

## 🎯 Step 1: Update Vercel Configuration

We need to configure Vercel to handle the Python backend.

### Option A: Add Backend to Existing Vercel Project

1. **Go to your Vercel project:**
   - Open: `founderai-workspace` (or your project name)
   - Go to **Settings** → **General**

2. **Add Build Settings:**
   - Vercel will auto-detect Python files
   - Or manually configure if needed

### Option B: Create Separate Backend Project (Recommended)

Create a separate Vercel project just for the backend:

1. **Go to Vercel Dashboard:**
   - Click **"Add New Project"**

2. **Import Repository:**
   - Select: `atmanartworks/founderai_workspace`
   - Click **"Import"**

3. **Configure as Backend:**
   - **Project Name:** `rag-backend` (or your name)
   - **Root Directory:** `rag-backend`
   - **Framework Preset:** Other (or Python if available)
   - **Build Command:** `pip install -r requirements.txt`
   - **Output Directory:** Leave empty (for serverless)

## ⚙️ Step 2: Create Vercel Serverless Function

Vercel needs a specific structure for Python serverless functions.

### Create `api/index.py`:

This will be the entry point for Vercel serverless functions.

```python
# api/index.py
from rag_backend.app.main import app

# Export the FastAPI app for Vercel
handler = app
```

### Or use Vercel's Python runtime:

Create `vercel.json` with Python configuration:

```json
{
  "functions": {
    "rag-backend/app/**/*.py": {
      "runtime": "python3.9"
    }
  },
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "/rag-backend/app/main.py"
    }
  ]
}
```

## 🎯 Step 3: Configure Vercel for Python

### Update `vercel.json` in root:

```json
{
  "buildCommand": "cd rag-backend && pip install -r requirements.txt",
  "outputDirectory": "dist",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "framework": "vite",
  "functions": {
    "api/**/*.py": {
      "runtime": "python3.9"
    }
  },
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    },
    {
      "source": "/api/(.*)",
      "destination": "/api/index.py"
    }
  ]
}
```

## 🔑 Step 4: Add Environment Variables

In Vercel project settings, add backend environment variables:

1. **Go to Settings → Environment Variables**

2. **Add Backend Variables:**
   - `SUPABASE_URL` = your Supabase URL
   - `SUPABASE_KEY` = your Supabase anon key
   - `SUPABASE_SERVICE_ROLE_KEY` = your service role key
   - `OPENAI_API_KEY` = your OpenAI key
   - `PYTHON_VERSION` = `3.12.0` (optional)

3. **Set for:** Production, Preview, Development

## 📋 Alternative: Use Vercel Python Runtime

Vercel supports Python serverless functions natively. Here's the setup:

### Create `api/` directory structure:

```
api/
  index.py  (or handler.py)
```

### Simple handler for Vercel:

```python
# api/index.py
from http.server import BaseHTTPRequestHandler
import json
from rag_backend.app.main import app

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.w.write(json.dumps({"status": "healthy"}).encode())
    
    def do_POST(self):
        # Handle POST requests
        pass
```

## 🎯 Recommended: Separate Backend Project

**Best approach:** Create a separate Vercel project for backend:

1. **Create New Project:**
   - Name: `rag-backend`
   - Root: `rag-backend`
   - Framework: Other

2. **Configure:**
   - Build: `pip install -r requirements.txt`
   - Output: Leave empty

3. **Add Environment Variables:**
   - All backend env vars

4. **Deploy:**
   - Vercel will create serverless functions
   - Get the backend URL
   - Add to frontend as `VITE_RAG_API_URL`

## ⚠️ Important Notes

### Memory Limits:
- Vercel serverless functions have memory limits
- **Free tier:** 1024MB per function
- **Pro tier:** Up to 3008MB
- Still might need lighter model or OpenAI embeddings

### Execution Time:
- **Free tier:** 10 seconds max
- **Pro tier:** 60 seconds max
- For long operations, consider async processing

### Cold Starts:
- First request after inactivity: 1-3 seconds
- Subsequent requests: Fast
- Better than Render's sleep/wake

## 📋 Quick Steps Summary

1. **Create separate Vercel project for backend:**
   - New Project → Import `atmanartworks/founderai_workspace`
   - Root: `rag-backend`
   - Framework: Other

2. **Configure:**
   - Build: `pip install -r rag-backend/requirements.txt`
   - Add environment variables

3. **Deploy:**
   - Vercel handles Python serverless automatically
   - Get backend URL

4. **Connect frontend:**
   - Add `VITE_RAG_API_URL` to frontend project
   - Set to backend Vercel URL

## 🎯 My Recommendation

**Use separate Vercel project for backend:**
- ✅ Cleaner separation
- ✅ Independent scaling
- ✅ Better organization
- ✅ Easier to manage

---

**Want me to help set this up?** I can create the necessary files for Vercel serverless deployment!
