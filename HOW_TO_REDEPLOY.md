# 🔄 How to Redeploy on Vercel

When Vercel tells you to "redeploy to take effect" (usually after adding environment variables), here's how:

## Method 1: Quick Redeploy (No Code Changes)

**Use this when you:**
- Added/updated environment variables
- Changed project settings
- Want to rebuild with same code

### Steps:

1. **Go to Vercel Dashboard**
   - Visit [vercel.com/dashboard](https://vercel.com/dashboard)
   - Click on your project: `founderai-workspace-vr4i`

2. **Go to Deployments Tab**
   - Click **"Deployments"** in the top navigation

3. **Find Latest Deployment**
   - You'll see a list of deployments
   - The most recent one is at the top

4. **Click Redeploy**
   - Hover over the deployment
   - Click the **three dots (⋯)** menu on the right
   - Click **"Redeploy"**
   - Confirm if prompted

5. **Watch the Build**
   - A new deployment will start
   - Click on it to see build logs in real-time
   - Wait for it to complete (1-3 minutes)

6. **Done!**
   - Once complete, your changes (like new env vars) will be active

## Method 2: Push to GitHub (Triggers Auto-Deploy)

**Use this when you:**
- Made code changes
- Want to deploy new commits
- Prefer automatic deployment

### Steps:

```powershell
# If you have uncommitted changes, commit them first
git add .
git commit -m "Update configuration"

# Push to GitHub
git push origin merwin
```

Vercel will automatically:
- Detect the new push
- Start a new deployment
- Build and deploy your app

## Method 3: Manual Deploy Button

If you see a **"Deploy"** button in the Overview tab:

1. Go to **Overview** tab
2. Click the **"Deploy"** button (if available)
3. Select branch (usually `merwin` or `main`)
4. Click **"Deploy"**

## ⚠️ Important Notes

### After Adding Environment Variables:
- **Always redeploy** after adding/updating environment variables
- Environment variables are only loaded during build time
- Existing deployments won't have new variables until redeployed

### When to Use Each Method:

**Use Method 1 (Redeploy)** when:
- ✅ You just added environment variables
- ✅ You changed Vercel settings
- ✅ You want to rebuild without code changes

**Use Method 2 (Push)** when:
- ✅ You made code changes
- ✅ You want to deploy new commits
- ✅ You prefer automatic deployments

## 📋 Quick Checklist

- [ ] Added environment variables in Vercel Settings
- [ ] Went to Deployments tab
- [ ] Clicked "Redeploy" on latest deployment
- [ ] Watched build logs
- [ ] Deployment completed successfully
- [ ] Verified changes are live

## 🐛 Troubleshooting

### Can't Find Redeploy Button?
- Make sure you're in the **Deployments** tab
- Look for the three dots (⋯) menu
- If no deployments exist, you need to deploy first

### Redeploy Failed?
- Check build logs for errors
- Verify environment variables are set correctly
- Ensure code builds locally: `npm run build`

### Changes Not Taking Effect?
- Make sure you redeployed AFTER adding environment variables
- Check that variables are set for the correct environment (Production/Preview)
- Clear browser cache and try again

---

**Quick Tip:** After adding environment variables, always use Method 1 (Redeploy) to ensure they're included in the build!
