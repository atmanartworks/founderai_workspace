# 🏛️ Clean Architecture Migration Guide

## 📋 Table of Contents
1. [Current Architecture Analysis](#current-architecture-analysis)
2. [Clean Architecture Overview](#clean-architecture-overview)
3. [Proposed Structure](#proposed-structure)
4. [Migration Plan](#migration-plan)
5. [Step-by-Step Implementation](#step-by-step-implementation)
6. [Benefits](#benefits)
7. [Trade-offs](#trade-offs)

---

## 🔍 Current Architecture Analysis

### **Backend (Python/FastAPI):**

```
rag-backend/
├── app/
│   ├── routes/           # API endpoints (FastAPI routers)
│   │   ├── chat.py
│   │   ├── embeddings.py
│   │   ├── search.py
│   │   └── vault.py
│   ├── services/         # Business logic + infrastructure
│   │   ├── chunk_service.py
│   │   ├── embedding_service.py
│   │   └── text_extraction.py
│   ├── utils/            # Utility functions
│   ├── database.py       # Supabase client (infrastructure)
│   ├── config.py         # Configuration
│   └── main.py           # FastAPI app initialization
```

**Current Issues:**
- ❌ **Mixed Concerns**: Services contain both business logic AND infrastructure
- ❌ **Tight Coupling**: Routes directly depend on Supabase, Groq, etc.
- ❌ **Hard to Test**: Can't test business logic without real databases
- ❌ **No Domain Layer**: Business rules scattered across routes/services
- ❌ **Infrastructure Dependency**: Core logic depends on external frameworks

---

### **Frontend (React/TypeScript):**

```
src/
├── pages/              # UI components (presentation)
│   ├── Chat.tsx
│   ├── Dashboard.tsx
│   └── ...
├── components/         # Reusable UI components
├── hooks/              # Custom React hooks (contains business logic!)
│   └── useConversations.ts
├── services/           # API clients
│   ├── ragApi.ts
│   └── titleGenerator.ts
├── integrations/       # External service clients
│   └── supabase/
└── lib/                # Utilities
```

**Current Issues:**
- ❌ **Business Logic in Hooks**: `useConversations` mixes UI state + business rules
- ❌ **Tight Coupling**: Components directly call Supabase
- ❌ **Hard to Test**: Can't test logic without React
- ❌ **No Domain Model**: Data structures are just types
- ❌ **State Management**: No clear separation of concerns

---

## 🏛️ Clean Architecture Overview

### **Core Principles:**

```
┌──────────────────────────────────────────────┐
│           🎨 Presentation Layer              │
│         (UI, Controllers, Routes)            │
└──────────────────────────────────────────────┘
                    ↓ depends on
┌──────────────────────────────────────────────┐
│         💼 Application/Use Cases             │
│      (Orchestration, Business Flows)         │
└──────────────────────────────────────────────┘
                    ↓ depends on
┌──────────────────────────────────────────────┐
│           🧠 Domain/Entities                 │
│       (Business Rules, Core Logic)           │
└──────────────────────────────────────────────┘
                    ↑ implemented by
┌──────────────────────────────────────────────┐
│         🔧 Infrastructure Layer              │
│   (Database, APIs, File System, External)    │
└──────────────────────────────────────────────┘
```

**Key Rules:**
1. ✅ **Dependency Inversion**: Inner layers don't know about outer layers
2. ✅ **Domain Independence**: Core business logic has NO external dependencies
3. ✅ **Testability**: Can test each layer independently
4. ✅ **Flexibility**: Easy to swap implementations (e.g., change database)

---

## 🗂️ Proposed Structure

### **Backend Clean Architecture:**

```
rag-backend/
├── domain/                        # 🧠 CORE BUSINESS LOGIC (No dependencies!)
│   ├── entities/                  # Business entities
│   │   ├── conversation.py        # Conversation entity
│   │   ├── message.py             # Message entity
│   │   ├── document.py            # Document entity
│   │   ├── chunk.py               # Document chunk entity
│   │   └── user.py                # User entity
│   ├── value_objects/             # Immutable value objects
│   │   ├── embedding.py           # Embedding vector
│   │   ├── file_path.py           # File path with validation
│   │   └── conversation_id.py     # Typed IDs
│   ├── repositories/              # Repository interfaces (contracts)
│   │   ├── conversation_repository.py
│   │   ├── message_repository.py
│   │   ├── document_repository.py
│   │   └── chunk_repository.py
│   ├── services/                  # Domain services (pure business logic)
│   │   ├── chunking_service.py    # Text chunking logic
│   │   ├── title_generator.py     # Smart title generation
│   │   └── text_cleaner.py        # Text sanitization rules
│   └── exceptions/                # Domain-specific exceptions
│       ├── document_not_found.py
│       └── invalid_chunk.py
│
├── application/                   # 💼 USE CASES (Application logic)
│   ├── use_cases/
│   │   ├── chat/
│   │   │   ├── send_message.py           # SendMessage use case
│   │   │   ├── create_conversation.py    # CreateConversation
│   │   │   └── get_chat_history.py       # GetChatHistory
│   │   ├── documents/
│   │   │   ├── upload_document.py        # UploadDocument
│   │   │   ├── embed_document.py         # EmbedDocument
│   │   │   └── search_documents.py       # SearchDocuments
│   │   └── vault/
│   │       ├── list_files.py             # ListFiles
│   │       └── delete_file.py            # DeleteFile
│   ├── dtos/                      # Data Transfer Objects
│   │   ├── chat_request.py
│   │   ├── chat_response.py
│   │   └── upload_request.py
│   └── interfaces/                # Application interfaces
│       ├── embedding_provider.py  # Interface for embeddings
│       ├── llm_provider.py        # Interface for LLM
│       └── storage_provider.py    # Interface for file storage
│
├── infrastructure/                # 🔧 EXTERNAL IMPLEMENTATIONS
│   ├── database/
│   │   ├── supabase/
│   │   │   ├── supabase_client.py        # Supabase connection
│   │   │   ├── conversation_repo_impl.py # Implements repo interface
│   │   │   ├── message_repo_impl.py
│   │   │   ├── document_repo_impl.py
│   │   │   └── chunk_repo_impl.py
│   │   └── models/                       # Database models (Supabase tables)
│   │       ├── conversation_model.py
│   │       ├── message_model.py
│   │       └── document_model.py
│   ├── ai/
│   │   ├── groq_provider.py              # Groq LLM implementation
│   │   ├── sentence_transformer.py       # SentenceTransformer embeddings
│   │   └── ollama_provider.py            # Alternative LLM
│   ├── storage/
│   │   ├── supabase_storage.py           # Supabase storage
│   │   └── local_storage.py              # Alternative: local files
│   ├── text_extraction/
│   │   ├── pdf_extractor.py              # PDF extraction
│   │   ├── docx_extractor.py             # DOCX extraction
│   │   └── text_extractor.py             # Plain text
│   └── config/
│       └── settings.py                   # Environment variables
│
├── presentation/                  # 🎨 API LAYER (FastAPI)
│   ├── api/
│   │   ├── v1/
│   │   │   ├── routers/
│   │   │   │   ├── chat.py               # Chat endpoints
│   │   │   │   ├── documents.py          # Document endpoints
│   │   │   │   └── vault.py              # Vault endpoints
│   │   │   └── schemas/                  # Pydantic schemas for API
│   │   │       ├── chat_schema.py
│   │   │       ├── document_schema.py
│   │   │       └── vault_schema.py
│   │   └── dependencies/                 # FastAPI dependencies
│   │       └── container.py              # Dependency injection
│   └── main.py                           # FastAPI app
│
└── tests/                         # 🧪 TESTS
    ├── unit/
    │   ├── domain/                       # Test domain logic
    │   ├── application/                  # Test use cases
    │   └── infrastructure/               # Test implementations
    ├── integration/                      # Integration tests
    └── e2e/                              # End-to-end tests
```

---

### **Frontend Clean Architecture:**

```
src/
├── domain/                        # 🧠 CORE BUSINESS LOGIC
│   ├── entities/
│   │   ├── Conversation.ts        # Conversation entity
│   │   ├── Message.ts             # Message entity
│   │   └── VaultFile.ts           # File entity
│   ├── repositories/              # Repository interfaces
│   │   ├── IConversationRepository.ts
│   │   ├── IMessageRepository.ts
│   │   └── IVaultRepository.ts
│   ├── services/                  # Domain services
│   │   └── TitleGenerator.ts      # Pure title generation logic
│   └── value-objects/
│       ├── ConversationId.ts
│       └── MessageContent.ts
│
├── application/                   # 💼 USE CASES
│   ├── use-cases/
│   │   ├── chat/
│   │   │   ├── SendMessageUseCase.ts
│   │   │   ├── CreateConversationUseCase.ts
│   │   │   └── LoadMessagesUseCase.ts
│   │   ├── vault/
│   │   │   ├── UploadFileUseCase.ts
│   │   │   └── ListFilesUseCase.ts
│   │   └── auth/
│   │       ├── LoginUseCase.ts
│   │       └── SignupUseCase.ts
│   ├── dtos/
│   │   ├── ChatRequestDto.ts
│   │   └── ChatResponseDto.ts
│   └── ports/                     # Interfaces
│       ├── IAuthProvider.ts
│       ├── IRagApiClient.ts
│       └── IStorageProvider.ts
│
├── infrastructure/                # 🔧 IMPLEMENTATIONS
│   ├── api/
│   │   ├── SupabaseClient.ts      # Supabase implementation
│   │   ├── RagApiClient.ts        # RAG backend client
│   │   └── HttpClient.ts          # Generic HTTP client
│   ├── repositories/
│   │   ├── SupabaseConversationRepository.ts
│   │   ├── SupabaseMessageRepository.ts
│   │   └── SupabaseVaultRepository.ts
│   ├── auth/
│   │   └── SupabaseAuthProvider.ts
│   └── state/                     # State management
│       ├── ConversationStore.ts   # Zustand/Redux store
│       └── AuthStore.ts
│
├── presentation/                  # 🎨 UI LAYER
│   ├── pages/
│   │   ├── Chat/
│   │   │   ├── ChatPage.tsx       # Page component
│   │   │   ├── useChatViewModel.ts # ViewModel hook
│   │   │   └── ChatViewModel.ts   # Presentation logic
│   │   ├── Dashboard/
│   │   └── Auth/
│   ├── components/
│   │   ├── chat/
│   │   │   ├── ChatBubble.tsx     # Pure UI component
│   │   │   └── ChatComposer.tsx
│   │   └── common/
│   └── hooks/                     # UI-only hooks
│       ├── useToast.ts
│       └── useMobile.ts
│
├── di/                            # 📦 DEPENDENCY INJECTION
│   └── container.ts               # IoC container (tsyringe/inversify)
│
└── tests/
    ├── unit/
    ├── integration/
    └── e2e/
```

---

## 📋 Migration Plan

### **Phase 1: Domain Layer (Backend)** ⏱️ 1-2 days

**Goal:** Extract pure business logic with zero dependencies

**Tasks:**
1. ✅ Create domain entities (Conversation, Message, Document, Chunk)
2. ✅ Define repository interfaces
3. ✅ Extract pure business logic from services
4. ✅ Create domain exceptions
5. ✅ Write unit tests for domain layer

**Example - Before:**
```python
# app/services/chunk_service.py (mixed concerns)
class ChunkingService:
    @staticmethod
    def chunk_text(text: str, max_chars: int = 1000):
        # Business logic mixed with implementation details
        ...
```

**After:**
```python
# domain/services/chunking_service.py (pure logic)
class ChunkingDomainService:
    def chunk_text(self, text: str, max_chars: int = 1000) -> List[Chunk]:
        # Pure business logic, returns domain entities
        chunks = []
        # ... chunking logic ...
        return [Chunk(content=..., index=...) for ...]
```

---

### **Phase 2: Application Layer (Backend)** ⏱️ 2-3 days

**Goal:** Create use cases that orchestrate domain logic

**Tasks:**
1. ✅ Define use case interfaces
2. ✅ Implement SendMessage use case
3. ✅ Implement EmbedDocument use case
4. ✅ Implement SearchDocuments use case
5. ✅ Create DTOs for input/output
6. ✅ Write unit tests with mocks

**Example - SendMessage Use Case:**
```python
# application/use_cases/chat/send_message.py
class SendMessageUseCase:
    def __init__(
        self,
        conversation_repo: ConversationRepository,
        message_repo: MessageRepository,
        chunk_repo: ChunkRepository,
        embedding_provider: EmbeddingProvider,
        llm_provider: LLMProvider
    ):
        self.conversation_repo = conversation_repo
        self.message_repo = message_repo
        self.chunk_repo = chunk_repo
        self.embedding_provider = embedding_provider
        self.llm_provider = llm_provider
    
    async def execute(self, request: SendMessageRequest) -> SendMessageResponse:
        # 1. Get or create conversation
        conversation = await self.conversation_repo.get_by_id(request.conversation_id)
        if not conversation:
            conversation = await self.conversation_repo.create(...)
        
        # 2. Save user message
        user_message = Message(
            conversation_id=conversation.id,
            content=request.message,
            is_ai=False
        )
        await self.message_repo.save(user_message)
        
        # 3. Embed query
        query_embedding = await self.embedding_provider.embed_text(request.message)
        
        # 4. Search relevant chunks
        chunks = await self.chunk_repo.search_by_embedding(
            query_embedding, 
            user_id=request.user_id,
            limit=request.top_k
        )
        
        # 5. Build context
        context = self._build_context(chunks)
        
        # 6. Generate response
        ai_response = await self.llm_provider.generate(
            prompt=self._build_prompt(context, request.message)
        )
        
        # 7. Save AI message
        ai_message = Message(
            conversation_id=conversation.id,
            content=ai_response,
            is_ai=True
        )
        await self.message_repo.save(ai_message)
        
        # 8. Return response
        return SendMessageResponse(
            response=ai_response,
            sources=[chunk.source_file for chunk in chunks],
            message_id=ai_message.id,
            conversation_id=conversation.id
        )
```

---

### **Phase 3: Infrastructure Layer (Backend)** ⏱️ 2-3 days

**Goal:** Implement repository interfaces with Supabase

**Tasks:**
1. ✅ Implement Supabase repositories
2. ✅ Implement Groq LLM provider
3. ✅ Implement SentenceTransformer embedding provider
4. ✅ Implement Supabase storage provider
5. ✅ Create database models/mappers
6. ✅ Write integration tests

**Example - Repository Implementation:**
```python
# infrastructure/database/supabase/conversation_repo_impl.py
class SupabaseConversationRepository(ConversationRepository):
    def __init__(self, client: Client):
        self.client = client
    
    async def get_by_id(self, conversation_id: str) -> Optional[Conversation]:
        result = self.client.table("conversations").select("*").eq("id", conversation_id).execute()
        if not result.data:
            return None
        return self._to_entity(result.data[0])
    
    async def save(self, conversation: Conversation) -> Conversation:
        data = self._to_model(conversation)
        result = self.client.table("conversations").insert(data).execute()
        return self._to_entity(result.data[0])
    
    def _to_entity(self, model: dict) -> Conversation:
        return Conversation(
            id=ConversationId(model["id"]),
            user_id=model["user_id"],
            title=model["title"],
            created_at=model["created_at"],
            updated_at=model["updated_at"]
        )
    
    def _to_model(self, entity: Conversation) -> dict:
        return {
            "id": str(entity.id),
            "user_id": entity.user_id,
            "title": entity.title,
            "created_at": entity.created_at.isoformat(),
            "updated_at": entity.updated_at.isoformat()
        }
```

---

### **Phase 4: Presentation Layer (Backend)** ⏱️ 1-2 days

**Goal:** Thin API controllers that delegate to use cases

**Tasks:**
1. ✅ Refactor FastAPI routes to use use cases
2. ✅ Set up dependency injection
3. ✅ Create Pydantic schemas for API
4. ✅ Add proper error handling
5. ✅ Write API tests

**Example - Thin Controller:**
```python
# presentation/api/v1/routers/chat.py
from fastapi import APIRouter, Depends
from presentation.api.v1.schemas.chat_schema import ChatRequest, ChatResponse
from application.use_cases.chat.send_message import SendMessageUseCase
from presentation.api.dependencies.container import get_send_message_use_case

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    use_case: SendMessageUseCase = Depends(get_send_message_use_case)
):
    """
    Thin controller - just validates input and delegates to use case
    """
    try:
        # Convert API schema to use case DTO
        use_case_request = SendMessageRequest(
            conversation_id=request.conversation_id,
            message=request.message,
            user_id=request.user_id,
            top_k=request.top_k
        )
        
        # Execute use case
        result = await use_case.execute(use_case_request)
        
        # Convert use case result to API schema
        return ChatResponse(
            response=result.response,
            sources=result.sources,
            message_id=result.message_id,
            conversation_id=result.conversation_id
        )
    except DomainException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

### **Phase 5: Frontend Domain Layer** ⏱️ 1-2 days

**Goal:** Extract frontend business logic

**Tasks:**
1. ✅ Create domain entities
2. ✅ Define repository interfaces
3. ✅ Extract business logic from hooks
4. ✅ Create domain services
5. ✅ Write unit tests

---

### **Phase 6: Frontend Application Layer** ⏱️ 2-3 days

**Goal:** Create frontend use cases

**Tasks:**
1. ✅ Implement SendMessage use case
2. ✅ Implement CreateConversation use case
3. ✅ Implement UploadFile use case
4. ✅ Set up state management (Zustand/Redux)
5. ✅ Write tests

---

### **Phase 7: Frontend Infrastructure** ⏱️ 1-2 days

**Goal:** Implement repository interfaces

**Tasks:**
1. ✅ Implement Supabase repositories
2. ✅ Implement RAG API client
3. ✅ Implement auth provider
4. ✅ Write integration tests

---

### **Phase 8: Frontend Presentation** ⏱️ 2-3 days

**Goal:** Refactor UI components to use ViewModels

**Tasks:**
1. ✅ Create ViewModels for pages
2. ✅ Refactor components to be pure UI
3. ✅ Connect ViewModels to use cases
4. ✅ Set up dependency injection
5. ✅ Write component tests

---

## 🎯 Benefits

### **1. Testability** ✅

**Before:**
```python
# Can't test without real Supabase connection
def test_chat():
    # Need real database, API keys, etc.
    pass
```

**After:**
```python
# Test with mocks
def test_send_message_use_case():
    # Mock repositories
    mock_repo = Mock(MessageRepository)
    mock_llm = Mock(LLMProvider)
    
    use_case = SendMessageUseCase(mock_repo, mock_llm)
    result = use_case.execute(request)
    
    assert result.response == "Expected response"
```

---

### **2. Flexibility** ✅

**Easy to swap implementations:**

```python
# Switch from Supabase to PostgreSQL
container.register(
    ConversationRepository,
    PostgresConversationRepository  # Just change this line!
)

# Switch from Groq to OpenAI
container.register(
    LLMProvider,
    OpenAIProvider  # Just change this line!
)
```

---

### **3. Maintainability** ✅

- ✅ Clear separation of concerns
- ✅ Each layer has single responsibility
- ✅ Easy to locate and fix bugs
- ✅ Easy to add new features

---

### **4. Team Scalability** ✅

- ✅ Different teams can work on different layers
- ✅ Clear contracts (interfaces) between layers
- ✅ Less merge conflicts
- ✅ Easier onboarding

---

### **5. Domain-Driven Design** ✅

- ✅ Business logic is explicit and clear
- ✅ Entities represent real business concepts
- ✅ Easy to discuss with non-technical stakeholders

---

## ⚖️ Trade-offs

### **Pros:**

1. ✅ **Better Code Quality** - Clear structure, testable
2. ✅ **Future-Proof** - Easy to change/extend
3. ✅ **Professional** - Industry-standard architecture
4. ✅ **Team-Ready** - Scales with team size
5. ✅ **Testable** - Can test everything in isolation

### **Cons:**

1. ❌ **More Code** - More files and boilerplate
2. ❌ **Initial Complexity** - Steeper learning curve
3. ❌ **Migration Time** - 10-14 days of work
4. ❌ **Abstraction Overhead** - More layers to navigate

---

## 🤔 Should You Migrate?

### **Migrate NOW if:**

- ✅ Planning to scale the team
- ✅ Project will grow significantly
- ✅ Need to swap implementations (e.g., change database)
- ✅ Want professional, maintainable code
- ✅ Building a long-term product

### **Don't Migrate if:**

- ❌ Quick prototype/MVP
- ❌ Solo developer for small project
- ❌ Time-sensitive deadline
- ❌ Project will be thrown away soon

---

## 📊 Comparison

| Aspect | Current | Clean Architecture |
|--------|---------|-------------------|
| **Testability** | Hard | Easy |
| **Maintainability** | Medium | High |
| **Flexibility** | Low | High |
| **Code Volume** | Less | More |
| **Complexity** | Simple | Structured |
| **Onboarding** | Quick | Moderate |
| **Scalability** | Limited | Excellent |

---

## 🚀 Getting Started

### **Option 1: Full Migration (Recommended)**
- Migrate entire project over 10-14 days
- Start with backend domain layer
- Test thoroughly at each phase

### **Option 2: Gradual Migration**
- Migrate one feature at a time
- Keep old code working alongside new
- Slower but less risky

### **Option 3: New Features Only**
- Keep existing code as-is
- Use Clean Architecture for all new features
- Gradually refactor old code when touching it

---

## 📚 Resources

- [Clean Architecture by Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Domain-Driven Design](https://martinfowler.com/tags/domain%20driven%20design.html)
- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)

---

## ✅ Next Steps

If you want to proceed, I can:

1. 🎯 **Start Phase 1** - Create domain entities for backend
2. 📝 **Create detailed code examples** - Show exactly how to implement
3. 🔧 **Set up dependency injection** - Configure IoC container
4. 🧪 **Set up testing infrastructure** - Unit/integration tests
5. 📦 **Create migration scripts** - Automate the migration

**Let me know if you want to proceed with the migration!** 🚀

