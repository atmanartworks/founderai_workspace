-- Create a table to track file metadata
CREATE TABLE IF NOT EXISTS public.vault_files (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL,
  storage_path TEXT NOT NULL,
  original_name TEXT NOT NULL,
  file_size BIGINT DEFAULT 0,
  content_type TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(storage_path)
);

-- Enable RLS
ALTER TABLE public.vault_files ENABLE ROW LEVEL SECURITY;

-- Create policies for user access
CREATE POLICY "Users can view their own files"
  ON public.vault_files
  FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own files"
  ON public.vault_files
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own files"
  ON public.vault_files
  FOR DELETE
  USING (auth.uid() = user_id);