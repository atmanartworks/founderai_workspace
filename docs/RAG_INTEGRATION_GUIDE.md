# RAG Backend Integration Guide

## 🎉 Integration Complete!

Your frontend is now connected to the RAG backend for intelligent document-based chat.

## 📁 Files Created/Modified

### ✅ New Files:
1. **`src/services/ragApi.ts`** - RAG Backend API client
   - `sendMessage()` - Send chat messages with RAG context
   - `uploadFile()` - Upload files to vault
   - `embedDocument()` - Trigger document embedding
   - `listFiles()` - List vault files
   - `healthCheck()` - Check backend health

### ✅ Modified Files:
2. **`src/pages/Chat.tsx`** - Updated chat handler
   - Integrated RAG API for intelligent responses
   - Auto-uploads files to vault
   - Auto-embeds documents after upload
   - Shows sources with AI responses

## 🚀 Setup Instructions

### 1. Create Environment File

Create a `.env` file in the **root** of your frontend project:

```bash
# .env
VITE_RAG_API_URL=http://127.0.0.1:8000
```

### 2. Start the RAG Backend

In a **separate terminal**, navigate to the `rag-backend` folder:

```powershell
cd rag-backend
.\start.ps1
```

Or manually:

```powershell
cd rag-backend
.\venv\Scripts\activate
uvicorn app.main:app --reload
```

**Backend should be running at:** `http://127.0.0.1:8000`

### 3. Start the Frontend

In your main project directory:

```bash
npm run dev
```

**Frontend should be running at:** `http://localhost:5173`

## 🎯 How It Works

### Chat Flow:
1. User sends a message in the chat
2. **File Upload** (if files attached):
   - Files are uploaded to RAG vault via `/api/vault/upload`
   - Documents are automatically embedded via `/api/embeddings/embed-document/{vault_id}`
3. **Message Processing**:
   - User message is sent to `/api/chat/message`
   - Backend embeds the query
   - Searches relevant document chunks (vector similarity)
   - Generates context-aware response using Groq LLM
4. **Display Response**:
   - AI response is displayed with source files
   - Sources show actual filenames (e.g., "report.pdf")

## 🔑 Key Features

✅ **RAG-Powered Chat** - AI answers based on your documents
✅ **Auto File Upload** - Drag & drop files to add to knowledge base
✅ **Auto Embedding** - Documents are automatically processed
✅ **Source Attribution** - See which documents were used
✅ **Multi-format Support** - PDF, DOCX, TXT, HTML, JSON, MD
✅ **User-scoped** - Each user has their own vault

## 🧪 Testing the Integration

### Test 1: Upload a Document
1. Go to `/chat` page
2. Attach a PDF/DOCX file in the chat
3. Type a message related to the document
4. You should see the file being uploaded and embedded
5. AI should respond with relevant information

### Test 2: Ask Questions
After uploading documents, try queries like:
- "What is this document about?"
- "Summarize the key points"
- "What are the main findings?"

### Test 3: Check Sources
- AI responses should include "📚 Sources" at the bottom
- Sources show actual filenames

## 🔧 Configuration

### Change Backend URL
Edit `.env`:
```bash
VITE_RAG_API_URL=http://your-backend-url:port
```

### Adjust Search Results
In `Chat.tsx`, modify the `top_k` parameter:
```typescript
const response = await ragApi.sendMessage({
  conversation_id: currentConversation.id,
  message: content,
  user_id: user.id,
  top_k: 5, // ← Change this (default: 5 chunks)
});
```

## 🐛 Troubleshooting

### Issue: "Failed to send message"
**Solution:**
- Check if RAG backend is running: `http://127.0.0.1:8000/health`
- Verify `.env` has correct `VITE_RAG_API_URL`
- Check browser console for CORS errors

### Issue: "No relevant documents found"
**Solution:**
- Upload and embed documents first
- Check if embeddings were created: `http://127.0.0.1:8000/docs` → Try `/api/vault/list`
- Re-embed documents if needed

### Issue: "PDF extraction shows structure instead of text"
**Solution:**
- Already fixed with `pdfplumber`
- Re-embed the document: POST to `/api/embeddings/embed-document/{vault_id}`

## 📚 API Endpoints Available

### Chat:
- `POST /api/chat/message` - Send chat message

### Vault:
- `POST /api/vault/upload` - Upload file
- `GET /api/vault/list` - List files

### Embeddings:
- `POST /api/embeddings/embed-document/{vault_id}` - Embed document
- `GET /api/embeddings/fix-storage-paths` - Fix storage paths
- `POST /api/embeddings/auto-reupload-missing` - Re-upload missing files

### Search:
- `POST /api/search/semantic-search` - Semantic search

### Health:
- `GET /health` - Backend health check

## 🎨 UI Features

- **File Upload**: Drag & drop or click to upload
- **Real-time Status**: Toast notifications for upload/embedding
- **Source Display**: See which documents AI used
- **Error Handling**: Clear error messages if backend is down

## 🚀 Next Steps

1. **Add Dashboard Integration**: Show vault files in UI
2. **File Management**: Delete/rename vault files
3. **Advanced Search**: Direct document search interface
4. **Analytics**: Track which documents are used most
5. **Settings**: Configure chunk size, model, etc.

## 💡 Tips

- Upload documents before asking questions about them
- Be specific in your queries for better results
- Check sources to verify AI responses
- Keep backend running while using the chat

---

**Your RAG-powered chat is ready! 🎉**

Start by uploading some documents and asking questions about them!

