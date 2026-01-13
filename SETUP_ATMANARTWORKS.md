# ✅ Setup @atmanartworks Account - Step by Step

Following Option 2: Using @atmanartworks account for Git.

## Step 1: Update Git Config ✅

Already done! Your git config is now set to:
- **Name:** `atmanartworks`
- **Email:** (need to set this)

## Step 2: Set Email for @atmanartworks

You need to set the email associated with the @atmanartworks GitHub account:

```powershell
# Replace with the email for @atmanartworks GitHub account
git config user.email "atmanartworks-email@example.com"
```

**To find the email:**
1. Go to: https://github.com/atmanartworks
2. Or check: https://github.com/settings/emails (when logged in as @atmanartworks)
3. Use one of the verified emails

## Step 3: Update Remote URL

```powershell
git remote set-url origin https://github.com/atmanartworks/founderai_workspace.git
```

## Step 4: Verify Settings

```powershell
git config user.name
git config user.email
git remote -v
```

Should show:
- Name: `atmanartworks`
- Email: (your @atmanartworks email)
- Remote: `https://github.com/atmanartworks/founderai_workspace.git`

## Step 5: Create Repository on GitHub

1. **Go to GitHub:**
   - Make sure you're logged in as `@atmanartworks`
   - Visit: https://github.com/new

2. **Repository Settings:**
   - **Owner:** `atmanartworks`
   - **Repository name:** `founderai_workspace`
   - **Visibility:** Public or Private
   - **⚠️ IMPORTANT:** Do NOT check:
     - ❌ Add a README file
     - ❌ Add .gitignore
     - ❌ Choose a license
   - (Leave all unchecked)

3. **Click "Create repository"**

## Step 6: Push Your Code

After creating the repository:

```powershell
git push -u origin merwin
```

This will:
- ✅ Push all your commits
- ✅ Set up branch tracking
- ✅ Trigger Vercel to automatically deploy!

## Step 7: Connect @atmanartworks in Vercel

1. In Vercel dashboard
2. Click **"Connect @atmanartworks"** button
3. Sign in with @atmanartworks GitHub account
4. Authorize Vercel

## 🎯 Quick Command Summary

```powershell
# 1. Set email (replace with actual email)
git config user.email "atmanartworks-email@example.com"

# 2. Update remote
git remote set-url origin https://github.com/atmanartworks/founderai_workspace.git

# 3. Verify
git config user.name
git config user.email
git remote -v

# 4. Create repo on GitHub (github.com/new as @atmanartworks)

# 5. Push
git push -u origin merwin
```

---

**Next:** Set the email for @atmanartworks, then follow the steps above!
