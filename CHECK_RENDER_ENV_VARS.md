# ✅ Check Render Environment Variables

## 🚨 The Problem

Build succeeded, but app fails to start. This is likely because **environment variables are missing** in Render.

## ✅ Solution: Add Environment Variables in Render

### Step 1: Go to Render Dashboard

1. Go to: https://dashboard.render.com
2. Click on your **rag-backend** service

### Step 2: Add Environment Variables

1. Go to **Environment** tab (or **Settings** → **Environment Variables**)
2. Click **"Add Environment Variable"**
3. **Add these EXACT variables:**

   ```
   SUPABASE_URL = your_supabase_url
   SUPABASE_KEY = your_supabase_anon_key
   SUPABASE_SERVICE_ROLE_KEY = your_service_role_key
   OPENAI_API_KEY = your_openai_key
   PYTHON_VERSION = 3.12.0
   PORT = 10000
   ```

4. **Click "Save Changes"** after adding each one

### Step 3: Redeploy

1. Go to **Manual Deploy** tab
2. Click **"Clear build cache & deploy"**
3. Wait for deployment

## 🎯 Verify Variables Are Set

After adding, you should see all variables listed in the **Environment** section.

## 📋 Quick Checklist

- [ ] `SUPABASE_URL` is set
- [ ] `SUPABASE_KEY` is set
- [ ] `SUPABASE_SERVICE_ROLE_KEY` is set
- [ ] `OPENAI_API_KEY` is set
- [ ] `PYTHON_VERSION` = `3.12.0` (optional)
- [ ] `PORT` = `10000` (optional, Render sets this automatically)
- [ ] Saved all changes
- [ ] Redeployed
- [ ] App starts successfully! ✅

---

**Add environment variables in Render - that's likely the issue!**
