# Deploy Changes to Vercel (Frontend) and Render (Backend)

## Summary of Changes Made

### Frontend Changes (Vercel)
1. **Fixed active document ID tracking** - Documents are now properly tracked when uploaded
2. **Improved error handling** - Better error messages for embedding failures
3. **Enhanced logging** - Console logs show document upload and embedding status
4. **Fixed state management** - Active document ID is now properly passed to backend

### Backend Changes (Render)
1. **Enhanced DOCX extraction** - Now extracts tables, headers, and footers
2. **Text extraction during upload** - Text is extracted immediately, not just during embedding
3. **Improved CORS configuration** - Fixed CORS issues for localhost and production
4. **Better error handling** - Comprehensive logging and error messages
5. **Fixed Pydantic validation** - Changed `str = None` to `Optional[str]` for proper null handling
6. **Enhanced vague query detection** - Better detection of "explain this document" queries
7. **Direct text injection** - Uses full document text when available for better answers

## Deployment Steps

### 1. Commit All Changes

```bash
# Stage all changes
git add .

# Commit with descriptive message
git commit -m "Fix document upload and embedding: Add text extraction during upload, fix active document tracking, improve CORS, enhance DOCX extraction"

# Push to GitHub
git push origin main
```

### 2. Vercel Auto-Deploy (Frontend)

Vercel should automatically deploy when you push to GitHub:
- Go to your Vercel dashboard
- Check the deployment status
- Wait for build to complete (usually 1-2 minutes)

### 3. Render Auto-Deploy (Backend)

Render should automatically deploy when you push to GitHub:
- Go to your Render dashboard
- Check the deployment status
- Wait for build to complete (usually 2-5 minutes)

### 4. Verify Deployment

After both deployments complete:

1. **Test Frontend (Vercel)**:
   - Visit your Vercel URL
   - Upload a document
   - Check console logs for "Set active document ID"
   - Ask "explain this document"

2. **Test Backend (Render)**:
   - Check Render logs for any errors
   - Verify environment variables are set correctly
   - Test the `/health` endpoint

## Important Files Changed

### Frontend (src/)
- `src/pages/Chat.tsx` - Fixed active document tracking
- `src/services/ragApi.ts` - Improved error handling

### Backend (rag-backend/)
- `rag-backend/app/routes/vault.py` - Text extraction during upload
- `rag-backend/app/routes/embeddings.py` - Better error handling and logging
- `rag-backend/app/routes/chat.py` - Fixed Pydantic models, enhanced query handling
- `rag-backend/app/services/text_extraction.py` - Enhanced DOCX extraction
- `rag-backend/app/main.py` - Fixed CORS configuration

## Environment Variables to Check

### Vercel (Frontend)
- `VITE_RAG_API_URL` - Should point to your Render backend URL
- `VITE_SUPABASE_URL` - Your Supabase project URL
- `VITE_SUPABASE_ANON_KEY` - Your Supabase anon key

### Render (Backend)
- `OPENAI_API_KEY` - Your OpenAI API key
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_KEY` - Your Supabase service role key
- `SUPABASE_BUCKET` - Your Supabase storage bucket name

## Troubleshooting

If deployments fail:

1. **Check build logs** in Vercel/Render dashboards
2. **Verify environment variables** are set correctly
3. **Check for syntax errors** in the code
4. **Ensure all dependencies** are in package.json/requirements.txt

## Manual Deployment (if auto-deploy fails)

### Vercel
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

### Render
- Go to Render dashboard
- Click "Manual Deploy" on your service
- Select the branch/commit to deploy
