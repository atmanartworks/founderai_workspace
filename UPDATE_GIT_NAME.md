# 📝 Update Your Git Commit Name

Your current git config:
- **Name:** `atmanartworks`
- **Email:** `techteam@silambarasantr.com`

## ✅ Update Your Name

Run these commands to change your commit name:

```powershell
# Update your name (replace "Your Name" with your desired name)
git config user.name "Your Name"

# Keep your email or update it to match your GitHub account
git config user.email "techteam@silambarasantr.com"
```

**Or if you want to use a different email that matches your GitHub:**

```powershell
git config user.name "Your Name"
git config user.email "your.github.email@example.com"
```

## 🔍 Check Your GitHub Email

1. Go to: https://github.com/settings/emails
2. See which emails are verified on your GitHub account
3. Use one of those emails in the git config above

## ✅ Verify It Worked

```powershell
git config user.name
git config user.email
```

## 🚀 Test It

Make a test commit to see the new name:

```powershell
git commit --allow-empty -m "Test: Verify new commit name"
git push origin merwin
```

Then check GitHub - the commit should show your new name!

## 🌐 Set Globally (All Repos)

If you want this name for **all git repositories** on your computer:

```powershell
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

## ⚠️ Important

- **Future commits** will use the new name ✅
- **Existing commits** on GitHub will still show "atmanartworks"
- To change existing commits, you'd need to rewrite git history (not recommended)

---

**Just update the name and email, then future commits will show correctly!**
