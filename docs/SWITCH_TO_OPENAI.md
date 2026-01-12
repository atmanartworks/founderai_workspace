# 🔄 Switch from Groq to OpenAI

## Quick Setup

### Step 1: Install OpenAI Package

```powershell
pip install openai
```

Or it will be installed automatically when you run:
```powershell
pip install -r requirements.txt
```

### Step 2: Add OpenAI API Key to `.env`

Add this line to your `.env` file:

```env
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-3.5-turbo
```

**Optional:** You can also specify a different model:
- `gpt-3.5-turbo` (default, cheaper, fast)
- `gpt-4` (better quality, more expensive)
- `gpt-4-turbo-preview` (latest GPT-4)
- `gpt-4o` (fastest GPT-4)

### Step 3: Restart Server

The server will automatically use OpenAI if `OPENAI_API_KEY` is set.

```powershell
# Stop current server (Ctrl+C)
# Start again
uvicorn app.main:app --reload
```

---

## How It Works

The system now uses **priority-based selection**:

1. **OpenAI** (if `OPENAI_API_KEY` is set) ✅ **Priority**
2. **Groq** (if `GROQ_API_KEY` is set, fallback)
3. **None** (if neither is set)

---

## Configuration Options

### Use OpenAI Only

```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-3.5-turbo
# Don't set GROQ_API_KEY (or remove it)
```

### Use Groq Only

```env
GROQ_API_KEY=gsk-...
GROQ_MODEL=llama-3.1-8b-instant
# Don't set OPENAI_API_KEY (or remove it)
```

### Use Both (OpenAI priority)

```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-3.5-turbo
GROQ_API_KEY=gsk-...
GROQ_MODEL=llama-3.1-8b-instant
```

If OpenAI fails, it will automatically fallback to Groq.

---

## Model Comparison

| Provider | Model | Speed | Quality | Cost |
|----------|-------|-------|---------|------|
| OpenAI | gpt-3.5-turbo | Fast | Good | $ |
| OpenAI | gpt-4 | Medium | Excellent | $$$ |
| OpenAI | gpt-4o | Fast | Excellent | $$ |
| Groq | llama-3.1-8b-instant | Very Fast | Good | Free |

---

## Verify It's Working

### Check Server Logs

When you start the server, you should see:
```
INFO: Using OpenAI with model: gpt-3.5-turbo
```

### Test Chat Endpoint

1. Go to http://localhost:8000/docs
2. Find `POST /api/chat/message`
3. Test with a message
4. Should get response from OpenAI

---

## Troubleshooting

### "OPENAI_API_KEY not found"
- Check `.env` file has `OPENAI_API_KEY=sk-...`
- Make sure `.env` is in `rag-backend` directory
- Restart server after adding key

### "No module named 'openai'"
- Run: `pip install openai`
- Or: `pip install -r requirements.txt`

### Still using Groq?
- Check server logs to see which provider initialized
- Make sure `OPENAI_API_KEY` is set correctly
- Remove `GROQ_API_KEY` if you want OpenAI only

### API Errors
- Verify API key is valid
- Check you have credits/quota
- Try a different model if one fails

---

## Cost Considerations

### OpenAI Pricing (as of 2024)
- **gpt-3.5-turbo**: ~$0.0015 per 1K tokens (input), $0.002 per 1K tokens (output)
- **gpt-4**: ~$0.03 per 1K tokens (input), $0.06 per 1K tokens (output)
- **gpt-4o**: ~$0.005 per 1K tokens (input), $0.015 per 1K tokens (output)

### Groq Pricing
- **Free tier available** (with rate limits)
- Good for development/testing

**Recommendation:** Use `gpt-3.5-turbo` for cost-effective production, or Groq for free development.

---

## Complete `.env` Example

```env
# Supabase
SUPABASE_URL=https://axaxcynwwpndnvdbjbow.supabase.co
SUPABASE_KEY=your-key-here
SUPABASE_BUCKET=vault

# OpenAI (for chat/LLM)
OPENAI_API_KEY=sk-your-openai-key-here
OPENAI_MODEL=gpt-3.5-turbo

# Embedding Model (local, free)
LOCAL_EMBEDDING_MODEL=nomic-ai/nomic-embed-text-v1

# Optional: Groq (fallback)
# GROQ_API_KEY=gsk-...
# GROQ_MODEL=llama-3.1-8b-instant
```

---

**After adding `OPENAI_API_KEY` to `.env`, restart the server and it will use OpenAI!** 🚀

