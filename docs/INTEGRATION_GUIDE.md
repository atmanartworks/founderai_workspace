# 🔄 Integration Guide - Using Clean Architecture in Existing Code

## ✅ All Repositories Completed!

All infrastructure implementations are now complete:
- ✅ SupabaseConversationRepository
- ✅ SupabaseMessageRepository
- ✅ SupabaseDocumentRepository  
- ✅ SupabaseChunkRepository (with vector search!)

---

## 🚀 Quick Integration - Replace Components Incrementally

You can start using Clean Architecture components RIGHT NOW without refactoring everything!

### **Step 1: Replace Groq API Calls**

**Before:**
```python
# app/routes/chat.py
from groq import Groq
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

response = groq_client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[{"role": "user", "content": prompt}]
)
```

**After (using Clean Architecture):**
```python
# app/routes/chat.py
from infrastructure.ai.groq_provider import GroqLLMProvider

# Initialize once (can be module-level)
llm_provider = GroqLLMProvider()

# Use in route
response = await llm_provider.generate(
    prompt=prompt,
    system_message="You are a helpful assistant",
    temperature=0.0
)
```

**Benefits:**
- ✅ Cleaner interface
- ✅ Better error handling
- ✅ Easy to test (mock the provider)
- ✅ Easy to swap (change to OpenAI later)

---

### **Step 2: Replace Embedding Calls**

**Before:**
```python
# app/routes/chat.py
from app.services.embedding_service import embedding_service

query_embedding = await embedding_service.embed_text(payload.message)
```

**After (using Clean Architecture):**
```python
# app/routes/chat.py
from infrastructure.ai.sentence_transformer_provider import SentenceTransformerEmbeddingProvider

# Initialize once
embedding_provider = SentenceTransformerEmbeddingProvider()

# Use in route
embedding = await embedding_provider.embed_text(payload.message)
query_embedding = embedding.to_list()  # Convert to list for Supabase
```

**Benefits:**
- ✅ Returns domain `Embedding` value object
- ✅ Batch support for efficiency
- ✅ Consistent interface

---

### **Step 3: Replace Direct Supabase Calls with Repositories**

**Before:**
```python
# Direct database access
existing = supabase.table("conversations").select("id").eq("id", conversation_id).execute()
if not existing.data:
    supabase.table("conversations").insert({...}).execute()
```

**After (using Clean Architecture):**
```python
# Use repository
from infrastructure.database.supabase.conversation_repository_impl import SupabaseConversationRepository
from domain.entities.conversation import Conversation

# Initialize once
conversation_repo = SupabaseConversationRepository(supabase)

# Use in route
conversation = await conversation_repo.get_by_id(conversation_id)
if not conversation:
    conversation = Conversation(
        user_id=payload.user_id,
        title="New Conversation"
    )
    conversation = await conversation_repo.save(conversation)
```

**Benefits:**
- ✅ Works with domain entities (with validation!)
- ✅ Testable (mock the repository)
- ✅ Database agnostic
- ✅ Business logic in entities

---

### **Step 4: Use Text Cleaner**

**Before:**
```python
# Manual text cleaning
text = text.replace("\x00", "")
text = text.encode("utf-8", "ignore").decode("utf-8", "ignore").strip()
```

**After (using Clean Architecture):**
```python
from domain.services.text_cleaner import TextCleaner

# Use domain service
cleaned_text = TextCleaner.clean(text)

# Validate
if not TextCleaner.is_valid(cleaned_text):
    raise ValueError("Invalid text")
```

---

### **Step 5: Use Chunking Service**

**Before:**
```python
# app/services/chunk_service.py
from app.services.chunk_service import ChunkingService

chunks = ChunkingService.chunk_text(text)
```

**After (using Clean Architecture):**
```python
from domain.services.chunking_service import ChunkingDomainService

# Use domain service
chunker = ChunkingDomainService(max_chars=1000, overlap=200)
chunks = chunker.chunk_text(text)

for content, index in chunks:
    tokens = chunker.estimate_tokens(content)
    # Create domain Chunk entity
```

---

## 📝 Complete Example - Refactored Chat Route

Here's how your `/api/chat/message` route looks using Clean Architecture:

```python
# app/routes/chat.py (REFACTORED VERSION)
import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

# Clean Architecture imports
from infrastructure.ai.groq_provider import GroqLLMProvider
from infrastructure.ai.sentence_transformer_provider import SentenceTransformerEmbeddingProvider
from infrastructure.database.supabase.conversation_repository_impl import SupabaseConversationRepository
from infrastructure.database.supabase.message_repository_impl import SupabaseMessageRepository
from infrastructure.database.supabase.chunk_repository_impl import SupabaseChunkRepository
from infrastructure.database.supabase.document_repository_impl import SupabaseDocumentRepository
from domain.entities.conversation import Conversation
from domain.entities.message import Message
from domain.services.title_generator import TitleGenerator

from app.database import supabase

router = APIRouter(prefix="/api/chat", tags=["chat"])

# Initialize providers once (module level)
llm_provider = GroqLLMProvider()
embedding_provider = SentenceTransformerEmbeddingProvider()
conversation_repo = SupabaseConversationRepository(supabase)
message_repo = SupabaseMessageRepository(supabase)
chunk_repo = SupabaseChunkRepository(supabase)
document_repo = SupabaseDocumentRepository(supabase)

class ChatRequest(BaseModel):
    conversation_id: str = None
    message: str
    user_id: str
    top_k: int = 5

class ChatResponse(BaseModel):
    response: str
    sources: List[str]
    message_id: str
    conversation_id: str

@router.post("/message", response_model=ChatResponse)
async def send_message(payload: ChatRequest):
    """
    Send message using Clean Architecture components.
    
    This is a HYBRID approach - using new components with minimal refactoring.
    """
    try:
        # Get or create conversation (using repository!)
        conversation = None
        if payload.conversation_id:
            try:
                conversation = await conversation_repo.get_by_id(payload.conversation_id)
            except:
                pass
        
        if not conversation:
            # Create new conversation with smart title
            title = TitleGenerator.generate_from_message(payload.message)
            conversation = Conversation(
                user_id=payload.user_id,
                title=title
            )
            conversation = await conversation_repo.save(conversation)
        
        # Save user message (using repository!)
        user_message = Message(
            conversation_id=conversation.id,
            content=payload.message,
            is_ai=False
        )
        user_message = await message_repo.save(user_message)
        
        # Embed query (using provider!)
        embedding = await embedding_provider.embed_text(payload.message)
        query_embedding = embedding.to_list()
        
        # Search chunks (using repository!)
        chunks = await chunk_repo.search_by_embedding(
            query_embedding=query_embedding,
            user_id=payload.user_id,
            limit=payload.top_k
        )
        
        if not chunks:
            # No relevant chunks found
            ai_message = Message(
                conversation_id=conversation.id,
                content="I couldn't find relevant information in your documents.",
                is_ai=True
            )
            ai_message = await message_repo.save(ai_message)
            
            return ChatResponse(
                response=ai_message.content,
                sources=[],
                message_id=ai_message.id,
                conversation_id=conversation.id
            )
        
        # Build context from chunks
        context_pieces = []
        source_files = set()
        
        for chunk in chunks:
            # Get document info
            document = await document_repo.get_by_id(chunk.vault_id)
            if document:
                source_files.add(document.original_name)
                context_pieces.append(
                    f"[{document.original_name}] (chunk {chunk.chunk_index}):\n{chunk.get_content_preview(1000)}"
                )
        
        context = "\n\n---\n\n".join(context_pieces)
        
        # Generate AI response (using provider!)
        prompt = f"""You must answer only using the document context below.
If the answer is not present, say "I cannot find that in your documents."

Document context:
{context}

User question:
{payload.message}

Answer:"""
        
        ai_response = await llm_provider.generate(
            prompt=prompt,
            system_message="You are a helpful assistant. Answer ONLY based on provided context.",
            temperature=0.0
        )
        
        # Save AI message (using repository!)
        ai_message = Message(
            conversation_id=conversation.id,
            content=ai_response,
            is_ai=True,
            used_documents={
                "chunks": [chunk.id for chunk in chunks],
                "files": list(source_files)
            }
        )
        ai_message = await message_repo.save(ai_message)
        
        # Update conversation timestamp
        conversation.touch()
        await conversation_repo.save(conversation)
        
        return ChatResponse(
            response=ai_response,
            sources=list(source_files),
            message_id=ai_message.id,
            conversation_id=conversation.id
        )
        
    except Exception as e:
        raise HTTPException(500, f"Error: {str(e)}")
```

---

## 🎯 Benefits of This Approach

### **1. Gradual Migration** ✅
- Don't need to refactor everything at once
- Replace components one at a time
- Keep existing functionality working

### **2. Immediate Value** ✅
- Better error handling
- Cleaner code
- Type safety with domain entities
- Business validation built-in

### **3. Easy Testing** ✅
```python
# Test with mocks
from unittest.mock import Mock

# Mock repositories
mock_conv_repo = Mock()
mock_msg_repo = Mock()

# Test your route logic
```

### **4. Future-Proof** ✅
- Easy to swap Groq for OpenAI
- Easy to swap Supabase for Postgres
- Database-agnostic code

---

## 📚 What to Replace First

### **Priority 1: Providers** (Easiest, Highest Value)
1. ✅ GroqLLMProvider (replace direct Groq calls)
2. ✅ EmbeddingProvider (replace embedding_service)
3. ✅ StorageProvider (replace direct storage calls)

### **Priority 2: Domain Services** (Easy, Good Value)
1. ✅ TextCleaner (replace manual text cleaning)
2. ✅ ChunkingService (replace old chunk_service)
3. ✅ TitleGenerator (replace hardcoded titles)

### **Priority 3: Repositories** (Medium, Great Value)
1. ✅ ConversationRepository (replace table queries)
2. ✅ MessageRepository (replace table queries)
3. ✅ ChunkRepository (replace RPC calls)
4. ✅ DocumentRepository (replace vault_files queries)

---

## 🔧 Quick Start Checklist

- [ ] Replace Groq API calls with GroqLLMProvider
- [ ] Replace embedding_service with EmbeddingProvider
- [ ] Use TextCleaner for text sanitization
- [ ] Use ChunkingDomainService for chunking
- [ ] Use TitleGenerator for conversation titles
- [ ] Replace conversation queries with ConversationRepository
- [ ] Replace message queries with MessageRepository
- [ ] Replace chunk search with ChunkRepository
- [ ] Test everything works!

---

## 💡 Pro Tips

1. **Initialize providers once** at module level, not in every request
2. **Use domain entities** - they have validation and behavior
3. **Let repositories handle database** - don't mix direct queries
4. **Keep your existing routes** - just replace internal implementation
5. **Test as you go** - verify each replacement works

---

## 🎉 Result

After integration, you'll have:
- ✅ Clean, testable code
- ✅ Domain entities with validation
- ✅ Swappable implementations
- ✅ Better error handling
- ✅ Professional architecture

**All while keeping your API working!** 🚀

---

**Ready to integrate? Start with replacing the LLM provider - it's the easiest win!**

