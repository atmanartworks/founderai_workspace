# Critical Bug Fixes - Document Retrieval & Hallucination

## Issues Fixed

### 1. **Wrong Document Retrieval (Critical Security Issue)**
**Problem**: The chat endpoint was searching across ALL users' documents, not just the current user's documents.

**Root Cause**: Missing `user_id_input` parameter in the `search_embeddings` RPC call.

**Fix**: Added `user_id_input: payload.user_id` to the RPC call in `chat.py`:
```python
rpc = supabase.rpc("search_embeddings", {
    "query_embedding": query_embedding, 
    "user_id_input": payload.user_id,  # FIX: Filter by user_id
    "match_count": payload.top_k
}).execute()
```

**Impact**: 
- ✅ Users now only see their own documents
- ✅ Prevents data leakage between users
- ✅ Matches behavior of `/api/search/semantic-search` endpoint

---

### 2. **Hallucination from Empty/Unreadable Files**
**Problem**: When documents had no readable text (empty extraction), the system would still generate answers by hallucinating content.

**Root Cause**: 
- Empty chunks were being included in context
- No validation for minimal/empty context before generating answers

**Fix**: 
1. **Skip empty chunks** during context building:
```python
chunk_content = c.get("content", "").strip()
# Skip empty or minimal chunks (prevents hallucination)
if not chunk_content or len(chunk_content) < 10:
    continue
```

2. **Validate total context** before generation:
```python
# Validate we have meaningful context (prevents hallucination)
if not context_pieces or total_context_length < 20:
    return ChatResponse(
        response="The documents found don't contain readable text, or the text is too minimal to answer your question.",
        sources=[],
        message_id=mid,
        conversation_id=conversation_id
    )
```

**Impact**:
- ✅ No more hallucinated answers from empty files
- ✅ Clear error message when documents are unreadable
- ✅ Better user experience

---

### 3. **Constraint Enforcement Not Working**
**Problem**: Line constraints (e.g., "explain in 6 lines") were not being strictly enforced.

**Root Cause**: 
- Answer enforcer was truncating lines but not limiting line length
- LLM might generate very long single lines

**Fix**: Enhanced `enforce_constraints()` to:
1. **Strictly truncate** to exact line count
2. **Limit each line** to ~20 words (as per prompt requirement)
3. **Better handling** of multi-line answers

```python
if lines > 0:
    answer_lines = [line.strip() for line in answer.split("\n") if line.strip()]
    if len(answer_lines) > lines:
        answer_lines = answer_lines[:lines]
    
    # Also limit each line to ~20 words max
    trimmed_lines = []
    for line in answer_lines:
        words = line.split()
        if len(words) > 20:
            line = " ".join(words[:20])
        trimmed_lines.append(line)
    
    answer = "\n".join(trimmed_lines)
```

**Impact**:
- ✅ Line constraints now strictly enforced
- ✅ Answers respect both line count and line length
- ✅ Better compliance with user requests

---

## Additional Improvements

### Logging Added
Added logging to help debug constraint extraction and question rewriting:
```python
logging.info(f"Extracted constraints: {constraints} from message: '{payload.message}'")
logging.info(f"Rewritten question: '{rewritten_question}'")
```

---

## Testing Recommendations

### Test Case 1: User Isolation
```bash
# User A uploads document A
# User B uploads document B
# User A asks question - should ONLY see document A
# User B asks question - should ONLY see document B
```

### Test Case 2: Empty File Handling
```bash
# Upload a file with no readable text (e.g., image, corrupted PDF)
# Ask a question about it
# Should return: "The documents found don't contain readable text..."
```

### Test Case 3: Line Constraints
```bash
# Ask: "Explain X in 3 lines"
# Verify answer is exactly 3 lines (or fewer)
# Verify each line is reasonable length (~20 words max)
```

---

## Files Modified

1. `app/routes/chat.py`
   - Added `user_id_input` to RPC call
   - Added empty chunk filtering
   - Added context validation
   - Added logging

2. `app/services/answer_enforcer.py`
   - Enhanced line constraint enforcement
   - Added line length limiting

---

## Migration Notes

**No database migration required** - these are code-level fixes.

**Backward Compatibility**: 
- ✅ All existing API calls continue to work
- ✅ No breaking changes to request/response format
- ✅ Only behavior improvements

---

## Security Impact

**HIGH**: The user_id filtering fix prevents cross-user data access, which is a critical security issue.

**Recommendation**: Review all other endpoints that query `document_chunks` to ensure they filter by `user_id`.

