# 🔧 Fix Render Out of Memory Error

Render is showing "out of memory" error. This is common with Python ML applications using sentence-transformers.

## 🚨 Quick Solutions

### Solution 1: Upgrade Render Plan (Recommended - Fastest Fix)

The **Starter (Free)** plan has limited memory (512MB). Upgrade to Standard:

1. **Go to Render Dashboard:**
   - Open your service: `rag-backend`
   - Click **"Settings"** tab

2. **Change Plan:**
   - Scroll to **"Plan"** section
   - Change from **"Starter"** to **"Standard"**
   - Standard plan has 512MB+ memory (enough for sentence-transformers)

3. **Save and Redeploy:**
   - Click **"Save Changes"**
   - Service will restart with more memory
   - This usually fixes the issue immediately

**Cost:** Standard plan is ~$7/month, but has no sleep and more resources.

### Solution 2: Use OpenAI Embeddings Instead (Free - No Upgrade Needed)

If you're already using OpenAI for LLM, use OpenAI embeddings too (no local model needed):

1. **Update your code to use OpenAI embeddings:**
   - Remove sentence-transformers dependency
   - Use OpenAI's `text-embedding-3-small` model
   - Much lighter, no local model loading

2. **Benefits:**
   - ✅ No memory issues
   - ✅ Works on free tier
   - ✅ Faster (no model download)
   - ✅ Better quality embeddings

### Solution 3: Use Lighter Embedding Model

Switch to a smaller model that uses less memory:

1. **Update environment variable:**
   - Add: `LOCAL_EMBEDDING_MODEL=all-MiniLM-L6-v2`
   - This is a much smaller model (~80MB vs 400MB+)

2. **Update in Render:**
   - Go to Environment Variables
   - Add: `LOCAL_EMBEDDING_MODEL` = `all-MiniLM-L6-v2`
   - Redeploy

### Solution 4: Optimize Requirements (Remove Unused Packages)

Create a minimal requirements.txt for production:

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-dotenv==1.0.0
supabase>=2.24.0
httpx>=0.28.0
openai>=1.0.0
python-multipart>=0.0.20

# Optional - only if you need local embeddings
# sentence-transformers>=5.0.0
# einops>=0.7.0

# Document processing (only if needed)
PyPDF2==3.0.1
pdfplumber>=0.10.0
python-docx>=0.8.11

# Remove if not using FAISS locally
# faiss-cpu>=1.7.4
```

## 🎯 Recommended: Use OpenAI Embeddings

Since you're already using OpenAI, switch to OpenAI embeddings:

### Step 1: Update Code to Use OpenAI Embeddings

The code already supports OpenAI. Just ensure you're using it instead of sentence-transformers.

### Step 2: Update Requirements (Remove sentence-transformers)

Create `rag-backend/requirements-production.txt`:

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

### Step 3: Update Render Build Command

In Render settings, change build command to:
```
pip install -r rag-backend/requirements-production.txt
```

Or rename `requirements-production.txt` to `requirements.txt` and commit.

## 📋 Quick Fix Steps (Choose One)

### Option A: Upgrade Plan (5 minutes)
1. Render Dashboard → Your Service → Settings
2. Change Plan: Starter → Standard
3. Save and wait for restart
4. ✅ Fixed!

### Option B: Use OpenAI Embeddings (15 minutes)
1. Remove sentence-transformers from requirements
2. Update code to use OpenAI embeddings only
3. Update Render build command
4. Redeploy
5. ✅ Fixed!

### Option C: Use Lighter Model (10 minutes)
1. Add `LOCAL_EMBEDDING_MODEL=all-MiniLM-L6-v2` to Render env vars
2. Redeploy
3. ✅ Fixed!

## 🎯 My Recommendation

**For Production:** Upgrade to Standard plan ($7/month)
- ✅ Most reliable
- ✅ No sleep (always on)
- ✅ Enough memory for everything
- ✅ Better performance

**For Free Tier:** Use OpenAI embeddings
- ✅ No memory issues
- ✅ Works on free tier
- ✅ Better quality
- ✅ Faster startup

## ⚠️ Current Issue

Your app is trying to load `nomic-ai/nomic-embed-text-v1` which is a large model (~400MB+ in memory). The free tier can't handle this.

**Quick fix:** Upgrade to Standard plan, or switch to OpenAI embeddings.

---

**Which solution do you want to use?** I recommend upgrading to Standard plan for the fastest fix!
