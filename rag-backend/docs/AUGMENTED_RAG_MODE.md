# Augmented RAG Mode - General Knowledge + Vault Context

## Overview

The system now operates in **Augmented RAG mode**, where the LLM can answer questions using:
1. **Vault documents** (when relevant context is found)
2. **General knowledge** (when context is missing or insufficient)

This is different from strict RAG mode, which only allowed answers from documents.

## Key Changes

### Before (Strict RAG)
- ❌ Only answered from document context
- ❌ Returned "Not found in project knowledge" if answer wasn't in documents
- ❌ Required document context to generate answers

### After (Augmented RAG)
- ✅ Uses document context when available and relevant
- ✅ Falls back to general knowledge when context is missing
- ✅ Can answer questions even without any documents
- ✅ Combines both sources for comprehensive answers

## How It Works

### Flow

```
User Question
    ↓
1. Search vault documents (vector similarity)
    ↓
2. Retrieve relevant chunks (if any)
    ↓
3. Build context from chunks
    ↓
4. LLM generates answer using:
   - Document context (if available)
   - General knowledge (always available)
    ↓
5. Return answer with sources (if documents were used)
```

### Prompt Structure

**System Message:**
```
You are FounderGPT, a senior AI tech lead and knowledgeable assistant.

Rules:
- Follow user constraints STRICTLY.
- Use the provided context from vault documents when relevant, but you can also use your general knowledge.
- If the context contains relevant information, prioritize it and incorporate it into your answer.
- If the context doesn't have the answer, use your general knowledge to provide a helpful response.
- Do NOT mention source documents in your answer (sources are shown separately).
- Provide comprehensive, accurate answers using both context and your knowledge.
```

**User Prompt:**
```
RELEVANT CONTEXT FROM VAULT DOCUMENTS (if available):
[Document chunks here]

USER QUESTION:
[User's question]

FORMAT REQUIREMENTS:
[Constraints if any]

Provide a helpful answer using the context above if relevant, or your general knowledge:
```

## Behavior Examples

### Example 1: Question with Relevant Document Context
**User:** "What is RAG?"
**Vault:** Contains documents about RAG
**Result:** LLM uses vault context + general knowledge for comprehensive answer

### Example 2: Question without Document Context
**User:** "What is machine learning?"
**Vault:** No relevant documents
**Result:** LLM answers using general knowledge ✅ (previously would return error)

### Example 3: Question with Partial Context
**User:** "How does RAG work in our system?"
**Vault:** Contains some relevant docs but incomplete
**Result:** LLM combines vault context + general knowledge to fill gaps

### Example 4: General Question
**User:** "What is the capital of France?"
**Vault:** No relevant documents
**Result:** LLM answers using general knowledge ✅

## Benefits

1. **Better UX**: Users get answers even when documents don't have the information
2. **Comprehensive answers**: Combines document-specific info with general knowledge
3. **No dead ends**: System always provides helpful responses
4. **Flexible**: Works with or without documents

## Source Attribution

- **Sources shown**: When documents are used, they appear in the `sources` field
- **No sources**: When only general knowledge is used, `sources` will be empty
- **Mixed**: When both are used, sources show which documents contributed

## Configuration

No configuration needed - this is the default behavior now.

## Migration Notes

**Breaking Changes:** None - this is backward compatible.

**Behavior Changes:**
- System no longer returns "Not found in documents" errors
- Answers can now come from general knowledge
- Context is supplementary, not required

## Future Enhancements

Potential improvements:
1. **Haystack integration**: For more sophisticated document retrieval and ranking
2. **Confidence scoring**: Indicate when answer is from documents vs. general knowledge
3. **Hybrid search**: Combine vector search with keyword search
4. **Document prioritization**: Weight certain documents higher

## Haystack Integration (Future)

If you want to integrate Haystack for more advanced RAG:

**Benefits:**
- Better document retrieval with multiple strategies
- Hybrid search (vector + keyword)
- Document ranking and filtering
- Pipeline-based architecture

**Considerations:**
- Additional dependency
- More complex setup
- May require architecture changes

**Current System:**
- Simple vector search (works well for most cases)
- Fast and lightweight
- Easy to maintain

The current system works well for most use cases. Haystack would be beneficial if you need:
- Complex multi-step retrieval
- Multiple document sources
- Advanced ranking algorithms
- Pipeline orchestration

