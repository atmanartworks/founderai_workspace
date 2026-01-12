-- Update Embedding Column from 384 to 768 Dimensions
-- Run this in Supabase SQL Editor

-- IMPORTANT: Delete old chunks first (they have 384 dimensions)
-- This will clear all existing embeddings
DELETE FROM document_chunks;

-- Drop existing indexes
DROP INDEX IF EXISTS document_chunks_embedding_idx;
DROP INDEX IF EXISTS document_chunks_embedding_idx1;

-- Update the embedding column to 768 dimensions
ALTER TABLE document_chunks 
ALTER COLUMN embedding TYPE vector(768);

-- Recreate the vector index for similarity search
CREATE INDEX document_chunks_embedding_idx 
ON document_chunks 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Verify the update worked
SELECT 
    attname as column_name,
    format_type(atttypid, atttypmod) as full_type
FROM pg_attribute
WHERE attrelid = 'document_chunks'::regclass
AND attname = 'embedding';

-- Expected result: should show "vector(768)"

