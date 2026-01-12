-- =============================================
-- Fix Existing Users Script
-- Run this in Supabase SQL Editor
-- =============================================

-- 1. Check current email confirmation setting
SELECT * FROM auth.config 
WHERE parameter = 'enable_email_confirmations';

-- 2. View all users and their confirmation status
SELECT 
  id,
  email,
  email_confirmed_at,
  raw_user_meta_data->>'full_name' as full_name,
  created_at,
  CASE 
    WHEN email_confirmed_at IS NOT NULL THEN 'Confirmed'
    ELSE 'Not Confirmed'
  END as status
FROM auth.users 
ORDER BY created_at DESC;

-- 3. View profiles and check if they were created
SELECT 
  p.id,
  p.full_name,
  p.created_at,
  u.email
FROM profiles p
FULL OUTER JOIN auth.users u ON u.id = p.id
ORDER BY p.created_at DESC;

-- =============================================
-- FIX COMMANDS (uncomment to run)
-- =============================================

-- 4. Manually confirm all unconfirmed users
-- UNCOMMENT BELOW TO RUN:
-- UPDATE auth.users 
-- SET email_confirmed_at = NOW() 
-- WHERE email_confirmed_at IS NULL;

-- 5. Create missing profiles for users without them
-- UNCOMMENT BELOW TO RUN:
-- INSERT INTO profiles (id, full_name)
-- SELECT 
--   u.id, 
--   u.raw_user_meta_data->>'full_name' AS full_name
-- FROM auth.users u
-- LEFT JOIN profiles p ON p.id = u.id
-- WHERE p.id IS NULL
-- ON CONFLICT (id) DO NOTHING;

-- 6. Update profiles with missing full_name
-- UNCOMMENT BELOW TO RUN:
-- UPDATE profiles p
-- SET full_name = u.raw_user_meta_data->>'full_name'
-- FROM auth.users u
-- WHERE p.id = u.id 
-- AND (p.full_name IS NULL OR p.full_name = '')
-- AND u.raw_user_meta_data->>'full_name' IS NOT NULL;

-- =============================================
-- VERIFICATION
-- =============================================

-- 7. Verify all users now have profiles
SELECT 
  COUNT(*) as total_users,
  COUNT(p.id) as users_with_profiles,
  COUNT(*) - COUNT(p.id) as missing_profiles
FROM auth.users u
LEFT JOIN profiles p ON p.id = u.id;

-- 8. Show users with their profile info
SELECT 
  u.email,
  u.email_confirmed_at,
  p.full_name,
  p.created_at as profile_created_at
FROM auth.users u
LEFT JOIN profiles p ON p.id = u.id
ORDER BY u.created_at DESC;

