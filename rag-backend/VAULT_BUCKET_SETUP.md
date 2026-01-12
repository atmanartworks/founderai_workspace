# Vault Storage Bucket Setup Guide

## Problem
You're getting this error when uploading files:
```
"Bucket not found"
```

## Solution: Create the Vault Bucket

### Option 1: Using Supabase Dashboard (Recommended)

1. **Go to your Supabase Dashboard**
   - Visit: https://supabase.com/dashboard
   - Select your project

2. **Navigate to Storage**
   - Click on "Storage" in the left sidebar
   - Click "New bucket"

3. **Create the Bucket**
   - **Name:** `vault`
   - **Public bucket:** ❌ Unchecked (Private)
   - **File size limit:** 50 MB (optional)
   - **Allowed MIME types:** (optional, or leave empty)
     - `application/pdf`
     - `application/msword`
     - `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
     - `text/plain`
     - `text/csv`
   - Click **"Create bucket"**

4. **Set up RLS Policies** (Important!)
   
   Go to SQL Editor and run this SQL:

   ```sql
   -- Users can view their own files
   CREATE POLICY "Users can view their own vault files"
   ON storage.objects FOR SELECT
   USING (
     bucket_id = 'vault' 
     AND (storage.foldername(name))[1] = 'user_' || auth.uid()::text
   );

   -- Users can upload their own files
   CREATE POLICY "Users can upload their own vault files"
   ON storage.objects FOR INSERT
   WITH CHECK (
     bucket_id = 'vault' 
     AND (storage.foldername(name))[1] = 'user_' || auth.uid()::text
   );

   -- Users can update their own files
   CREATE POLICY "Users can update their own vault files"
   ON storage.objects FOR UPDATE
   USING (
     bucket_id = 'vault' 
     AND (storage.foldername(name))[1] = 'user_' || auth.uid()::text
   );

   -- Users can delete their own files
   CREATE POLICY "Users can delete their own vault files"
   ON storage.objects FOR DELETE
   USING (
     bucket_id = 'vault' 
     AND (storage.foldername(name))[1] = 'user_' || auth.uid()::text
   );
   ```

   **Note:** For backend API usage (service role key), you may need to allow service role access:

   ```sql
   -- Allow service role to manage all vault files (for backend API)
   CREATE POLICY "Service role can manage vault files"
   ON storage.objects FOR ALL
   USING (bucket_id = 'vault')
   WITH CHECK (bucket_id = 'vault');
   ```

### Option 2: Using SQL Migration

If you're using Supabase migrations, run the migration file:
```sql
-- File: supabase/migrations/20251108052600_create_vault_bucket.sql
```

Run it via Supabase CLI:
```bash
supabase migration up
```

Or manually in the SQL Editor.

## Alternative: Make Bucket Public (For Testing Only)

⚠️ **Not recommended for production!**

If you just want to test quickly, you can:

1. Create the bucket as **Public**
2. Skip RLS policies (or set very permissive ones)

**For production, always use private buckets with proper RLS policies.**

## Verify Setup

After creating the bucket:

1. **Check bucket exists:**
   ```python
   from app.database import supabase
   buckets = supabase.storage.list_buckets()
   print([b.name for b in buckets])
   ```

2. **Test upload:**
   - Go to http://localhost:8000/docs
   - Try uploading a file via `/api/vault/upload`

## Troubleshooting

### Still getting "Bucket not found"?
- ✅ Check bucket name is exactly `vault` (lowercase)
- ✅ Check you're using the correct Supabase project
- ✅ Verify `SUPABASE_URL` and `SUPABASE_KEY` in `.env`

### Getting permission errors?
- ✅ Check RLS policies are created
- ✅ Verify service role key has permissions (for backend API)
- ✅ Check bucket is not restricted by file type limits

### Backend API needs full access?
If your backend uses a service role key (not user auth), you may need to:
1. Allow service role in RLS policies, OR
2. Temporarily disable RLS for testing (NOT recommended for production)

## Next Steps

After setting up the bucket:
1. ✅ Test file upload
2. ✅ Test document embedding
3. ✅ Test search functionality

