-- Create storage bucket for vault (document storage)
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
  'vault',
  'vault',
  false, -- Private bucket
  52428800, -- 50 MB file size limit
  ARRAY['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain', 'text/csv']
)
ON CONFLICT (id) DO NOTHING;

-- Create RLS policies for vault bucket
-- Note: Backend API uses service role key, so these policies allow service role access
-- For user-based access, uncomment the user-specific policies below

-- Allow service role (backend API) full access to vault bucket
CREATE POLICY "Service role can manage vault files"
ON storage.objects FOR ALL
USING (bucket_id = 'vault')
WITH CHECK (bucket_id = 'vault');

-- Optional: User-specific policies (for frontend direct access)
-- Uncomment if you want users to access their files directly from frontend

-- CREATE POLICY "Users can view their own vault files"
-- ON storage.objects FOR SELECT
-- USING (
--   bucket_id = 'vault' 
--   AND (storage.foldername(name))[1] = 'user_' || auth.uid()::text
-- );

-- CREATE POLICY "Users can upload their own vault files"
-- ON storage.objects FOR INSERT
-- WITH CHECK (
--   bucket_id = 'vault' 
--   AND (storage.foldername(name))[1] = 'user_' || auth.uid()::text
-- );

-- CREATE POLICY "Users can update their own vault files"
-- ON storage.objects FOR UPDATE
-- USING (
--   bucket_id = 'vault' 
--   AND (storage.foldername(name))[1] = 'user_' || auth.uid()::text
-- );

-- CREATE POLICY "Users can delete their own vault files"
-- ON storage.objects FOR DELETE
-- USING (
--   bucket_id = 'vault' 
--   AND (storage.foldername(name))[1] = 'user_' || auth.uid()::text
-- );

