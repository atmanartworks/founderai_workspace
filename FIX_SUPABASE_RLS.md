# 🔧 Fix: Supabase Row-Level Security (RLS) Error

## 🚨 The Problem

Error: `'new row violates row-level security policy for table "conversations"'`

**Root Cause:** The backend is using the Supabase **anon key** which is subject to Row-Level Security (RLS) policies. Backend services should use the **service role key** to bypass RLS.

## ✅ The Fix

I've updated the code to:
1. **Prefer service role key** if available
2. **Fallback to anon key** if service role key is not set
3. **Log which key type** is being used

## ✅ Next Steps

### Step 1: Verify Environment Variables in Render

Make sure you have **BOTH** keys set in Render:

1. **Render Dashboard** → Your service → **Environment**
2. Verify these variables exist:
   - `SUPABASE_URL` = your Supabase project URL
   - `SUPABASE_KEY` = your Supabase **anon key** (for fallback)
   - `SUPABASE_SERVICE_ROLE_KEY` = your Supabase **service role key** (required for backend)

### Step 2: Get Your Service Role Key

1. Go to **Supabase Dashboard** → Your project
2. **Settings** → **API**
3. Find **"service_role"** key (NOT the anon key)
4. Copy it

### Step 3: Add Service Role Key to Render

1. **Render Dashboard** → Your service → **Environment**
2. Click **"Add Environment Variable"**
3. **Key:** `SUPABASE_SERVICE_ROLE_KEY`
4. **Value:** Paste your service role key
5. **Save**

### Step 4: Redeploy

1. **Render Dashboard** → Your service
2. **Manual Deploy** tab
3. **Clear build cache & deploy**
4. OR just push the code fix (auto-deploys)

### Step 5: Test

After redeploy:
- Send a message in the frontend
- Should work without RLS errors! ✅

## 🎯 What Changed

**Updated `app/config.py`:**
- Added `SUPABASE_SERVICE_ROLE_KEY` support
- Created `SUPABASE_KEY_TO_USE` that prefers service role key

**Updated `app/database.py`:**
- Uses `SUPABASE_KEY_TO_USE` instead of `SUPABASE_KEY`
- Logs which key type is being used

## ⚠️ Important Notes

- **Service role key bypasses ALL RLS policies** - this is correct for backend services
- **Never expose service role key** in frontend code
- **Anon key** is for frontend (subject to RLS)
- **Service role key** is for backend (bypasses RLS)

## 📋 Quick Checklist

- [ ] Got service role key from Supabase dashboard
- [ ] Added `SUPABASE_SERVICE_ROLE_KEY` to Render environment
- [ ] Pushed code fix (or will redeploy)
- [ ] Render redeployed
- [ ] Tested - no more RLS errors! ✅

---

**The fix is committed. Add the service role key to Render and redeploy!**
