# 🔧 Fix Commit Author Name on GitHub

Your commits are showing as "atmanartworks" but you want them to show a different name.

## ✅ Quick Fix: Update Git Config

### Step 1: Check Current Settings

```powershell
git config user.name
git config user.email
```

### Step 2: Update Your Name and Email

```powershell
# Set your name (replace with your desired name)
git config user.name "Your Name"

# Set your email (use the email associated with your GitHub account)
git config user.email "your.email@example.com"
```

**Important:** Use the **email address associated with your GitHub account** so commits are linked to your profile.

### Step 3: Verify Settings

```powershell
git config user.name
git config user.email
```

### Step 4: Future Commits Will Use New Name

All **new commits** will now use your updated name and email.

## 🔄 Fix Existing Commits (Optional)

If you want to change the author of **existing commits**, you'll need to rewrite history:

### Option A: Change Last Commit Only

```powershell
git commit --amend --author="Your Name <your.email@example.com>" --no-edit
git push --force origin merwin
```

**⚠️ Warning:** Only do this if you haven't shared the commits with others, or coordinate with your team.

### Option B: Change All Commits (Advanced)

This requires rewriting git history. Only do this if:
- You're the only one working on this branch
- You haven't shared these commits publicly
- You understand the risks

```powershell
# This will open an editor - follow the instructions
git filter-branch --env-filter '
OLD_EMAIL="old-email@example.com"
CORRECT_NAME="Your Name"
CORRECT_EMAIL="your.email@example.com"

if [ "$GIT_COMMITTER_EMAIL" = "$OLD_EMAIL" ]
then
    export GIT_COMMITTER_NAME="$CORRECT_NAME"
    export GIT_COMMITTER_EMAIL="$CORRECT_EMAIL"
fi
if [ "$GIT_AUTHOR_EMAIL" = "$OLD_EMAIL" ]
then
    export GIT_AUTHOR_NAME="$CORRECT_NAME"
    export GIT_AUTHOR_EMAIL="$CORRECT_EMAIL"
fi
' --tag-name-filter cat -- --branches --tags

# Force push (DANGEROUS - only if you're sure)
git push --force --all origin
```

## 📋 Quick Steps Summary

1. **Set your name:**
   ```powershell
   git config user.name "Your Name"
   ```

2. **Set your email (must match GitHub):**
   ```powershell
   git config user.email "your.github.email@example.com"
   ```

3. **Verify:**
   ```powershell
   git config user.name
   git config user.email
   ```

4. **Make a test commit:**
   ```powershell
   git commit --allow-empty -m "Test commit with new name"
   git push origin merwin
   ```

5. **Check GitHub** - your new commits will show the correct name!

## 🎯 Set Globally (Optional)

If you want these settings for **all repositories** on your computer:

```powershell
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

## ⚠️ Important Notes

### Email Must Match GitHub
- Your git email **must match** the email in your GitHub account
- Go to GitHub → Settings → Emails to see/add emails
- Commits will only link to your GitHub profile if emails match

### Existing Commits
- **Future commits** will use the new name automatically
- **Existing commits** on GitHub will still show "atmanartworks"
- To change existing commits, you need to rewrite history (see above)

### Multiple Machines
- If you work on multiple computers, set git config on each one
- Or use `--global` flag to set it for all repos

## 🔍 Find Your GitHub Email

1. Go to [github.com/settings/emails](https://github.com/settings/emails)
2. Check which email addresses are verified
3. Use one of those emails in your git config

---

**Quick Fix:** Just update your git config - future commits will show the correct name!
