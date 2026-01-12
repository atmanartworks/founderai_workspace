-- Check the actual dimension of the embedding column
-- Run this in Supabase SQL Editor

-- Method 1: Check column definition
SELECT 
    column_name, 
    data_type,
    udt_name,
    character_maximum_length
FROM information_schema.columns 
WHERE table_name = 'document_chunks' 
AND column_name = 'embedding';

-- Method 2: Check by trying to insert a test vector
-- This will show the expected dimension in the error if wrong
DO $$
BEGIN
    -- Try to insert a 768-dim vector (will fail if column is 384)
    INSERT INTO document_chunks (vault_id, user_id, content, chunk_index, tokens, embedding)
    VALUES (
        '00000000-0000-0000-0000-000000000000'::uuid,
        '00000000-0000-0000-0000-000000000000'::uuid,
        'test',
        0,
        10,
        array_fill(0.1::real, ARRAY[768])::vector
    );
    RAISE NOTICE 'Column accepts 768 dimensions';
    -- Clean up
    DELETE FROM document_chunks WHERE vault_id = '00000000-0000-0000-0000-000000000000'::uuid;
EXCEPTION WHEN OTHERS THEN
    IF SQLERRM LIKE '%expected 384 dimensions%' THEN
        RAISE NOTICE 'Column is set to 384 dimensions - needs update to 768';
    ELSIF SQLERRM LIKE '%expected 768 dimensions%' THEN
        RAISE NOTICE 'Column is already set to 768 dimensions - no update needed';
    ELSE
        RAISE NOTICE 'Error: %', SQLERRM;
    END IF;
END $$;

-- Method 3: Check pg_attribute directly (most reliable)
SELECT 
    attname as column_name,
    atttypid::regtype as type_name
FROM pg_attribute
WHERE attrelid = 'document_chunks'::regclass
AND attname = 'embedding';

