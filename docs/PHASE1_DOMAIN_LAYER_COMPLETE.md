# ✅ Phase 1 Complete: Domain Layer

## 🎉 What We've Built

The **Domain Layer** is the heart of Clean Architecture - pure business logic with **ZERO external dependencies**!

---

## 📁 Structure Created

```
domain/
├── __init__.py
├── entities/                    ✅ 4 Core Business Objects
│   ├── __init__.py
│   ├── conversation.py          • Conversation (chat session)
│   ├── message.py               • Message (user/AI message)
│   ├── document.py              • Document (uploaded file)
│   └── chunk.py                 • Chunk (document piece for RAG)
│
├── repositories/                ✅ 4 Repository Interfaces
│   ├── __init__.py
│   ├── conversation_repository.py    • Contract for conversation data access
│   ├── message_repository.py         • Contract for message data access
│   ├── document_repository.py        • Contract for document data access
│   └── chunk_repository.py           • Contract for chunk data access
│
├── services/                    ✅ 3 Domain Services
│   ├── __init__.py
│   ├── chunking_service.py      • Pure text chunking logic
│   ├── text_cleaner.py          • Text sanitization rules
│   └── title_generator.py       • Smart title generation
│
├── value_objects/               ✅ Value Objects
│   ├── __init__.py
│   └── embedding.py             • Immutable embedding vector
│
└── exceptions/                  ✅ Domain Exceptions
    ├── __init__.py
    ├── domain_exception.py      • Base exception
    ├── not_found_exception.py   • Entity not found errors
    ├── validation_exception.py  • Validation errors
    └── access_denied_exception.py • Authorization errors
```

---

## 🧠 Entities Created

### **1. Conversation** (`domain/entities/conversation.py`)

**Business Object:** Represents a chat session

**Business Rules:**
- ✅ Must have user_id
- ✅ Title cannot be empty
- ✅ Created_at is immutable
- ✅ Updated_at changes on modification

**Key Methods:**
```python
conversation.update_title(new_title)  # Update title
conversation.touch()                  # Update timestamp
conversation.is_owned_by(user_id)     # Check ownership
```

---

### **2. Message** (`domain/entities/message.py`)

**Business Object:** Represents a single message

**Business Rules:**
- ✅ Must belong to a conversation
- ✅ Content cannot be empty
- ✅ is_ai flag distinguishes user from AI
- ✅ Can reference source documents

**Key Methods:**
```python
message.is_from_user()           # Check if from user
message.is_from_ai()             # Check if from AI
message.has_sources()            # Check if has sources
message.get_source_files()       # Get source files
message.add_file_url(url)        # Add attachment
```

---

### **3. Document** (`domain/entities/document.py`)

**Business Object:** Represents an uploaded file

**Business Rules:**
- ✅ Must have user_id (owner)
- ✅ Must have storage_path
- ✅ file_size must be positive
- ✅ Tracks extracted text content

**Key Methods:**
```python
document.is_owned_by(user_id)        # Check ownership
document.has_text_content()          # Check if extracted
document.set_text_content(text)      # Set extracted text
document.get_file_extension()        # Get extension
document.is_pdf()                    # Check if PDF
document.is_docx()                   # Check if DOCX
```

---

### **4. Chunk** (`domain/entities/chunk.py`)

**Business Object:** Represents a document piece for RAG

**Business Rules:**
- ✅ Must belong to a document
- ✅ Content cannot be empty
- ✅ chunk_index indicates position
- ✅ Has embedding vector for similarity search
- ✅ Must have user_id for access control

**Key Methods:**
```python
chunk.is_owned_by(user_id)              # Check ownership
chunk.belongs_to_document(doc_id)       # Check document
chunk.get_embedding_dimension()         # Get vector dimension
chunk.get_content_preview(length)       # Get preview
```

---

## 🔌 Repository Interfaces

These are **CONTRACTS** - not implementations!

### **ConversationRepository**
```python
async def get_by_id(conversation_id) -> Conversation
async def get_by_user(user_id) -> List[Conversation]
async def save(conversation) -> Conversation
async def delete(conversation_id) -> bool
async def exists(conversation_id) -> bool
```

### **MessageRepository**
```python
async def get_by_id(message_id) -> Message
async def get_by_conversation(conversation_id) -> List[Message]
async def save(message) -> Message
async def delete(message_id) -> bool
async def delete_by_conversation(conversation_id) -> int
async def count_by_conversation(conversation_id) -> int
```

### **DocumentRepository**
```python
async def get_by_id(document_id) -> Document
async def get_by_user(user_id) -> List[Document]
async def save(document) -> Document
async def delete(document_id) -> bool
async def exists(document_id) -> bool
async def get_by_storage_path(storage_path) -> Document
```

### **ChunkRepository**
```python
async def get_by_id(chunk_id) -> Chunk
async def get_by_document(document_id) -> List[Chunk]
async def save(chunk) -> Chunk
async def save_batch(chunks) -> List[Chunk]
async def delete_by_document(document_id) -> int
async def search_by_embedding(query_embedding, user_id, limit) -> List[Chunk]
async def count_by_document(document_id) -> int
```

---

## ⚙️ Domain Services

### **1. ChunkingDomainService** - Text Chunking Logic

```python
service = ChunkingDomainService(max_chars=1000, overlap=200)

# Chunk text into pieces
chunks = service.chunk_text("Long text here...")
# Returns: List of (content, index) tuples

# Estimate tokens
tokens = service.estimate_tokens("Some text")

# Validate chunk size
is_valid = service.validate_chunk_size("Chunk content")
```

**Business Rules:**
- ✅ Chunks ~1000 characters
- ✅ 200 character overlap for context
- ✅ Break at sentence boundaries
- ✅ Track chunk index

---

### **2. TextCleaner** - Text Sanitization

```python
# Clean text for database
cleaned = TextCleaner.clean(text)

# Check if valid
is_valid = TextCleaner.is_valid(text)

# Normalize whitespace
normalized = TextCleaner.normalize_whitespace(text)

# Remove control characters
clean = TextCleaner.remove_control_characters(text)
```

**Business Rules:**
- ✅ Remove null bytes (PostgreSQL compatibility)
- ✅ Handle Unicode encoding errors
- ✅ Normalize whitespace
- ✅ Preserve meaningful content

---

### **3. TitleGenerator** - Smart Title Generation

```python
# Generate title from first message
title = TitleGenerator.generate_from_message("How do I build a startup?")
# Returns: "How do I build a startup"

# Extract keywords
keywords = TitleGenerator.extract_keywords("Message here", max_keywords=3)
```

**Business Rules:**
- ✅ Max 50 characters
- ✅ Extract from first sentence
- ✅ Capitalize properly
- ✅ Fallback to "New Conversation"

---

## 🎯 Value Objects

### **Embedding** - Immutable Vector

```python
# Create embedding
embedding = Embedding.from_list([0.1, 0.2, 0.3, ...])

# Get dimension
dim = embedding.dimension()  # 384 for MiniLM

# Convert back to list
vector = embedding.to_list()

# Immutable - cannot be changed!
# embedding.vector[0] = 0.5  # ❌ Error!
```

---

## ⚠️ Domain Exceptions

### **Not Found Exceptions**
```python
raise ConversationNotFoundException(conversation_id)
raise MessageNotFoundException(message_id)
raise DocumentNotFoundException(document_id)
raise ChunkNotFoundException(chunk_id)
```

### **Validation Exception**
```python
raise ValidationException("Title cannot be empty", field="title")
```

### **Access Denied Exception**
```python
raise AccessDeniedException("Conversation", conversation_id, user_id)
```

---

## ✨ Key Features

### **1. Zero External Dependencies** ✅

NO imports from:
- ❌ FastAPI
- ❌ Supabase
- ❌ Groq
- ❌ SentenceTransformers
- ❌ Any framework or library

ONLY Python standard library!

---

### **2. Testable** ✅

Can test everything without:
- ❌ Database
- ❌ API keys
- ❌ Network
- ❌ File system

Just pure logic testing!

---

### **3. Clear Business Rules** ✅

Every entity has explicit validation:
```python
# This will raise ValueError
conversation = Conversation(user_id="", title="")  # ❌ Empty user_id

# This will work
conversation = Conversation(user_id="user123", title="My Chat")  # ✅
```

---

### **4. Type Safety** ✅

Using Python dataclasses and type hints:
```python
@dataclass
class Message:
    conversation_id: str
    content: str
    is_ai: bool
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)
```

---

## 🧪 How to Test

### **Test Entities:**

```python
def test_conversation_validation():
    # Should raise error for empty user_id
    with pytest.raises(ValueError):
        Conversation(user_id="", title="Test")

def test_conversation_update_title():
    conv = Conversation(user_id="user123", title="Old Title")
    conv.update_title("New Title")
    assert conv.title == "New Title"
    assert conv.updated_at > conv.created_at

def test_conversation_ownership():
    conv = Conversation(user_id="user123", title="Test")
    assert conv.is_owned_by("user123") == True
    assert conv.is_owned_by("other_user") == False
```

### **Test Domain Services:**

```python
def test_chunking_service():
    service = ChunkingDomainService(max_chars=100, overlap=20)
    text = "A" * 250  # Long text
    chunks = service.chunk_text(text)
    
    assert len(chunks) > 1  # Multiple chunks
    assert all(len(content) <= 120 for content, _ in chunks)  # Within limit

def test_text_cleaner():
    dirty_text = "Hello\x00World\r\n\r\n\r\nTest"
    clean_text = TextCleaner.clean(dirty_text)
    
    assert "\x00" not in clean_text  # Null bytes removed
    assert clean_text == "HelloWorld\n\nTest"

def test_title_generator():
    message = "How do I build a successful startup?"
    title = TitleGenerator.generate_from_message(message)
    
    assert len(title) <= 50
    assert title == "How do I build a successful startup"
```

---

## 📊 What This Achieves

### **Before (Current Architecture):**

```python
# app/services/chunk_service.py
class ChunkingService:
    @staticmethod
    def chunk_text(text: str):
        # Mixed concerns: business logic + implementation details
        # Directly used by routes
        # Hard to test
        # Tightly coupled
        pass
```

### **After (Clean Architecture):**

```python
# domain/services/chunking_service.py
class ChunkingDomainService:
    def chunk_text(self, text: str) -> List[Tuple[str, int]]:
        # Pure business logic
        # No dependencies
        # Easy to test
        # Returns domain objects
        pass

# infrastructure/implementations will use this
# application/use_cases will orchestrate this
# presentation/routes will never directly touch this
```

---

## 🎯 Benefits Achieved

| Aspect | Before | After |
|--------|--------|-------|
| **Dependencies** | Mixed with Supabase, Groq | Zero |
| **Testability** | Need real DB | Pure unit tests |
| **Business Logic** | Scattered | Centralized |
| **Validation** | Implicit | Explicit |
| **Type Safety** | Some | Complete |
| **Maintainability** | Medium | High |

---

## 🚀 Next Steps

### **Phase 2: Application Layer** (Next)

Create use cases that **orchestrate** domain logic:
- ✅ SendMessage use case
- ✅ CreateConversation use case
- ✅ UploadDocument use case
- ✅ EmbedDocument use case
- ✅ SearchDocuments use case

### **Phase 3: Infrastructure Layer**

Implement repository interfaces:
- ✅ Supabase repositories
- ✅ Groq LLM provider
- ✅ SentenceTransformer embeddings
- ✅ File storage

### **Phase 4: Presentation Layer**

Refactor FastAPI routes:
- ✅ Thin controllers
- ✅ Dependency injection
- ✅ Use case delegation

---

## 💡 How to Use

### **Import Entities:**

```python
from domain.entities import Conversation, Message, Document, Chunk

# Create entities
conversation = Conversation(user_id="user123", title="My Chat")
message = Message(
    conversation_id=conversation.id,
    content="Hello AI!",
    is_ai=False
)
```

### **Import Services:**

```python
from domain.services import ChunkingDomainService, TextCleaner, TitleGenerator

# Use services
chunker = ChunkingDomainService()
chunks = chunker.chunk_text(text)

cleaned_text = TextCleaner.clean(dirty_text)
title = TitleGenerator.generate_from_message(first_message)
```

### **Import Exceptions:**

```python
from domain.exceptions import (
    ConversationNotFoundException,
    ValidationException,
    AccessDeniedException
)

# Raise domain exceptions
if not conversation:
    raise ConversationNotFoundException(conversation_id)

if not conversation.is_owned_by(user_id):
    raise AccessDeniedException("Conversation", conversation_id, user_id)
```

---

## ✅ Phase 1 Status

- [x] **Entities** - 4 core business objects
- [x] **Repositories** - 4 interface contracts
- [x] **Domain Services** - 3 pure business logic services
- [x] **Value Objects** - Embedding value object
- [x] **Exceptions** - 5 domain exception types
- [x] **Documentation** - This guide

**DOMAIN LAYER COMPLETE!** 🎉

---

## 🎓 What You Learned

1. **Entities** = Business objects with behavior + validation
2. **Repositories** = Interfaces (contracts) for data access
3. **Domain Services** = Pure business logic with no dependencies
4. **Value Objects** = Immutable values with business meaning
5. **Domain Exceptions** = Business rule violations

**Core Principle:** The domain layer knows NOTHING about infrastructure!

---

**Ready for Phase 2?** Let's create the Application Layer (Use Cases)! 🚀

