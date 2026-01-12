# How to Add OPENAI_API_KEY to .env File

## Problem

The `.env` file is missing `OPENAI_API_KEY`. The system requires this to generate LLM responses.

## Solution

Add the following line to your `.env` file in the `rag-backend` directory:

```env
OPENAI_API_KEY=sk-your-actual-api-key-here
```

## Steps

1. **Open the `.env` file** in `rag-backend/.env`

2. **Add this line** (replace with your actual API key):
   ```env
   OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

3. **Save the file**

4. **Restart the server**:
   ```bash
   # Stop the current server (Ctrl+C)
   # Then restart:
   uvicorn app.main:app --reload
   ```

## Example .env File

Your `.env` file should look like this:

```env
SUPABASE_URL=https://axaxcynwwpndnvdbjbow.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_BUCKET=vault
MISTRAL_API_KEY=your-mistral-key
LOCAL_EMBEDDING_MODEL=nomic-ai/nomic-embed-text-v1
LOCAL_TEXT_MODEL=...
GROQ_API_KEY=your-groq-key
DEBUG=true
PORT=8000

# Add this line:
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-3.5-turbo
```

## Getting Your OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)
5. Paste it in your `.env` file

## Important Notes

- ✅ **No spaces** around the `=` sign
- ✅ **No quotes** needed (unless the key itself contains special characters)
- ✅ **One key per line**
- ✅ **Don't commit** `.env` to git (it should be in `.gitignore`)

## Verify It's Working

After adding the key and restarting, you should see in the logs:
```
✅ Loaded .env from: C:\...\rag-backend\.env
✅ OPENAI_API_KEY loaded (length: 51)
✅ OpenAI LLM Provider initialized with model: gpt-3.5-turbo
```

## Optional: OPENAI_MODEL

You can also specify which OpenAI model to use:

```env
OPENAI_API_KEY=sk-your-key
OPENAI_MODEL=gpt-3.5-turbo    # Default
# or
OPENAI_MODEL=gpt-4
# or
OPENAI_MODEL=gpt-4o
```

