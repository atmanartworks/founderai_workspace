# 🌐 Testing Endpoints in Browser

## Quick Access

### 1. **Interactive API Documentation (Swagger UI)** - Easiest Method! ⭐

Open in your browser:
```
http://localhost:8000/docs
```

**Features:**
- ✅ See all available endpoints
- ✅ Test endpoints directly in the browser
- ✅ View request/response schemas
- ✅ No need to write code or use curl

**How to use:**
1. Open http://localhost:8000/docs
2. Click on any endpoint (e.g., `GET /health`)
3. Click "Try it out"
4. Click "Execute"
5. See the response below

---

### 2. **Alternative API Docs (ReDoc)**

Open in your browser:
```
http://localhost:8000/redoc
```

Beautiful documentation interface with all endpoints listed.

---

## Direct Browser Testing (GET Endpoints Only)

### Health Check
```
http://localhost:8000/health
```

**Expected Response:**
```json
{"status": "healthy"}
```

---

### List All Vault Files
```
http://localhost:8000/api/vault/list
```

**Expected Response:**
```json
{
  "files": [
    {
      "id": "...",
      "user_id": "...",
      "original_name": "...",
      "storage_path": "...",
      ...
    }
  ]
}
```

---

## Testing POST Endpoints (Requires Tools)

POST endpoints (like `/api/chat/message`, `/api/vault/upload`) need to send data, so you can't test them directly by typing a URL. Use one of these methods:

### Method 1: Swagger UI (Recommended) ✅

1. Go to http://localhost:8000/docs
2. Find the endpoint (e.g., `POST /api/chat/message`)
3. Click "Try it out"
4. Fill in the request body:
   ```json
   {
     "conversation_id": null,
     "message": "Hello, what can you help me with?",
     "user_id": "test-user-123",
     "top_k": 5
   }
   ```
5. Click "Execute"
6. See the response

---

### Method 2: Browser Extension

Install a browser extension like:
- **REST Client** (Chrome/Edge)
- **Talend API Tester** (Chrome)
- **Postman** (Desktop app)

Then you can send POST requests with JSON bodies.

---

### Method 3: JavaScript Console (In Browser)

Open browser console (F12) and run:

```javascript
// Test chat endpoint
fetch('http://localhost:8000/api/chat/message', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    conversation_id: null,
    message: "Hello, what can you help me with?",
    user_id: "test-user-123",
    top_k: 5
  })
})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error('Error:', error));
```

---

## Available Endpoints

### Health & Info
- `GET /health` - Server health check
- `GET /docs` - Swagger UI documentation
- `GET /redoc` - ReDoc documentation

### Vault (File Management)
- `GET /api/vault/list` - List all files
- `POST /api/vault/upload` - Upload a file (needs form data)

### Embeddings
- `POST /api/embeddings/embed-document/{vault_id}` - Embed a document
- `GET /api/embeddings/fix-storage-paths` - Check storage paths
- `POST /api/embeddings/auto-reupload-missing` - Re-upload missing files

### Chat
- `POST /api/chat/message` - Send a chat message

### Search
- `POST /api/search/semantic-search` - Semantic search

---

## Step-by-Step: Testing Chat Endpoint

### Using Swagger UI:

1. **Start the server** (if not running):
   ```powershell
   uvicorn app.main:app --reload
   ```

2. **Open Swagger UI**:
   - Go to: http://localhost:8000/docs

3. **Find the Chat Endpoint**:
   - Scroll to `POST /api/chat/message`
   - Click on it to expand

4. **Click "Try it out"**

5. **Fill in the request body**:
   ```json
   {
     "conversation_id": null,
     "message": "What is artificial intelligence?",
     "user_id": "test-user-123",
     "top_k": 5
   }
   ```

6. **Click "Execute"**

7. **View the response**:
   ```json
   {
     "response": "AI response here...",
     "sources": ["file1.pdf", "file2.txt"],
     "message_id": "...",
     "conversation_id": "..."
   }
   ```

---

## Step-by-Step: Testing File Upload

### Using Swagger UI:

1. **Go to**: http://localhost:8000/docs

2. **Find**: `POST /api/vault/upload`

3. **Click "Try it out"**

4. **Fill in parameters**:
   - `user_id`: `test-user-123`
   - `folder`: (leave empty or specify a folder)
   - `file`: Click "Choose File" and select a PDF/DOCX/TXT file

5. **Click "Execute"**

6. **View response**:
   ```json
   {
     "success": true,
     "vault_id": "...",
     "storage_path": "test-user-123/filename.pdf"
   }
   ```

---

## Troubleshooting

### "Connection Refused" Error
- Make sure the server is running
- Check the URL is correct: `http://localhost:8000`
- Try `http://127.0.0.1:8000` instead

### CORS Errors
- The server has CORS enabled for all origins
- If you still get CORS errors, check the server logs

### 404 Not Found
- Make sure you're using the correct endpoint path
- Check the `/docs` page to see all available endpoints

### 500 Internal Server Error
- Check the server terminal for error messages
- Make sure your `.env` file is configured correctly
- Verify database connection

---

## Quick Test Checklist

- [ ] Server is running (`uvicorn app.main:app --reload`)
- [ ] Open http://localhost:8000/health - Should return `{"status": "healthy"}`
- [ ] Open http://localhost:8000/docs - Should show Swagger UI
- [ ] Test `GET /api/vault/list` - Should return list of files (may be empty)
- [ ] Test `POST /api/chat/message` via Swagger UI

---

## Pro Tips

1. **Bookmark Swagger UI**: http://localhost:8000/docs - It's your best friend!
2. **Use Swagger for POST requests**: Much easier than curl or Postman
3. **Check server logs**: The terminal shows all requests and errors
4. **Test health first**: Always verify `/health` works before testing other endpoints

---

**Happy Testing! 🚀**

