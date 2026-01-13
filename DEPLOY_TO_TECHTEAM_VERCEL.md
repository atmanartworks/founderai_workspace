# 🚀 Deploy to Tech Team Vercel Account

Since the hobby plan isn't working, let's deploy to a new Vercel project under the tech team account (techteam@silambarasantr.com).

## ✅ Step 1: Sign In to Tech Team Vercel Account

1. **Go to Vercel:**
   - Visit: https://vercel.com/login

2. **Sign In:**
   - Use email: `techteam@silambarasantr.com`
   - Enter your password
   - Complete any 2FA if required

3. **Verify Account:**
   - Make sure you're logged into the tech team account
   - Check the account name in top right corner

## 🎯 Step 2: Create New Project

1. **Go to Dashboard:**
   - After signing in, you'll see the Vercel dashboard

2. **Add New Project:**
   - Click **"Add New Project"** button (usually top right)
   - Or go to: https://vercel.com/new

3. **Import Repository:**
   - You'll see a list of your GitHub repositories
   - Find: `atmanartworks/founderai_workspace`
   - Click **"Import"** next to it

## ⚙️ Step 3: Configure Project

1. **Project Settings:**
   - **Project Name:** `founderai-workspace` (or your preferred name)
   - **Framework Preset:** Vite (should auto-detect)
   - **Root Directory:** `.` (leave empty)
   - **Build Command:** `npm run build` (should auto-detect)
   - **Output Directory:** `dist` (should auto-detect)
   - **Install Command:** `npm install` (should auto-detect)

2. **Environment Variables:**
   - Click **"Environment Variables"** section
   - Add these variables:
     - `VITE_SUPABASE_URL` = your Supabase project URL
     - `VITE_SUPABASE_ANON_KEY` = your Supabase anon key
     - `VITE_RAG_API_URL` = (add after backend is deployed)
   - Set for: **Production**, **Preview**, and **Development**
   - Click **"Add"** after each variable

3. **Deploy:**
   - Click **"Deploy"** button
   - Wait for build to complete (1-3 minutes)

## 🔗 Step 4: Connect GitHub Account

If you need to connect @atmanartworks GitHub account:

1. **Go to Settings:**
   - Project → **Settings** → **Git**

2. **Connect GitHub:**
   - Click **"Connect GitHub Account"** or **"Change"**
   - Sign in with @atmanartworks GitHub account
   - Authorize Vercel

3. **Verify:**
   - Should show: `atmanartworks/founderai_workspace`

## 📊 Step 5: Monitor Deployment

1. **Go to Deployments Tab:**
   - Click **"Deployments"** in your project
   - Watch the build logs in real-time

2. **Wait for Completion:**
   - Build usually takes 1-3 minutes
   - You'll see progress in the logs

3. **Check Status:**
   - ✅ Success = Your site is live!
   - ❌ Failed = Check logs for errors

## 🎯 Step 6: Get Your Live URL

Once deployment succeeds:

1. **Your site will be live!**
   - URL format: `https://your-project-name.vercel.app`
   - Or check the deployment for the exact URL

2. **Test Your Site:**
   - Visit the URL
   - Check if everything works
   - Test your features

## ⚠️ If Build Fails

1. **Check Build Logs:**
   - Click on the failed deployment
   - Scroll through logs
   - Look for error messages

2. **Common Issues:**
   - Missing environment variables → Add them in Settings
   - Build errors → Check logs for specific errors
   - Missing dependencies → Verify `package.json`

3. **Fix and Redeploy:**
   - Fix the issue locally
   - Test: `npm run build`
   - Push to GitHub, or click **"Redeploy"**

## 📋 Quick Checklist

- [ ] Signed into Vercel with techteam@silambarasantr.com
- [ ] Created new project
- [ ] Imported `atmanartworks/founderai_workspace` repository
- [ ] Configured build settings (auto-detected)
- [ ] Added environment variables
- [ ] Clicked "Deploy"
- [ ] Build completed successfully
- [ ] Site is live and accessible

## 🎯 Alternative: Use Existing Project

If you already have a Vercel project under tech team account:

1. **Go to Existing Project:**
   - Find your project in dashboard
   - Click on it

2. **Update Git Connection:**
   - Go to **Settings** → **Git**
   - Disconnect current connection
   - Connect to `atmanartworks/founderai_workspace`

3. **Redeploy:**
   - Go to **Deployments** tab
   - Click **"Redeploy"** or push new code

## 🚀 Next Steps After Deployment

1. ✅ Test your live site
2. ✅ Verify environment variables work
3. ✅ Deploy backend to Render (see `DEPLOYMENT_GUIDE.md`)
4. ✅ Add `VITE_RAG_API_URL` environment variable
5. ✅ Redeploy frontend to connect to backend

---

**Ready?** Sign into tech team Vercel account and create a new project! 🚀
