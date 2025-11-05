-- Add folder support to vault_files table
ALTER TABLE public.vault_files
ADD COLUMN is_folder boolean NOT NULL DEFAULT false,
ADD COLUMN parent_folder_id uuid REFERENCES public.vault_files(id) ON DELETE CASCADE;

-- Create index for faster folder queries
CREATE INDEX idx_vault_files_parent_folder ON public.vault_files(parent_folder_id);
CREATE INDEX idx_vault_files_user_folder ON public.vault_files(user_id, parent_folder_id);

-- Update RLS policy for folders
CREATE POLICY "Users can update their own files and folders"
ON public.vault_files
FOR UPDATE
USING (auth.uid() = user_id);