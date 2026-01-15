# Post-Deployment Checklist

## ✅ Changes Pushed to GitHub

All changes have been committed and pushed to the `merwin` branch:
- **89 files changed** with all the fixes
- Commit: `7768faa`

## 🔄 Auto-Deployment Status

### Vercel (Frontend)
- **Status**: Should auto-deploy within 1-2 minutes
- **Check**: Go to https://vercel.com/dashboard
- **Look for**: New deployment starting automatically
- **Build time**: Usually 1-2 minutes

### Render (Backend)
- **Status**: Should auto-deploy within 2-5 minutes
- **Check**: Go to https://dashboard.render.com
- **Look for**: New deployment starting automatically
- **Build time**: Usually 2-5 minutes (Python builds take longer)

## 📋 What to Check After Deployment

### 1. Vercel Deployment
1. Go to your Vercel dashboard
2. Find your project: `founderai-workspace`
3. Check the latest deployment:
   - Should show "Building..." then "Ready"
   - Check build logs for any errors
   - Verify the deployment URL is working

### 2. Render Deployment
1. Go to your Render dashboard
2. Find your backend service
3. Check the latest deployment:
   - Should show "Building..." then "Live"
   - Check build logs for any errors
   - Verify the service is running

### 3. Environment Variables

**Vercel (Frontend)**:
- `VITE_RAG_API_URL` → Should point to your Render backend URL
  - Example: `https://founderai-workspace.onrender.com`
- `VITE_SUPABASE_URL` → Your Supabase project URL
- `VITE_SUPABASE_ANON_KEY` → Your Supabase anon key

**Render (Backend)**:
- `OPENAI_API_KEY` → Your OpenAI API key
- `SUPABASE_URL` → Your Supabase project URL
- `SUPABASE_KEY` → Your Supabase service role key
- `SUPABASE_BUCKET` → Your storage bucket name (usually "vault")

## 🧪 Testing After Deployment

### Test 1: Frontend Loads
1. Visit your Vercel URL: `https://founderai-workspace-xi.vercel.app`
2. Should load without errors
3. Check browser console for any errors

### Test 2: Backend Health Check
1. Visit: `https://your-render-backend-url.onrender.com/health`
2. Should return: `{"status": "healthy"}`

### Test 3: Document Upload
1. Upload a PDF or DOCX file
2. Check console logs:
   - Should see "Embedding document..."
   - Should see "Successfully embedded document"
   - Should see "Set active document ID: [id]"
3. Check for success toast notification

### Test 4: Document Query
1. After uploading, ask: "explain this document"
2. Check console logs:
   - Should see "Sending message with active_document_id: [id]" (not null)
3. Should get a proper answer from the document

## 🐛 If Deployment Fails

### Vercel Build Fails
1. Check build logs in Vercel dashboard
2. Common issues:
   - Missing environment variables
   - Build command errors
   - Dependency installation failures
3. Fix and push again

### Render Build Fails
1. Check build logs in Render dashboard
2. Common issues:
   - Missing environment variables
   - Python dependency errors
   - Build command errors
3. Fix and push again

### Manual Redeploy
If auto-deploy doesn't trigger:
- **Vercel**: Go to deployment → "Redeploy"
- **Render**: Go to service → "Manual Deploy" → Select branch/commit

## 📝 Key Changes Deployed

### Frontend
- ✅ Fixed active document ID tracking
- ✅ Improved error handling
- ✅ Better logging for debugging

### Backend
- ✅ Text extraction during upload (not just embedding)
- ✅ Enhanced DOCX extraction (tables, headers, footers)
- ✅ Fixed CORS configuration
- ✅ Fixed Pydantic validation (Optional[str])
- ✅ Enhanced vague query detection
- ✅ Direct text injection for better answers

## 🎯 Expected Behavior After Deployment

1. **Upload Document**:
   - File uploads successfully
   - Text is extracted immediately
   - Document is embedded in FAISS
   - Active document ID is set

2. **Ask About Document**:
   - "explain this document" works
   - System uses text_content if available
   - Falls back to FAISS chunks if needed
   - Provides comprehensive answer

3. **Error Handling**:
   - Clear error messages
   - Graceful fallbacks
   - Detailed logging

## 📞 Next Steps

1. **Wait for deployments** (5-10 minutes total)
2. **Check both dashboards** for successful builds
3. **Test the full flow**:
   - Upload → Embed → Query
4. **Monitor logs** for any issues
5. **Report any problems** with deployment logs

---

**Note**: If you're using a different branch for production (like `main`), you may need to merge `merwin` into that branch first.
