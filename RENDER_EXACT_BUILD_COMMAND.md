# ⚠️ IMPORTANT: Exact Build Command for Render

## 🚨 The Problem

The build command in Render has extra text `(no cd!)` which is causing a syntax error. That was just a comment in my documentation, not part of the actual command!

## ✅ CORRECT Build Command

**Copy this EXACTLY (no comments, no extra text):**

```
pip install -r requirements-railway.txt
```

**That's it!** Just that one line, nothing else.

## ✅ Complete Render Settings

**Root Directory:**
```
rag-backend
```

**Build Command:**
```
pip install -r requirements-railway.txt
```

**Start Command:**
```
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## ✅ How to Fix in Render

1. **Render Dashboard** → Your service → **Settings**
2. **Build & Deploy** section
3. **Build Command** field - **DELETE everything** and paste:
   ```
   pip install -r requirements-railway.txt
   ```
4. **Make sure there's NO extra text** like "(no cd!)" or comments
5. **Save Changes**
6. **Manual Deploy** → **Clear build cache & deploy**

## 🎯 What Happened

You copied the command from my documentation which had `(no cd!)` as a comment. That comment got included in the build command, causing a bash syntax error.

**The actual command is just:**
```
pip install -r requirements-railway.txt
```

---

**Update Render settings with the exact command above (no comments)!**
