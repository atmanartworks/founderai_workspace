-- Supabase Storage RLS Policies for 'vault' bucket
-- Run these in your Supabase SQL Editor

-- Policy 1: Allow authenticated users to upload to their own user_id folder
CREATE POLICY "Allow users to upload to own folder"
ON storage.objects
FOR INSERT
TO authenticated
WITH CHECK (
  bucket_id = 'vault' AND
  (auth.uid())::text = (storage.foldername(name))[1]
);

-- Policy 2: Allow authenticated users to read from their own user_id folder
CREATE POLICY "Allow users to read own folder"
ON storage.objects
FOR SELECT
TO authenticated
USING (
  bucket_id = 'vault' AND
  (auth.uid())::text = (storage.foldername(name))[1]
);

-- Policy 3: Allow authenticated users to update files in their own folder
CREATE POLICY "Allow users to update own files"
ON storage.objects
FOR UPDATE
TO authenticated
USING (
  bucket_id = 'vault' AND
  (auth.uid())::text = (storage.foldername(name))[1]
);

-- Policy 4: Allow authenticated users to delete files in their own folder
CREATE POLICY "Allow users to delete own files"
ON storage.objects
FOR DELETE
TO authenticated
USING (
  bucket_id = 'vault' AND
  (auth.uid())::text = (storage.foldername(name))[1]
);

