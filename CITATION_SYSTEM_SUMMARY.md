# 📚 Interactive Citation System

## ✨ Overview

Implemented a complete citation-aware system that generates answers with interactive, clickable citations referencing specific document chunks.

## 🎯 Features

### Backend (Python/FastAPI)

1. **Citation Service** (`rag-backend/app/services/citation_service.py`)
   - Generates answers with inline citations using LLM
   - Creates citation metadata for each chunk
   - Tracks which chunks are used in answers

2. **Chat Route Updates** (`rag-backend/app/routes/chat.py`)
   - Integrated citation generation into chat flow
   - Returns citation metadata with responses
   - Handles fallback when citations can't be generated

3. **Response Model** (`ChatResponse`)
   - Added `citations` field with citation metadata
   - Each citation includes:
     - `citation_id`: Sequential number [1], [2], etc.
     - `source_document_id`: vault_id
     - `source_document_name`: filename
     - `chunk_id`: chunk index
     - `quoted_text`: Excerpt from chunk
     - `chunk_content`: Full chunk content
     - `score`: Relevance score

### Frontend (React/TypeScript)

1. **ChatBubble Component** (`src/components/ChatBubble.tsx`)
   - Parses citation markers `[1]`, `[2]` from message text
   - Renders clickable citation buttons
   - Shows citation dialog with full metadata on click
   - Displays source document, chunk content, and relevance score

2. **API Service** (`src/services/ragApi.ts`)
   - Updated `ChatResponse` interface to include citations
   - Passes citations through to components

3. **Hooks** (`src/hooks/useConversations.ts`)
   - Updated `Message` interface to include citations
   - `addMessage` now accepts citations parameter
   - Citations stored with messages

## 🔧 How It Works

### Citation Generation Flow

1. **RAG Retrieval**: Chunks retrieved from FAISS
2. **Citation Metadata Creation**: Each chunk gets a citation ID
3. **LLM Generation**: LLM generates answer with inline citations [1], [2]
4. **Citation Extraction**: Backend extracts which citations were used
5. **Response**: Returns answer + citation metadata

### Frontend Display

1. **Citation Parsing**: ChatBubble parses `[1]`, `[2]` markers
2. **Clickable Buttons**: Citations rendered as clickable buttons
3. **Dialog Display**: Clicking shows full citation metadata
4. **Source Viewing**: Users can see exact chunk content

## 📋 Citation Format

### In Answer Text
```
The project uses React for the frontend [1] and FastAPI for the backend [2].
```

### Citation Metadata
```json
{
  "citation_id": 1,
  "source_document_id": "vault_id_123",
  "source_document_name": "document.pdf",
  "chunk_id": "0",
  "quoted_text": "The frontend is built using React...",
  "chunk_content": "Full chunk content here...",
  "score": 0.85
}
```

## 🎨 UI Features

### Citation Buttons
- Small, rounded buttons with citation number
- Primary color with hover effects
- Tooltip shows document name
- Click opens citation dialog

### Citation Dialog
- Shows source document name
- Displays chunk ID
- Shows quoted text excerpt
- Full chunk content in scrollable area
- Relevance score and document ID

## ✅ Next Steps

1. **Test the system:**
   - Upload a document
   - Embed it
   - Ask a question
   - Check for citations in answer
   - Click citations to view sources

2. **Deploy:**
   ```powershell
   git push origin merwin
   ```

3. **Verify:**
   - Citations appear in answers
   - Citations are clickable
   - Citation dialog shows correct metadata

## 🚀 Result

The system now generates answers with interactive citations that:
- ✅ Reference specific document chunks
- ✅ Are clickable in the UI
- ✅ Show full source metadata
- ✅ Display exact quoted text
- ✅ Link to source documents

---

**Citation system implemented and ready to test!**
