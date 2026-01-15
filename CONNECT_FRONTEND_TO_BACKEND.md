# 🔗 Connect Frontend to Backend - Step by Step

Your backend is deployed! Now let's connect your frontend to it.

## ✅ Step 1: Get Your Backend URL

1. **Go to Vercel Dashboard:**
   - Open your **backend project** (e.g., `founderai-workspace-backend`)
   - Go to **Deployments** tab
   - Click on the latest (successful) deployment
   - **Copy the URL** (e.g., `https://founderai-workspace-backend.vercel.app`)

   **Or:**
   - Go to **Settings** → **Domains**
   - Copy the production domain

## ✅ Step 2: Test Backend (Optional but Recommended)

Test that your backend is working:

1. **Health Check:**
   Open in browser: `https://your-backend-url.vercel.app/health`
   
   Should show: `{"status":"healthy"}`

2. **If it works:** ✅ Backend is ready!
3. **If it doesn't:** Check deployment logs in Vercel

## ✅ Step 3: Update Frontend Environment Variable

1. **Go to Frontend Project:**
   - Open your **frontend project** in Vercel (e.g., `founderai-workspace`)
   - Go to **Settings** → **Environment Variables**

2. **Add/Update `VITE_RAG_API_URL`:**
   - **If it exists:** Click to edit
   - **If it doesn't exist:** Click **"Add New"**
   
   - **Key:** `VITE_RAG_API_URL`
   - **Value:** `https://your-backend-url.vercel.app`
   
   **Important:** 
   - Use the **exact backend URL** from Step 1
   - **No trailing slash** (don't add `/` at the end)
   - Example: `https://founderai-workspace-backend.vercel.app`

3. **Set for:**
   - ✅ Check **Production**
   - ✅ Check **Preview**
   - ✅ Check **Development**

4. **Click "Save"**

## ✅ Step 4: Redeploy Frontend

After updating the environment variable:

1. **Go to Deployments tab** in your frontend project
2. **Click "Redeploy"** on the latest deployment
3. **Or:** Push a new commit to trigger redeploy:
   ```powershell
   git commit --allow-empty -m "Trigger frontend redeploy"
   git push origin merwin
   ```

4. **Wait for deployment** to complete (usually 1-2 minutes)

## ✅ Step 5: Test the Connection

1. **Visit your frontend:**
   - Go to: `https://your-frontend-url.vercel.app`
   - Or your custom domain

2. **Try sending a message:**
   - Open the chat
   - Type a message (e.g., "Hello")
   - Click send

3. **Expected Result:**
   - ✅ Message should send successfully
   - ✅ Should get a response from the backend
   - ✅ No "Failed to fetch" error

## 🎯 Quick Checklist

- [ ] Got backend URL from Vercel
- [ ] Tested backend health endpoint (optional)
- [ ] Updated `VITE_RAG_API_URL` in frontend project
- [ ] Set for Production, Preview, Development
- [ ] Redeployed frontend
- [ ] Tested chat - works! ✅

## 📝 Example URLs

**Backend URL (what you copy):**
```
https://founderai-workspace-backend.vercel.app
```

**Frontend Environment Variable:**
```
VITE_RAG_API_URL = https://founderai-workspace-backend.vercel.app
```

**Backend Endpoints (for reference):**
- Health: `https://your-backend.vercel.app/health`
- Chat: `https://your-backend.vercel.app/api/chat/message`
- Vault: `https://your-backend.vercel.app/api/vault/*`

## ⚠️ Troubleshooting

### Still getting "Failed to fetch"?

1. **Check backend URL:**
   - Make sure `VITE_RAG_API_URL` matches your backend URL exactly
   - No trailing slash
   - Includes `https://`

2. **Check CORS:**
   - Backend should allow all origins (already configured)
   - If issues persist, check backend logs

3. **Check environment variable:**
   - Make sure it's set for **Production** environment
   - Redeploy frontend after adding/updating

4. **Check browser console:**
   - Open DevTools (F12)
   - Check Network tab for failed requests
   - Look for CORS errors or 404s

### Backend not responding?

1. **Check backend deployment:**
   - Go to backend project → Deployments
   - Make sure latest deployment is successful
   - Check build logs for errors

2. **Test backend directly:**
   - Visit: `https://your-backend.vercel.app/health`
   - Should return `{"status":"healthy"}`

---

**Ready? Start with Step 1 - get your backend URL!**
