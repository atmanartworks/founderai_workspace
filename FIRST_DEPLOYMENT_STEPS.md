# 🚀 First Deployment Steps - Vercel

Your Vercel project is created but needs its first deployment. Follow these steps:

## Current Status
- ✅ Vercel project created: `founderai-workspace-vr4i`
- ⏳ No production deployment yet
- 📝 Code ready to push to GitHub

## Step 1: Push Code to GitHub

This will trigger Vercel to automatically deploy:

```powershell
git push origin merwin
```

**Or if you want to use main branch:**
```powershell
git checkout -b main
git push -u origin main
```

## Step 2: Add Environment Variables in Vercel

**BEFORE the build completes**, add your environment variables:

1. In Vercel dashboard, go to your project: `founderai-workspace-vr4i`
2. Click **Settings** (in the top navigation)
3. Click **Environment Variables** (left sidebar)
4. Add these variables for **Production**, **Preview**, and **Development**:

   ```
   VITE_SUPABASE_URL=your_supabase_project_url
   VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
   ```

   **Note:** You can add `VITE_RAG_API_URL` later after deploying your backend.

5. Click **Save** after adding each variable

## Step 3: Trigger Deployment

After pushing to GitHub, Vercel will automatically:
- Detect the new commit
- Start a new deployment
- Build your project
- Deploy to production

**OR** you can manually trigger:

1. Go to **Deployments** tab in Vercel
2. Click **Redeploy** on the latest deployment
3. Or click **Deploy** button if available

## Step 4: Monitor the Build

1. Go to **Deployments** tab
2. Click on the active deployment
3. Watch the build logs in real-time
4. Wait for build to complete (usually 1-3 minutes)

## Step 5: Check Your Live Site

Once deployment succeeds:
- Your site will be live at: `https://founderai-workspace-vr4i.vercel.app`
- Or check the deployment for the exact URL

## ⚠️ If Build Fails

1. **Check Build Logs:**
   - Click on the failed deployment
   - Scroll through the logs
   - Look for error messages

2. **Common Issues:**
   - Missing environment variables → Add them in Settings
   - Build errors → Check logs for specific errors
   - Missing dependencies → Verify `package.json` is correct

3. **Fix and Redeploy:**
   - Fix the issue locally
   - Test: `npm run build`
   - Commit and push again
   - Or click **Redeploy** in Vercel

## 📋 Quick Checklist

- [ ] Code pushed to GitHub
- [ ] Environment variables added in Vercel
- [ ] Deployment triggered (automatic or manual)
- [ ] Build logs checked
- [ ] Deployment successful
- [ ] Site is live and accessible

## 🎯 Next Steps After Successful Deployment

1. ✅ Test your live site
2. ✅ Verify environment variables are working
3. ✅ Deploy backend to Render (see DEPLOYMENT_GUIDE.md)
4. ✅ Add `VITE_RAG_API_URL` environment variable
5. ✅ Redeploy frontend to connect to backend

---

**Need Help?** See `VERCEL_TROUBLESHOOTING.md` for detailed solutions.
