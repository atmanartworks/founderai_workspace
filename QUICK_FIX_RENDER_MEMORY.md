# ⚡ Quick Fix: Render Out of Memory

## 🚨 The Problem

Render free tier has **512MB memory**. The `nomic-ai/nomic-embed-text-v1` model needs **400MB+**, causing out of memory errors.

## ✅ Solution 1: Upgrade to Standard Plan (Fastest - 2 minutes)

1. **Render Dashboard:**
   - Go to your service: `rag-backend`
   - Click **"Settings"** tab

2. **Change Plan:**
   - Find **"Plan"** section
   - Change: **Starter** → **Standard**
   - Click **"Save Changes"**

3. **Wait for Restart:**
   - Service restarts automatically
   - Standard plan has 512MB+ memory
   - ✅ Fixed!

**Cost:** ~$7/month (no sleep, always on, more memory)

## ✅ Solution 2: Use Lighter Model (Free - 5 minutes)

Switch to a smaller model that fits in free tier:

1. **In Render Dashboard:**
   - Go to your service
   - Click **"Environment"** tab
   - Add new variable:
     - **Key:** `LOCAL_EMBEDDING_MODEL`
     - **Value:** `all-MiniLM-L6-v2`
   - Click **"Save Changes"**

2. **Redeploy:**
   - Go to **"Manual Deploy"** tab
   - Click **"Clear build cache & deploy"**
   - Wait for deployment

**This model is ~80MB** - fits in free tier!

## ✅ Solution 3: Use OpenAI Embeddings (Best Quality - Free)

Since you're using OpenAI, use their embeddings (no local model):

1. **Update requirements.txt:**
   - Remove `sentence-transformers` line
   - Keep only essential packages

2. **Update code** to use OpenAI embeddings only
   - No local model loading
   - Works on free tier
   - Better quality

## 📋 Quick Decision

**Need it working NOW?** → **Solution 1** (Upgrade to Standard - 2 minutes)

**Want to stay free?** → **Solution 2** (Use lighter model - 5 minutes)

**Best quality?** → **Solution 3** (Use OpenAI embeddings - 15 minutes)

---

**Recommendation:** Use **Solution 1** (upgrade) for fastest fix, or **Solution 2** (lighter model) to stay free!
