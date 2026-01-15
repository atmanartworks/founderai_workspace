# Restart Backend Server

After making changes to fix CORS and error handling, you need to restart the backend server.

## Steps

1. **Stop the current backend server** (if running):
   - Press `Ctrl+C` in the terminal where the server is running

2. **Start the backend server**:
   ```bash
   cd rag-backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Verify it's running**:
   - Open `http://127.0.0.1:8000/health` in your browser
   - Should return: `{"status": "healthy"}`

4. **Test document upload**:
   - Try uploading a PDF or DOCX file in the frontend
   - Check the backend terminal for detailed logs
   - Errors should now be more descriptive

## What Was Fixed

1. **CORS Configuration**: Fixed mixed origins issue (can't mix `"*"` with specific origins)
2. **Error Handling**: Added comprehensive try-catch blocks and logging
3. **Better Error Messages**: More descriptive errors for debugging

## Troubleshooting

If you still see CORS errors:
- Make sure the backend is running on port 8000
- Check that the frontend is using `http://127.0.0.1:8000` (not `localhost`)
- Clear browser cache and hard refresh (Ctrl+Shift+R)

If you see 500 errors:
- Check the backend terminal logs for detailed error messages
- Verify your Supabase credentials are correct in `.env`
- Ensure the `text_content` column exists (see `ADD_TEXT_CONTENT_COLUMN.md`)
