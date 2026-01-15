# 🔧 Fix Render - Update Manual Settings

## 🚨 The Problem

Render is still using the old build command. This means either:
1. The service was created manually (not using render.yaml)
2. Render.yaml isn't being read
3. Settings need to be updated manually in Render dashboard

## ✅ Solution: Update Settings in Render Dashboard

Since Render is using the old command, update it manually:

### Step 1: Go to Render Dashboard

1. Go to: https://dashboard.render.com
2. Click on your **rag-backend** service

### Step 2: Update Settings

1. Go to **Settings** tab
2. Scroll to **Build & Deploy** section

### Step 3: Update These Settings

**Root Directory:**
- Set to: `rag-backend`

**Build Command:**
- Change from: `pip install -r rag-backend/requirements.txt`
- Change to: `pip install -r requirements-railway.txt`

**Start Command:**
- Change from: `cd rag-backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Change to: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

**Python Version:**
- Set to: `3.12.0` (or leave as default)

### Step 4: Save and Redeploy

1. Click **"Save Changes"**
2. Go to **Manual Deploy** tab
3. Click **"Clear build cache & deploy"**
4. Wait for deployment

## 🎯 Alternative: Delete and Recreate Service

If manual update doesn't work:

1. **Delete the current service** in Render
2. **Create new Web Service**
3. **Connect GitHub repo**
4. **Render should auto-detect render.yaml** this time
5. **Verify settings match render.yaml**
6. **Add environment variables**
7. **Deploy**

## 📋 Quick Checklist

- [ ] Updated Root Directory to `rag-backend`
- [ ] Updated Build Command to `pip install -r requirements-railway.txt`
- [ ] Updated Start Command to `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- [ ] Saved changes
- [ ] Cleared build cache & redeployed
- [ ] Build successful
- [ ] Service is Live! ✅

---

**Update the settings manually in Render dashboard - that's the fastest fix!**
