# RAG Backend Testing Guide

## Quick Test Results
✅ **7/8 tests passed** - System is mostly working!

## Automated Testing

Run the comprehensive test suite:
```powershell
python test_api.py
```

## Manual Testing Methods

### Method 1: Using Swagger UI (Recommended)

1. **Start the server:**
   ```powershell
   python app/main.py
   ```

2. **Open Swagger UI:**
   - Navigate to: http://localhost:8000/docs
   - Interactive API documentation with "Try it out" buttons

3. **Test endpoints:**
   - Click on any endpoint
   - Click "Try it out"
   - Fill in parameters
   - Click "Execute"
   - See the response

### Method 2: Using curl/PowerShell

#### Health Check
```powershell
curl http://localhost:8000/health
```

#### List Vaults
```powershell
curl http://localhost:8000/api/vault/list/test-user-123
```

#### Semantic Search
```powershell
curl -X POST "http://localhost:8000/api/search/semantic?query=test&user_id=test-user-123&top_k=5"
```

#### Chat Message
```powershell
curl -X POST http://localhost:8000/api/chat/message `
  -H "Content-Type: application/json" `
  -d '{\"conversation_id\":\"test-123\",\"message\":\"Hello\",\"user_id\":\"test-user-123\"}'
```

### Method 3: Using Python requests

```python
import requests

BASE_URL = "http://localhost:8000"

# Health check
response = requests.get(f"{BASE_URL}/health")
print(response.json())

# List vaults
response = requests.get(f"{BASE_URL}/api/vault/list/test-user-123")
print(response.json())
```

## Test Checklist

### ✅ Core Functionality (All Working)
- [x] Health endpoint
- [x] API documentation
- [x] Database connection
- [x] Embedding service (Mistral AI)
- [x] Environment variables configured

### ⚠️ Features to Test
- [ ] File upload (`/api/vault/upload`)
- [ ] Document embedding (`/api/vault/embed/{vault_id}`)
- [ ] Semantic search (requires embedded documents)
- [ ] Chat functionality (requires embedded documents)

## Testing File Upload

### Using Swagger UI:
1. Go to http://localhost:8000/docs
2. Find `POST /api/vault/upload`
3. Click "Try it out"
4. Upload a PDF or DOCX file
5. Set `user_id` query parameter
6. Execute

### Using curl:
```powershell
curl -X POST "http://localhost:8000/api/vault/upload?user_id=test-user-123" `
  -F "file=@test-document.pdf"
```

## Testing Complete Workflow

1. **Upload a document:**
   ```powershell
   curl -X POST "http://localhost:8000/api/vault/upload?user_id=test-user-123" `
     -F "file=@your-document.pdf"
   ```
   Note the `vault_id` from the response

2. **Embed the document:**
   ```powershell
   curl -X POST "http://localhost:8000/api/vault/embed/{vault_id}"
   ```

3. **Search for content:**
   ```powershell
   curl -X POST "http://localhost:8000/api/search/semantic?query=your+query&user_id=test-user-123&top_k=5"
   ```

4. **Chat with your documents:**
   ```powershell
   curl -X POST http://localhost:8000/api/chat/message `
     -H "Content-Type: application/json" `
     -d '{\"conversation_id\":\"conv-123\",\"message\":\"What is in my documents?\",\"user_id\":\"test-user-123\"}'
   ```

## Troubleshooting

### Server not starting?
- Check if port 8000 is available
- Ensure virtual environment is activated
- Check if all dependencies are installed

### Database connection errors?
- Verify `SUPABASE_URL` and `SUPABASE_KEY` in `.env`
- Check if Supabase project is active

### Embedding service errors?
- Verify `MISTRAL_API_KEY` in `.env`
- Test with: `python app/test_mistral.py`

### Endpoints returning 500 errors?
- Check server logs for detailed error messages
- Ensure database tables exist (vault, document_chunks, etc.)
- Verify Supabase RPC functions are set up

## Next Steps

1. ✅ Server is running
2. ✅ Core services are working
3. 📝 Test file upload functionality
4. 📝 Test document embedding
5. 📝 Test search and chat with real documents

