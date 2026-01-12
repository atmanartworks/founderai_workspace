# Query Classification - Smart RAG Routing

## Problem Fixed

Previously, simple greetings like "hii" or "hello" would:
- ❌ Trigger full RAG document retrieval
- ❌ Generate verbose, irrelevant responses
- ❌ Waste API calls and resources
- ❌ Provide poor user experience

## Solution

Added **Query Classification** to intelligently route queries:
- ✅ Simple greetings → Quick friendly response (no RAG)
- ✅ Conversational queries → Simple acknowledgment (no RAG)
- ✅ Actual questions → Full RAG retrieval + LLM response

## How It Works

### Query Classifier

The `query_classifier.py` service analyzes queries and determines:

```python
{
    "needs_rag": bool,        # Whether to retrieve documents
    "is_greeting": bool,      # Simple greeting
    "is_conversational": bool, # Conversational query
    "is_question": bool       # Actual question
}
```

### Classification Rules

**Greetings (No RAG):**
- "hi", "hello", "hey"
- "how are you"
- "what's up"
- "thanks", "thank you"

**Conversational (No RAG):**
- "ok", "okay", "sure"
- "got it", "understood"
- "please"

**Questions (RAG Needed):**
- Contains question words: what, how, why, when, where, who, which
- Contains question mark: ?
- Contains action words: explain, tell, describe, show, list, find

## Flow

```
User Input: "hii"
    ↓
Query Classifier: {is_greeting: true, needs_rag: false}
    ↓
Return: "Hello! How can I help you today?"
    ↓
✅ No RAG retrieval
✅ No document search
✅ Fast response
```

```
User Input: "What is RAG?"
    ↓
Query Classifier: {is_question: true, needs_rag: true}
    ↓
RAG Retrieval → Documents → LLM → Answer
    ↓
✅ Full RAG pipeline
✅ Document context used
✅ Comprehensive answer
```

## Benefits

1. **Better UX**: Simple greetings get simple responses
2. **Faster**: No unnecessary document searches
3. **Cost-effective**: Fewer API calls
4. **Smarter**: Only uses RAG when needed

## Examples

### Greeting
**Input:** "hii"
**Response:** "Hello! How can I help you today?"
**RAG:** ❌ Skipped

### Question
**Input:** "What is machine learning?"
**Response:** [Full answer with document context if available]
**RAG:** ✅ Used

### Conversational
**Input:** "ok"
**Response:** "Got it! How can I help you?"
**RAG:** ❌ Skipped

## Implementation

### Files Modified

1. **`app/services/query_classifier.py`** (New)
   - Classifies queries using regex patterns
   - Determines if RAG is needed

2. **`app/routes/chat.py`**
   - Added query classification at start
   - Early return for greetings/conversational
   - Conditional RAG retrieval

### Code Flow

```python
# 1. Classify query
query_classification = classify_query(payload.message)

# 2. Handle greetings
if query_classification["is_greeting"]:
    return simple_greeting_response()

# 3. Handle conversational
if query_classification["is_conversational"]:
    return simple_acknowledgment()

# 4. Only do RAG if needed
if query_classification["needs_rag"]:
    chunks = perform_rag_retrieval()
else:
    chunks = []  # Skip RAG

# 5. Generate response (with or without context)
response = await generate_answer(context=chunks)
```

## Testing

### Test Cases

1. **Greeting**
   ```bash
   POST /api/chat/message
   {"message": "hi", "user_id": "test"}
   ```
   Expected: Simple greeting, no sources

2. **Question**
   ```bash
   POST /api/chat/message
   {"message": "What is RAG?", "user_id": "test"}
   ```
   Expected: Full RAG response with sources

3. **Conversational**
   ```bash
   POST /api/chat/message
   {"message": "ok", "user_id": "test"}
   ```
   Expected: Simple acknowledgment

## Future Enhancements

Potential improvements:
1. **Learning from user behavior**: Track which queries need RAG
2. **Context-aware classification**: Consider conversation history
3. **Custom patterns**: Allow users to define classification rules
4. **Confidence scoring**: Rate how certain the classification is

