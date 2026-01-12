# 🔧 Vercel Deployment Troubleshooting

## Issue: "404: DEPLOYMENT_NOT_FOUND" Error

This error means Vercel cannot find the deployment. Here's how to fix it:

### Solution 1: Check Deployment Status

1. **Go to Vercel Dashboard**
   - Visit [vercel.com/dashboard](https://vercel.com/dashboard)
   - Find your project
   - Check the **Deployments** tab

2. **Check Build Logs**
   - Click on the failed deployment
   - Review the build logs for errors
   - Common issues:
     - Build command failed
     - Missing environment variables
     - Dependency installation errors

### Solution 2: Re-deploy Your Project

1. **Delete and Recreate Project** (if needed)
   - Go to Project Settings → General
   - Scroll down and click "Delete Project"
   - Create a new project and import your GitHub repo again

2. **Manual Redeploy**
   - Go to your project in Vercel
   - Click on the latest deployment
   - Click "Redeploy" button

### Solution 3: Verify Project Configuration

#### Check Build Settings

In Vercel project settings, verify:
- **Framework Preset:** Vite (or leave as "Other")
- **Root Directory:** Leave empty (or set to `.` if needed)
- **Build Command:** `npm run build`
- **Output Directory:** `dist`
- **Install Command:** `npm install`

#### Verify vercel.json

Your `vercel.json` should be in the root directory. It should look like:

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "framework": "vite",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

### Solution 4: Check Environment Variables

1. **Go to Project Settings → Environment Variables**
2. **Add Required Variables:**
   - `VITE_SUPABASE_URL` - Your Supabase project URL
   - `VITE_SUPABASE_ANON_KEY` - Your Supabase anon key
   - `VITE_RAG_API_URL` - Your backend API URL (add after backend is deployed)

3. **Important:** 
   - Add variables for **Production**, **Preview**, and **Development**
   - Click **Save** after adding each variable
   - **Redeploy** after adding environment variables

### Solution 5: Check GitHub Connection

1. **Verify Repository Connection**
   - Go to Project Settings → Git
   - Ensure your GitHub repository is connected
   - Check the branch name (should be `main` or your default branch)

2. **Push Latest Code**
   ```powershell
   git add .
   git commit -m "Fix Vercel deployment"
   git push origin main
   ```
   - Vercel will automatically trigger a new deployment

### Solution 6: Common Build Errors

#### Error: "Build Command Failed"

**Possible Causes:**
- Missing dependencies in `package.json`
- TypeScript errors
- Build script issues

**Fix:**
1. Test build locally:
   ```powershell
   npm install
   npm run build
   ```
2. Fix any errors locally first
3. Commit and push fixes

#### Error: "Module Not Found"

**Fix:**
- Ensure all dependencies are in `package.json`
- Run `npm install` locally to update `package-lock.json`
- Commit `package-lock.json` to git

#### Error: "Environment Variable Missing"

**Fix:**
- Add all required environment variables in Vercel dashboard
- Ensure variable names start with `VITE_` for Vite projects
- Redeploy after adding variables

### Solution 7: Check File Structure

Ensure your project structure is correct:
```
your-project/
├── package.json
├── vercel.json
├── vite.config.ts
├── index.html
├── src/
│   └── main.tsx
└── dist/ (generated during build)
```

### Solution 8: Clear Cache and Rebuild

1. **In Vercel Dashboard:**
   - Go to your project
   - Settings → General
   - Scroll to "Clear Build Cache"
   - Click "Clear Build Cache"
   - Trigger a new deployment

### Solution 9: Check Node.js Version

1. **In Vercel Settings:**
   - Go to Settings → General
   - Check "Node.js Version"
   - Should be 18.x or 20.x (latest LTS)
   - If not, update it

### Solution 10: Verify Build Output

1. **Check if `dist` folder is created:**
   - Build locally: `npm run build`
   - Verify `dist` folder exists
   - Check `dist/index.html` exists

2. **If build fails locally:**
   - Fix errors before deploying
   - Check `vite.config.ts` for issues
   - Verify all imports are correct

## Quick Fix Checklist

- [ ] Check Vercel dashboard for deployment status
- [ ] Review build logs for errors
- [ ] Verify `vercel.json` is in root directory
- [ ] Add all required environment variables
- [ ] Test build locally (`npm run build`)
- [ ] Ensure `package-lock.json` is committed
- [ ] Push latest code to GitHub
- [ ] Clear build cache in Vercel
- [ ] Trigger manual redeploy

## Still Having Issues?

1. **Check Vercel Status Page:**
   - [status.vercel.com](https://status.vercel.com)

2. **Review Vercel Documentation:**
   - [vercel.com/docs](https://vercel.com/docs)

3. **Check Build Logs:**
   - Go to your deployment in Vercel
   - Click "View Function Logs" or "View Build Logs"
   - Look for specific error messages

4. **Common Issues:**
   - Missing environment variables → Add them in Settings
   - Build command failing → Test locally first
   - Wrong output directory → Check `vercel.json`
   - Framework not detected → Manually set in settings

## Next Steps After Fixing

Once deployment succeeds:
1. ✅ Note your production URL
2. ✅ Add `VITE_RAG_API_URL` environment variable
3. ✅ Redeploy to connect frontend to backend
4. ✅ Test your deployed application

---

**Need More Help?** Check the main [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for complete setup instructions.
