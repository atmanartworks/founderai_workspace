# Document Context Fix - "This Document" Query Handling

## Problem

When users ask vague questions like "EXPLAIN THIS DOCUMENT" or "what is in this document", the system was searching across ALL documents and often returning results from the wrong document (e.g., log.txt instead of the newly uploaded document).

## Root Causes

1. **Vague queries**: "this document" doesn't specify which document
2. **No document context**: System searches all user documents without knowing which one to prioritize
3. **Vector search bias**: Most similar chunks might come from a different document with more content

## Solution Implemented

### 1. Optional `vault_id` Parameter
Added optional `vault_id` to `ChatRequest` for explicit document selection:

```python
class ChatRequest(BaseModel):
    conversation_id: str = None
    message: str
    user_id: str
    top_k: int = 5
    vault_id: str = None  # Optional: specify which document to query
```

### 2. Vague Query Detection
Detects vague queries that need document context:

```python
is_vague_query = any(phrase in message_lower for phrase in [
    "this document", "this file", "this doc", "the document", "the file",
    "explain this", "what is this", "tell me about this"
])
```

### 3. Document Inference Strategy

When a vague query is detected and no `vault_id` is provided, the system uses a two-step inference:

**Strategy 1: Conversation History**
- Checks recent messages in the conversation
- Finds the most recently used document
- Uses that document's `vault_id`

**Strategy 2: Recent Uploads (Fallback)**
- If no conversation history, checks files uploaded in the last hour
- Uses the most recently uploaded file

### 4. Document Filtering
When `vault_id` is known (explicit or inferred):
- Filters search results to only chunks from that document
- Returns helpful error if document not found or not embedded

### 5. Question Rewrite Preservation
For vague queries with inferred document context:
- Skips question rewrite to preserve original intent
- Keeps "this document" reference for better document-specific search

## Code Flow

```
User: "EXPLAIN THIS DOCUMENT IN 6 LINES"
    ↓
1. Detect vague query: is_vague_query = True
    ↓
2. Check if vault_id provided → No
    ↓
3. Infer from conversation history:
   - Get recent messages
   - Find most recently used document
   - Extract vault_id
    ↓
4. If no history, check recent uploads (last hour)
    ↓
5. Filter search to that vault_id
    ↓
6. Return answer from correct document ✅
```

## Usage

### Frontend Integration (Recommended)

When user uploads a file and asks about it, pass the `vault_id`:

```typescript
const response = await ragApi.sendMessage({
  message: "Explain this document",
  user_id: userId,
  conversation_id: conversationId,
  vault_id: uploadedFile.vault_id  // Explicit document selection
});
```

### Automatic Inference (Fallback)

If `vault_id` is not provided, the system will:
1. Check conversation history
2. Fall back to recent uploads
3. If still no context, search all documents (original behavior)

## Benefits

✅ **Correct document selection**: Vague queries now target the right document
✅ **Better UX**: Users don't need to specify document name
✅ **Backward compatible**: Still works if no vault_id provided
✅ **Smart inference**: Uses conversation context intelligently

## Edge Cases Handled

1. **Document not embedded**: Returns helpful error message
2. **No conversation history**: Falls back to recent uploads
3. **No recent uploads**: Falls back to searching all documents
4. **Multiple documents in conversation**: Uses most recently referenced

## Testing

### Test Case 1: Explicit vault_id
```bash
POST /api/chat/message
{
  "message": "Explain this document",
  "user_id": "user123",
  "vault_id": "doc-uuid-here"
}
```
Expected: Only searches that specific document

### Test Case 2: Vague query with history
1. Upload document A
2. Ask question about document A (gets answer)
3. Upload document B
4. Ask "explain this document"
Expected: Should use document B (most recent)

### Test Case 3: Vague query without history
1. Upload document A
2. Immediately ask "explain this document"
Expected: Should use document A (recent upload)

## Files Modified

- `app/routes/chat.py`
  - Added `vault_id` parameter to `ChatRequest`
  - Added vague query detection
  - Added document inference logic
  - Added document filtering
  - Improved question rewrite handling

## Future Improvements

1. **Frontend integration**: Update frontend to pass `vault_id` when user asks about uploaded file
2. **Document selection UI**: Allow users to select which document to query
3. **Multi-document queries**: Support queries across multiple specified documents
4. **Document metadata**: Use document titles/names for better matching

