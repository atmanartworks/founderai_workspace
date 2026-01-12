# 🗄️ Supabase Configuration

This folder contains all Supabase-related configuration files, schemas, and SQL scripts.

## 📄 SQL Scripts

### Main Scripts
- [supabase_storage_policies.sql](./supabase_storage_policies.sql) - Storage bucket RLS policies for the vault bucket
- [supabase_full.sql](./supabase_full.sql) - Complete database schema and setup
- [fix_existing_users.sql](./fix_existing_users.sql) - Script to fix existing user records

### Migrations
Located in `migrations/` folder:
- `20251108052600_create_vault_bucket.sql` - Create vault storage bucket
- `20251105110251_5e519c54-2de5-4452-a7da-5f4a4811dea4.sql`
- `20251105105527_8e0c3e8d-36cd-44eb-b9e4-75cdcda5bfa8.sql`
- `20251105082118_3ee261ab-fa4e-4253-aa51-52a913296ce6.sql`
- `20251105081120_5efae0ce-ea34-4cec-a459-a85bda7a8876.sql`
- `20251105075034_2f86ea7e-d773-482e-b767-f2da675184e4.sql`

## 🗂️ Database Tables

### Core Tables
- `profiles` - User profile information
- `conversations` - Chat conversation metadata
- `messages` - Individual chat messages
- `vault_files` - File metadata for document vault
- `document_chunks` - Text chunks with embeddings for RAG

### Storage Buckets
- `vault` - Main storage bucket for user files

## 🔐 Row Level Security (RLS)

All tables and storage buckets have RLS policies enabled to ensure:
- Users can only access their own data
- Proper authentication is required
- Data isolation between users

## 🚀 Setup Instructions

1. Run `supabase_full.sql` in Supabase SQL Editor to create all tables
2. Run `supabase_storage_policies.sql` to set up storage bucket policies
3. Ensure migrations are applied in order (if using Supabase CLI)

## 📚 Related Documentation

See `/docs/` folder for application-level documentation and guides.

