-- Fix Embedding Dimension: Update from 384 to 768 for Nomic model
-- Run this in Supabase SQL Editor

-- Step 1: Drop old constraint/index if exists
ALTER TABLE document_chunks 
DROP CONSTRAINT IF EXISTS document_chunks_embedding_check;

-- Step 2: Update embedding column to 768 dimensions
ALTER TABLE document_chunks 
ALTER COLUMN embedding TYPE vector(768);

-- Step 3: Recreate index for vector similarity search
-- Drop old index if exists
DROP INDEX IF EXISTS document_chunks_embedding_idx;

-- Create new index with proper dimensions
CREATE INDEX document_chunks_embedding_idx 
ON document_chunks 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Step 4: Verify (optional - run separately to check)
-- SELECT column_name, data_type, udt_name
-- FROM information_schema.columns 
-- WHERE table_name = 'document_chunks' 
-- AND column_name = 'embedding';

-- Step 5: Delete old chunks with wrong dimensions (optional)
-- WARNING: This deletes all existing chunks!
-- Only run this if you want to start fresh
-- DELETE FROM document_chunks;

