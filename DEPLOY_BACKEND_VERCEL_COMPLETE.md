# 🚀 Deploy Backend to Vercel - Complete Setup

Your friend is right! You can deploy the backend to Vercel as serverless functions. Here's the complete setup:

## ✅ What I've Set Up

1. **Created `api/index.py`** - Vercel serverless function handler
2. **Updated `vercel.json`** - Added Python runtime and API routes
3. **Configured routing** - Backend APIs will be at `/api/*`

## 🎯 Step 1: Add Backend Dependencies

Vercel needs to install Python dependencies. Create `api/requirements.txt`:

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-dotenv==1.0.0
supabase>=2.24.0
httpx>=0.28.0
openai>=1.0.0
python-multipart>=0.0.20
PyPDF2==3.0.1
pdfplumber>=0.10.0
python-docx>=0.8.11
```

**Note:** I've removed `sentence-transformers` to avoid memory issues. Use OpenAI embeddings instead.

## ⚙️ Step 2: Update Vercel Project Settings

In your existing Vercel project:

1. **Go to Settings → General:**
   - Vercel should auto-detect Python files
   - If not, it will work with the `vercel.json` config

2. **Add Environment Variables:**
   - Go to **Settings → Environment Variables**
   - Add backend variables:
     - `SUPABASE_URL`
     - `SUPABASE_KEY`
     - `SUPABASE_SERVICE_ROLE_KEY`
     - `OPENAI_API_KEY`
   - Set for: Production, Preview, Development

## 🚀 Step 3: Deploy

1. **Push to GitHub:**
   ```powershell
   git add .
   git commit -m "Add Vercel serverless backend support"
   git push origin merwin
   ```

2. **Vercel Auto-Deploys:**
   - Vercel detects the changes
   - Builds frontend and backend
   - Deploys both automatically

## 📊 Step 4: Test Backend

Once deployed, your backend will be at:

- **Health check:** `https://your-project.vercel.app/api/health`
- **Chat API:** `https://your-project.vercel.app/api/api/chat/message`
- **Vault API:** `https://your-project.vercel.app/api/api/vault/*`

**Note:** The `/api` prefix is added by Vercel for serverless functions.

## 🔗 Step 5: Update Frontend API URL

Update your frontend to use the Vercel backend:

1. **In Vercel → Environment Variables:**
   - Add: `VITE_RAG_API_URL` = `https://your-project.vercel.app/api`
   - Set for: Production, Preview, Development

2. **Redeploy Frontend:**
   - Go to Deployments tab
   - Click "Redeploy"

## ⚠️ Important Notes

### API Route Structure:

Your backend routes are at `/api/api/...` because:
- Vercel adds `/api` prefix for serverless functions
- Your FastAPI routes have `/api` prefix
- Result: `/api` + `/api/chat` = `/api/api/chat`

**To fix this**, update your frontend to use:
```typescript
const RAG_API_URL = import.meta.env.VITE_RAG_API_URL || "http://127.0.0.1:8000";
// Use: https://your-project.vercel.app/api
```

### Memory Limits:

- **Vercel Free:** 1024MB per function
- **Vercel Pro:** Up to 3008MB
- **Recommendation:** Use OpenAI embeddings (no local models)

### Execution Time:

- **Free tier:** 10 seconds max
- **Pro tier:** 60 seconds max
- Should be enough for most API calls

## 🎯 Alternative: Separate Backend Project

If you prefer a separate project:

1. **Create New Vercel Project:**
   - Name: `rag-backend`
   - Root: `rag-backend` (or use `api/` structure)
   - Framework: Other

2. **Configure:**
   - Build: `pip install -r rag-backend/requirements.txt`
   - Add environment variables

3. **Get Backend URL:**
   - Use this URL in frontend's `VITE_RAG_API_URL`

## 📋 Quick Checklist

- [ ] Created `api/index.py` ✅
- [ ] Updated `vercel.json` ✅
- [ ] Created `api/requirements.txt` (need to create)
- [ ] Added backend env vars to Vercel
- [ ] Pushed to GitHub
- [ ] Vercel auto-deployed
- [ ] Tested `/api/health` endpoint
- [ ] Updated `VITE_RAG_API_URL` in frontend
- [ ] Redeployed frontend

## 🎯 Next Steps

1. **Create `api/requirements.txt`** (I'll do this)
2. **Push to GitHub**
3. **Add environment variables in Vercel**
4. **Test backend endpoints**
5. **Update frontend API URL**

---

**Want me to create the `api/requirements.txt` file?** This will complete the setup!
