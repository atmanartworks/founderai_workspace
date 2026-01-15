# 📚 FounderGPT - Complete Project Documentation

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Features](#features)
4. [Tech Stack](#tech-stack)
5. [Project Structure](#project-structure)
6. [Setup Instructions](#setup-instructions)
7. [Deployment](#deployment)
8. [API Documentation](#api-documentation)
9. [Key Components](#key-components)
10. [RAG System](#rag-system)
11. [Database Schema](#database-schema)
12. [Environment Variables](#environment-variables)
13. [Troubleshooting](#troubleshooting)
14. [Development Workflow](#development-workflow)

---

## Project Overview

**FounderGPT** is a full-stack RAG (Retrieval-Augmented Generation) application that provides an AI-powered assistant for entrepreneurs and founders. The application allows users to upload documents, ask questions, and receive intelligent, context-aware responses based on their uploaded content.

### Key Capabilities

- 📄 **Document Management**: Upload, store, and process documents (PDF, DOCX, TXT, HTML, MD, JSON)
- 🧠 **RAG-Powered Chat**: Ask questions and get answers based on your uploaded documents
- 💬 **Conversation Management**: Organize chats with smart titles and persistent history
- 📎 **Interactive Citations**: Clickable citations that open document viewer with highlighted text
- 🔍 **Semantic Search**: Advanced vector-based document search using FAISS
- 📱 **Mobile Responsive**: Fully responsive design with mobile-first approach
- 🎨 **Modern UI**: Dark glossy SaaS theme with glassmorphism effects

---

## Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (Vercel)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   React/TS   │  │  Supabase    │  │   Tailwind   │      │
│  │   + Vite     │  │   Client     │  │   + shadcn   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP/SSE
                            │
┌─────────────────────────────────────────────────────────────┐
│                    Backend API (Render)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   FastAPI    │  │   OpenAI     │  │   FAISS      │      │
│  │   + Python   │  │   API        │  │   Vector DB  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ PostgreSQL + Vector
                            │
┌─────────────────────────────────────────────────────────────┐
│                    Database (Supabase)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ PostgreSQL   │  │   Storage   │  │  Auth + RLS  │      │
│  │   + pgvector │  │   (Files)    │  │  (Security)  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Document Upload Flow**:
   ```
   User uploads file → Frontend → Supabase Storage
   → Backend downloads → Text extraction → Chunking
   → Embedding generation → FAISS storage → Metadata to Supabase
   ```

2. **Chat Flow**:
   ```
   User question → Frontend → Backend API
   → Query embedding → FAISS search → Context retrieval
   → LLM generation (OpenAI) → Streaming response → Frontend display
   ```

3. **Citation Flow**:
   ```
   User clicks citation → Frontend → Document viewer opens
   → Fetch document chunks → Highlight quoted text → Scroll to position
   ```

---

## Features

### 1. Document Management

- **Supported Formats**: PDF, DOCX, TXT, HTML, MD, JSON
- **Automatic Processing**: Documents are automatically embedded and indexed
- **Text Extraction**: Advanced extraction from PDFs and DOCX files (including tables, headers, footers)
- **Storage**: Files stored in Supabase Storage with metadata in PostgreSQL

### 2. RAG-Powered Chat

- **Streaming Responses**: Real-time token streaming using Server-Sent Events (SSE)
- **Context-Aware**: Answers based on uploaded documents
- **Multiple Modes**:
  - **MODE_DOCUMENT**: Answers from document chunks with citations
  - **MODE_GENERAL**: General knowledge answers (no citations)
  - **MODE_EMPTY**: Handles empty/invalid input
- **Active Document Memory**: Conversation-level document context tracking

### 3. Interactive Citations

- **Inline Citations**: Clickable citation numbers (e.g., `[1]`, `[2]`) in responses
- **Document Viewer**: Right-side panel opens when citation is clicked
- **Text Highlighting**: Automatically highlights quoted text in document
- **Smooth Scrolling**: Scrolls to the referenced chunk position

### 4. Conversation Management

- **Smart Titles**: Auto-generates meaningful titles from first message
- **Persistent History**: All conversations saved to database
- **Conversation Switching**: Seamless switching between conversations
- **Rename/Delete**: Full CRUD operations on conversations

### 5. UI/UX Features

- **Dark Glossy Theme**: Premium SaaS aesthetic with glassmorphism
- **Mobile Responsive**: Fully responsive design for all screen sizes
- **Sidebar Navigation**: Collapsible sidebar for conversations
- **Real-time Updates**: Live message streaming and updates

---

## Tech Stack

### Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| React | 18.3.1 | UI Framework |
| TypeScript | 5.8.3 | Type Safety |
| Vite | 5.4.19 | Build Tool |
| Tailwind CSS | 3.4.17 | Styling |
| shadcn/ui | Latest | UI Components |
| React Router | 6.30.1 | Navigation |
| Supabase JS | 2.79.0 | Database & Auth Client |
| TanStack Query | 5.83.0 | Data Fetching |
| Lucide React | 0.462.0 | Icons |

### Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.12+ | Programming Language |
| FastAPI | 0.104.1 | Web Framework |
| Uvicorn | 0.24.0 | ASGI Server |
| OpenAI | 1.0.0+ | LLM API (GPT models) |
| FAISS | 1.7.4+ | Vector Database |
| NumPy | 1.24.0+ | Numerical Computing |
| python-docx | 0.8.11+ | DOCX Processing |
| PyPDF2 | 3.0.1 | PDF Processing |
| pdfplumber | 0.10.0+ | Advanced PDF Processing |
| Supabase | 2.24.0+ | Database Client |

### Database & Storage

| Service | Purpose |
|---------|---------|
| Supabase PostgreSQL | Primary database (conversations, messages, vault_files) |
| Supabase Storage | File storage (uploaded documents) |
| FAISS (Local) | Vector similarity search (embeddings) |
| pgvector | Vector extension for PostgreSQL (optional) |

### Deployment

| Platform | Purpose |
|----------|---------|
| Vercel | Frontend deployment |
| Render | Backend API deployment |
| GitHub | Version control & CI/CD |

---

## Project Structure

```
founder-ai-workspace/
├── src/                          # Frontend source code
│   ├── pages/                    # Page components
│   │   ├── Chat.tsx              # Main chat interface
│   │   ├── Dashboard.tsx         # Document dashboard
│   │   ├── Landing.tsx          # Landing page
│   │   └── Login.tsx             # Authentication page
│   ├── components/              # Reusable components
│   │   ├── ui/                   # shadcn/ui components
│   │   ├── ChatBubble.tsx       # Message display component
│   │   ├── ChatComposer.tsx     # Message input component
│   │   └── DocumentViewerPanel.tsx  # Citation document viewer
│   ├── hooks/                    # Custom React hooks
│   │   └── useConversations.ts  # Conversation management hook
│   ├── services/                 # API services
│   │   └── ragApi.ts            # RAG backend API client
│   ├── integrations/             # Third-party integrations
│   │   └── supabase/            # Supabase client setup
│   └── App.tsx                   # Main app component
│
├── rag-backend/                  # Backend source code
│   ├── app/
│   │   ├── main.py              # FastAPI application entry
│   │   ├── config.py            # Configuration management
│   │   ├── database.py          # Supabase client setup
│   │   ├── routes/              # API endpoints
│   │   │   ├── chat.py          # Chat endpoints (streaming & non-streaming)
│   │   │   ├── vault.py         # File upload endpoints
│   │   │   ├── embeddings.py    # Document embedding endpoints
│   │   │   ├── documents.py    # Document retrieval endpoints
│   │   │   └── search.py        # Search endpoints
│   │   ├── services/            # Business logic
│   │   │   ├── embedding_service.py    # LLM & embedding generation
│   │   │   ├── citation_service.py    # Citation extraction
│   │   │   ├── chunk_service.py       # Text chunking
│   │   │   ├── faiss_store.py         # FAISS vector operations
│   │   │   ├── text_extraction.py     # Document text extraction
│   │   │   ├── query_classifier.py    # Query type detection
│   │   │   ├── constraint_extractor.py # Constraint extraction
│   │   │   ├── question_rewrite.py    # Question rewriting
│   │   │   ├── answer_enforcer.py     # Answer constraint enforcement
│   │   │   └── llm_stream.py           # Streaming LLM wrapper
│   │   └── utils/               # Utility functions
│   │       └── sse.py           # Server-Sent Events helper
│   ├── faiss_storage/           # FAISS index storage directory
│   │   ├── index.faiss         # FAISS vector index
│   │   └── chunks_metadata.pkl # Chunk metadata
│   ├── requirements-railway.txt # Python dependencies
│   └── infrastructure/          # Infrastructure layer (optional)
│
├── supabase/                     # Database schemas
│   ├── migrations/              # SQL migration files
│   └── config.toml             # Supabase configuration
│
├── public/                       # Static assets
├── docs/                        # Documentation
├── package.json                 # Frontend dependencies
├── vite.config.ts              # Vite configuration
├── tailwind.config.ts          # Tailwind configuration
└── tsconfig.json               # TypeScript configuration
```

---

## Setup Instructions

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.12+
- **Git**
- **Supabase Account** (free tier works)
- **OpenAI API Key**

### Frontend Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/atmanartworks/founderai_workspace.git
   cd founder-ai-workspace
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Set up environment variables**:
   Create a `.env` file in the root directory:
   ```env
   VITE_SUPABASE_URL=your_supabase_url
   VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
   VITE_RAG_API_URL=http://127.0.0.1:8000
   ```

4. **Start development server**:
   ```bash
   npm run dev
   ```
   Frontend will be available at `http://localhost:8080`

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd rag-backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements-railway.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file in `rag-backend/`:
   ```env
   OPENAI_API_KEY=your_openai_api_key
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_service_role_key
   OPENAI_MODEL=gpt-4o-mini
   ```

5. **Create FAISS storage directory**:
   ```bash
   mkdir -p faiss_storage
   ```

6. **Start the backend server**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   Backend will be available at `http://127.0.0.1:8000`

### Database Setup

1. **Create Supabase project** at [supabase.com](https://supabase.com)

2. **Run database migrations**:
   - Go to Supabase SQL Editor
   - Run the SQL scripts from `supabase/migrations/`
   - Or use the Supabase CLI:
     ```bash
     supabase db push
     ```

3. **Set up Storage bucket**:
   - In Supabase Dashboard → Storage
   - Create a bucket named `chat-files`
   - Set it to public or configure RLS policies

4. **Configure RLS policies**:
   - Ensure Row Level Security is enabled
   - Create policies for `conversations`, `messages`, and `vault_files` tables
   - Users should only access their own data

---

## Deployment

### Frontend Deployment (Vercel)

1. **Connect GitHub repository** to Vercel
2. **Set build settings**:
   - Framework Preset: Vite
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Install Command: `npm install`
3. **Add environment variables**:
   - `VITE_SUPABASE_URL`
   - `VITE_SUPABASE_ANON_KEY`
   - `VITE_RAG_API_URL` (your Render backend URL)
4. **Deploy**

### Backend Deployment (Render)

1. **Create new Web Service** on Render
2. **Connect GitHub repository**
3. **Configure settings**:
   - **Name**: `founderai-workspace-backend`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements-railway.txt`
   - **Start Command**: `cd rag-backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Root Directory**: `rag-backend`
4. **Add environment variables**:
   - `OPENAI_API_KEY`
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `OPENAI_MODEL`
   - `PYTHONUNBUFFERED=1`
5. **Deploy**

### Post-Deployment Checklist

- [ ] Verify frontend loads correctly
- [ ] Test backend health endpoint
- [ ] Verify CORS is configured correctly
- [ ] Test document upload
- [ ] Test chat functionality
- [ ] Test citation clicking
- [ ] Verify environment variables are set

---

## API Documentation

### Base URL

- **Local**: `http://127.0.0.1:8000`
- **Production**: `https://your-backend.onrender.com`

### Endpoints

#### 1. Chat Endpoints

##### `POST /api/chat/message`
Non-streaming chat endpoint.

**Request Body**:
```json
{
  "message": "What is in this document?",
  "user_id": "user-uuid",
  "conversation_id": "conv-uuid",
  "top_k": 5,
  "active_document_id": "doc-uuid"
}
```

**Response**:
```json
{
  "response": "Based on the documents...",
  "sources": ["document1.pdf"],
  "message_id": "msg-uuid",
  "conversation_id": "conv-uuid",
  "citations": [
    {
      "citation_id": 1,
      "source_document_id": "doc-uuid",
      "source_document_name": "document1.pdf",
      "chunk_id": "chunk-123",
      "quoted_text": "Relevant text excerpt...",
      "chunk_content": "Full chunk content...",
      "score": 0.85
    }
  ]
}
```

##### `POST /api/chat/stream`
Streaming chat endpoint using Server-Sent Events (SSE).

**Request Body**: Same as `/api/chat/message`

**Response**: SSE stream with events:
- `event: token` - Streaming text tokens
- `event: done` - Final response with citations

**Example**:
```
event: token
data: {"text": "Based"}

event: token
data: {"text": " on"}

event: done
data: {"citations": [...], "source": "document"}
```

#### 2. Document Endpoints

##### `POST /api/vault/upload`
Upload a document file.

**Request**: `multipart/form-data`
- `file`: File to upload
- `user_id`: User UUID

**Response**:
```json
{
  "vault_id": "doc-uuid",
  "original_name": "document.pdf",
  "file_size": 1024000,
  "storage_path": "path/to/file"
}
```

##### `POST /api/embeddings/embed-document/{vault_id}`
Process and embed a document.

**Response**:
```json
{
  "success": true,
  "chunks": 25,
  "vault_id": "doc-uuid"
}
```

##### `GET /api/documents/{document_id}/chunks`
Get document chunks for citation viewing.

**Query Parameters**:
- `user_id`: User UUID
- `chunk_id` (optional): Specific chunk ID
- `quoted_text` (optional): Text to highlight

**Response**:
```json
{
  "document_id": "doc-uuid",
  "document_name": "document.pdf",
  "chunks": [
    {
      "chunk_id": "chunk-123",
      "content": "Chunk content...",
      "chunk_index": 0
    }
  ],
  "text_content": "Full document text..."
}
```

#### 3. Search Endpoints

##### `POST /api/search/semantic-search`
Semantic search across documents.

**Request Body**:
```json
{
  "query": "search query",
  "user_id": "user-uuid",
  "top_k": 5
}
```

**Response**:
```json
{
  "results": [
    {
      "chunk_id": "chunk-123",
      "content": "Relevant content...",
      "score": 0.92,
      "document_id": "doc-uuid",
      "document_name": "document.pdf"
    }
  ]
}
```

---

## Key Components

### Frontend Components

#### `Chat.tsx`
Main chat interface component.

**Features**:
- Conversation management
- Message display
- Document upload
- Citation handling
- Active document tracking
- Sidebar navigation

**Key State**:
- `currentConversation`: Active conversation
- `messages`: Message list
- `activeDocumentId`: Current document context
- `sidebarOpen`: Sidebar visibility

#### `ChatBubble.tsx`
Individual message display component.

**Features**:
- User/AI message styling
- Citation button rendering
- Click handlers for citations
- Timestamp display

#### `ChatComposer.tsx`
Message input component.

**Features**:
- Text input with auto-resize
- File attachment
- Send button
- Keyboard shortcuts (Enter to send)

#### `DocumentViewerPanel.tsx`
Citation document viewer panel.

**Features**:
- Right-side slide-out panel
- Document chunk display
- Text highlighting
- Smooth scrolling to chunks

#### `useConversations.ts`
Custom hook for conversation management.

**Functions**:
- `loadConversations()`: Load all conversations
- `createConversation()`: Create new conversation
- `selectConversation()`: Switch to conversation
- `loadMessages()`: Load messages for conversation
- `addMessage()`: Add message to conversation
- `deleteConversation()`: Delete conversation
- `renameConversation()`: Rename conversation

### Backend Services

#### `embedding_service.py`
LLM and embedding generation service.

**Key Functions**:
- `generate()`: Generate LLM response
- `embed_batch()`: Generate embeddings for text chunks
- Handles MODE_DOCUMENT, MODE_GENERAL, MODE_EMPTY

#### `citation_service.py`
Citation extraction and formatting service.

**Key Functions**:
- `generate_answer_with_citations()`: Generate answer with inline citations
- `extract_citation_metadata()`: Extract citation information

#### `faiss_store.py`
FAISS vector database operations.

**Key Functions**:
- `add_chunks()`: Add chunks to FAISS index
- `search()`: Search similar chunks
- `delete_chunks_by_vault()`: Delete chunks by document

#### `text_extraction.py`
Document text extraction service.

**Supported Formats**:
- PDF (PyPDF2, pdfplumber)
- DOCX (python-docx with tables, headers, footers)
- TXT, HTML, MD, JSON

---

## RAG System

### How RAG Works

1. **Document Processing**:
   - Upload document → Extract text → Chunk text → Generate embeddings → Store in FAISS

2. **Query Processing**:
   - User question → Generate query embedding → Search FAISS → Retrieve top-k chunks → Generate answer with citations

3. **Answer Generation**:
   - Context chunks + User question → LLM (OpenAI) → Streamed response with citations

### RAG Modes

#### MODE_DOCUMENT
- Uses retrieved document chunks
- Includes citations
- Answers only from provided context
- If no relevant chunks: "The answer is not available in the uploaded documents."

#### MODE_GENERAL
- Answers using general knowledge
- No citations
- No mention of documents
- Ends with: "Source: Generated"

#### MODE_EMPTY
- Handles empty/invalid input
- Response: "Please enter a valid question."

### Active Document Memory

The system maintains conversation-level document context:

- **When set**: Document upload, document viewer opened, citation clicked
- **How used**: Vague queries ("what's in this document") automatically use active document
- **Fallback**: If text extraction failed, filters FAISS search to active document

### Citation System

1. **Citation Generation**:
   - During answer generation, chunks are tracked
   - Citation metadata includes: document ID, chunk ID, quoted text, score

2. **Citation Display**:
   - Inline citation numbers: `[1]`, `[2]`, etc.
   - Clickable buttons in chat bubbles

3. **Document Viewer**:
   - Opens on citation click
   - Displays document chunks
   - Highlights quoted text
   - Scrolls to chunk position

---

## Database Schema

### Tables

#### `conversations`
```sql
CREATE TABLE conversations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES auth.users(id),
  title TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### `messages`
```sql
CREATE TABLE messages (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
  content TEXT,
  is_ai BOOLEAN NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  file_urls TEXT[],
  citations JSONB,
  -- Legacy fields (for backward compatibility)
  user_message TEXT,
  assistant_message TEXT,
  used_documents JSONB
);
```

#### `vault_files`
```sql
CREATE TABLE vault_files (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES auth.users(id),
  storage_path TEXT NOT NULL,
  original_name TEXT NOT NULL,
  file_size BIGINT,
  content_type TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  text_content TEXT  -- Extracted text for direct access
);
```

### Row Level Security (RLS)

All tables have RLS enabled. Users can only access their own data:

```sql
-- Example policy for conversations
CREATE POLICY "Users can view own conversations"
  ON conversations FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own conversations"
  ON conversations FOR INSERT
  WITH CHECK (auth.uid() = user_id);
```

---

## Environment Variables

### Frontend (.env)

```env
# Supabase
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key

# Backend API
VITE_RAG_API_URL=http://127.0.0.1:8000  # Local
# VITE_RAG_API_URL=https://your-backend.onrender.com  # Production
```

### Backend (.env)

```env
# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key

# Server
PYTHONUNBUFFERED=1
PORT=8000
```

---

## Troubleshooting

### Common Issues

#### 1. CORS Errors

**Problem**: `Access-Control-Allow-Origin` header missing

**Solution**:
- Check backend CORS configuration in `app/main.py`
- Ensure `allow_origins=["*"]` is set
- Verify frontend URL matches allowed origins

#### 2. Messages Not Loading

**Problem**: Messages disappear when switching conversations

**Solution**:
- Check `loadMessages()` function in `useConversations.ts`
- Verify message format transformation (user_message/assistant_message → content/is_ai)
- Check database for message records

#### 3. Document Upload Fails

**Problem**: "Failed to fetch" error

**Solution**:
- Verify backend is running
- Check CORS configuration
- Verify Supabase Storage bucket exists
- Check RLS policies for storage

#### 4. Embeddings Not Working

**Problem**: "No usable text found" error

**Solution**:
- Check text extraction logs
- Verify document format is supported
- Ensure `text_content` column exists in `vault_files` table
- Check file is not password-protected or corrupted

#### 5. Citations Not Clickable

**Problem**: Citations don't open document viewer

**Solution**:
- Verify `DocumentViewerPanel` is rendered in `Chat.tsx`
- Check `onCitationClick` handler is connected
- Verify document chunks endpoint is accessible
- Check browser console for errors

#### 6. Streaming Not Working

**Problem**: Messages don't stream, appear all at once

**Solution**:
- Verify SSE endpoint is being called (`/api/chat/stream`)
- Check `streamMessage()` function in `ragApi.ts`
- Verify backend streaming implementation
- Check network tab for SSE events

### Debugging Tips

1. **Check Browser Console**: Look for JavaScript errors
2. **Check Network Tab**: Verify API requests/responses
3. **Check Backend Logs**: Look for Python errors
4. **Verify Environment Variables**: Ensure all are set correctly
5. **Test Endpoints Directly**: Use curl or Postman to test API

---

## Development Workflow

### Local Development

1. **Start Backend**:
   ```bash
   cd rag-backend
   source .venv/bin/activate
   uvicorn app.main:app --reload
   ```

2. **Start Frontend**:
   ```bash
   npm run dev
   ```

3. **Make Changes**: Edit files, changes auto-reload

### Git Workflow

1. **Create Feature Branch**:
   ```bash
   git checkout -b feature/your-feature
   ```

2. **Make Changes & Commit**:
   ```bash
   git add .
   git commit -m "Description of changes"
   ```

3. **Push to GitHub**:
   ```bash
   git push origin feature/your-feature
   ```

4. **Deploy**: Vercel and Render auto-deploy on push to `main` or `merwin` branch

### Testing

1. **Test Document Upload**: Upload PDF/DOCX, verify embedding
2. **Test Chat**: Ask questions, verify responses
3. **Test Citations**: Click citations, verify document viewer
4. **Test Mobile**: Resize browser, test responsive design
5. **Test Conversation Switching**: Switch between chats, verify messages persist

---

## Additional Resources

### Documentation Files

- `DEPLOYMENT_GUIDE.md` - Detailed deployment instructions
- `docs/RAG_INTEGRATION_GUIDE.md` - RAG system details
- `docs/CONVERSATION_FLOW_GUIDE.md` - Conversation flow explanation
- `ADD_TEXT_CONTENT_COLUMN.md` - Database migration guide

### External Links

- [Supabase Documentation](https://supabase.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [FAISS Documentation](https://github.com/facebookresearch/faiss)

---

## Support

For issues or questions:

1. Check this documentation
2. Review existing GitHub issues
3. Check deployment logs (Vercel/Render)
4. Review browser console and network tab

---

**Last Updated**: January 2026  
**Version**: 1.0.0  
**Maintainer**: FounderGPT Team
