# Add text_content Column to vault_files Table

If you're getting "No usable text found" errors for DOCX files, you may need to add the `text_content` column to store extracted text.

## SQL Migration

Run this in your Supabase SQL Editor:

```sql
-- Add text_content column to vault_files table
ALTER TABLE vault_files 
ADD COLUMN IF NOT EXISTS text_content TEXT;

-- Add comment for documentation
COMMENT ON COLUMN vault_files.text_content IS 'Extracted text content from the document for direct access without re-extraction';
```

## Why This Helps

1. **Faster Access**: Once text is extracted, it's stored in the database
2. **Active Document Context**: The conversation-aware system can use `text_content` directly
3. **Better Error Messages**: System can detect if extraction failed vs. document is empty

## After Adding Column

1. Re-embed existing DOCX files to populate `text_content`
2. New uploads will automatically save extracted text
