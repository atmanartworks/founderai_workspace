# 🔧 Add text_content Column to vault_files Table

## 🚨 The Problem

The `vault_files` table in Supabase doesn't have a `text_content` column, which is needed for:
- Document viewing when FAISS chunks aren't available
- Fallback chunk generation from extracted text

## ✅ Solution: Add Column via Supabase SQL Editor

### Step 1: Open Supabase SQL Editor

1. Go to: https://supabase.com/dashboard
2. Select your project
3. Click **"SQL Editor"** in the left sidebar
4. Click **"New query"**

### Step 2: Run This SQL

```sql
-- Add text_content column to vault_files table
ALTER TABLE vault_files 
ADD COLUMN IF NOT EXISTS text_content TEXT;

-- Add comment for documentation
COMMENT ON COLUMN vault_files.text_content IS 'Extracted text content from the document for viewing and fallback chunk generation';
```

### Step 3: Verify

Run this query to verify the column was added:

```sql
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'vault_files' 
AND column_name = 'text_content';
```

Should return: `text_content | text`

## 🎯 What This Does

- Adds `text_content` column to store extracted document text
- Allows document viewer to work even without FAISS chunks
- Enables automatic chunk generation from text_content

## ⚠️ Important Notes

- **Existing rows** will have `NULL` for `text_content`
- **New uploads** will populate `text_content` during file processing
- **Old documents** will need to be re-uploaded or re-processed to get text_content

## 🔄 After Adding Column

1. **Re-upload documents** to populate text_content
2. **Or** wait for new uploads to automatically extract text
3. **Document viewer** will now work with text_content fallback

---

**Run the SQL in Supabase SQL Editor to add the column!**
