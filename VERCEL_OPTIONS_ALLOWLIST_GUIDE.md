# 📖 Step-by-Step: Configure Vercel OPTIONS Allowlist

## 🎯 Exact Steps to Fix CORS

### Step 1: Access Vercel Dashboard

1. Go to: https://vercel.com/dashboard
2. Sign in if needed

### Step 2: Open Backend Project

1. Find and click on: **`founderai-workspace-backend`**
   - (This is your backend project, not the frontend)

### Step 3: Go to Settings

1. Click **"Settings"** tab (top navigation)
2. Look for **"Deployment Protection"** in the left sidebar
3. Click **"Deployment Protection"**

### Step 4: Configure OPTIONS Allowlist

**Look for one of these sections:**

**Option A: "OPTIONS Allowlist"**
- Find "OPTIONS Allowlist" section
- Toggle it **ON** if it's off
- Click **"Add Path"** or **"+"** button
- Enter: `/api/*`
- Click **Save**

**Option B: "Preflight Allowlist"**
- Same as above, but might be called "Preflight Allowlist"

**Option C: "Bypass Methods"**
- Look for "Bypass Methods" or similar
- Enable **OPTIONS** method
- Add path: `/api/*`

### Step 5: Save and Wait

1. Click **"Save"** or **"Update"**
2. Wait **1-2 minutes** for changes to propagate

### Step 6: Test

1. **Open frontend site**
2. **Press F12** → **Console**
3. **Run:**
   ```javascript
   fetch('https://founderai-workspace-backend-dc090ufif.vercel.app/api/chat/message', {
     method: 'OPTIONS',
     headers: {
       'Origin': 'https://founderai-workspace-h37ukxw9d-atman-artwork-llps-projects.vercel.app',
       'Access-Control-Request-Method': 'POST'
     }
   })
   .then(r => {
     console.log('✅ Status:', r.status);
     console.log('✅ CORS:', r.headers.get('Access-Control-Allow-Origin'));
   });
   ```

4. **Should see:** Status 200 and CORS header! ✅

## 🖼️ What to Look For

The Deployment Protection page should have:
- Toggle switches for different protection methods
- A section for "OPTIONS" or "Preflight"
- Path input fields
- Save/Update button

## ⚠️ If You Don't See OPTIONS Allowlist

**Your Vercel plan might not include this feature.**

**Temporary workaround:**
1. **Disable Deployment Protection** temporarily
2. **Test if CORS works**
3. **If it works:** Re-enable and contact Vercel support to enable OPTIONS Allowlist
4. **If it doesn't work:** The issue is something else

---

**Follow these steps exactly - this should fix the CORS issue!**
