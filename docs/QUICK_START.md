# 🚀 Quick Start Guide - Running RAG Backend

## Prerequisites

- Python 3.8+ installed
- Virtual environment (recommended)
- Required environment variables in `.env` file

## Step-by-Step Setup

### 1. Navigate to the Project Directory

```powershell
cd rag-backend
```

### 2. Create Virtual Environment (if not already created)

```powershell
python -m venv venv
```

### 3. Activate Virtual Environment

**Windows PowerShell:**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows CMD:**
```cmd
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Install Dependencies

```powershell
pip install -r requirements.txt
```

**Note:** This may take a few minutes as it installs:
- FastAPI and Uvicorn
- Supabase client
- Sentence Transformers (large ML model)
- Groq client
- PDF/DOCX processing libraries

### 5. Configure Environment Variables

Make sure your `.env` file in the `rag-backend` directory contains:

```env
# Supabase Configuration
SUPABASE_URL=https://axaxcynwwpndnvdbjbow.supabase.co
SUPABASE_KEY=your_supabase_service_role_key_here
SUPABASE_BUCKET=vault

# LLM Provider (choose one or both - OpenAI takes priority)
# Option 1: OpenAI (recommended)
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-3.5-turbo

# Option 2: Groq (fallback, free tier available)
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant

# Embedding Model (optional, defaults to nomic-embed-text-v1)
# Options: nomic-embed-text-v1 (768 dims, recommended), nomic-embed-text-v1.5, all-MiniLM-L6-v2 (384 dims)
LOCAL_EMBEDDING_MODEL=nomic-embed-text-v1
```

**Where to get these:**
- **SUPABASE_URL & SUPABASE_KEY**: From your Supabase project dashboard → Settings → API
- **OPENAI_API_KEY**: Get from https://platform.openai.com/api-keys (recommended)
- **GROQ_API_KEY**: Sign up at https://console.groq.com/ (optional, free fallback)
- **SUPABASE_BUCKET**: Should be "vault" (create it in Supabase Storage if it doesn't exist)

**Note:** The system uses OpenAI if `OPENAI_API_KEY` is set, otherwise falls back to Groq if `GROQ_API_KEY` is set.

### 6. Run the Server

**Option A: Using the PowerShell Script (Windows)**
```powershell
.\start.ps1
```

**Option B: Using Python Directly**
```powershell
uvicorn app.main:app --reload
```

**Option C: Using Python Module**
```powershell
python -m uvicorn app.main:app --reload
```

The server will start on: **http://localhost:8000**

## Verify It's Working

### 1. Check Health Endpoint

Open your browser or use PowerShell:
```powershell
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "healthy"}
```

### 2. Open API Documentation

Navigate to: **http://localhost:8000/docs**

This opens Swagger UI where you can:
- See all available endpoints
- Test the API interactively
- View request/response schemas

### 3. Run Test Suite (Optional)

```powershell
python test_api.py
```

## Common Issues & Solutions

### ❌ "Module not found" errors

**Solution:** Make sure virtual environment is activated and dependencies are installed:
```powershell
pip install -r requirements.txt
```

### ❌ "SUPABASE_URL or SUPABASE_KEY missing"

**Solution:** Check your `.env` file exists and has correct values. Make sure it's in the `rag-backend` directory.

### ❌ "Bucket not found" error when uploading

**Solution:** Create the "vault" bucket in Supabase:
1. Go to Supabase Dashboard → Storage
2. Click "New bucket"
3. Name: `vault`
4. Set to Private
5. Create bucket

See `VAULT_BUCKET_SETUP.md` for detailed instructions.

### ❌ Port 8000 already in use

**Solution:** Use a different port:
```powershell
uvicorn app.main:app --reload --port 8001
```

### ❌ Sentence Transformers download is slow

**Solution:** This is normal on first run. The model (~90MB) downloads automatically. Subsequent runs will be faster.

## API Endpoints

Once running, you can access:

- **Health Check:** `GET /health`
- **API Docs:** `GET /docs` (Swagger UI)
- **Upload File:** `POST /api/vault/upload`
- **Embed Document:** `POST /api/embeddings/embed-document/{vault_id}`
- **Chat:** `POST /api/chat/message`
- **Search:** `POST /api/search/semantic-search`
- **List Files:** `GET /api/vault/list`

## Next Steps

1. ✅ Server is running
2. 📝 Upload a document via `/api/vault/upload`
3. 📝 Embed the document via `/api/embeddings/embed-document/{vault_id}`
4. 📝 Test chat functionality via `/api/chat/message`
5. 📝 Test search via `/api/search/semantic-search`

## Development Tips

- **Auto-reload:** The `--reload` flag automatically restarts the server when you change code
- **Logs:** Check the terminal for error messages and debug info
- **Testing:** Use the Swagger UI at `/docs` for interactive testing
- **Database:** Check Supabase dashboard to see data being created

## Stopping the Server

Press `Ctrl+C` in the terminal where the server is running.

---

**Need help?** Check the other documentation files:
- `TESTING.md` - Testing guide
- `VAULT_BUCKET_SETUP.md` - Storage setup
- `INTEGRATION_GUIDE.md` - Clean Architecture integration

