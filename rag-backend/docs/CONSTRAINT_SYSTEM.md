# Constraint Extraction & Question Rewriting System

## Overview

This system enhances the RAG chat endpoint with intelligent constraint extraction, question rewriting, and strict answer enforcement. It solves common problems:

- ✅ **Vague questions** → Automatically rewritten for clarity
- ✅ **Ignored constraints** (e.g., "3 lines") → Strictly enforced
- ✅ **Uncontextual questions** → RAG guard ensures context-only answers
- ✅ **Hallucinations** → Context-only mode prevents made-up information

## Architecture

### Flow

```
User Input
    ↓
1. Extract Constraints (lines, short, steps)
    ↓
2. Rewrite Question (OpenAI gpt-4o-mini)
    ↓
3. RAG Retrieval (using rewritten question)
    ↓
4. Generate Answer (strict prompt with constraints)
    ↓
5. Enforce Constraints (post-processing fail-safe)
    ↓
Final Answer
```

### Services

#### 1. `constraint_extractor.py`
Extracts user constraints from natural language:
- **Lines**: "3 lines", "5 lines", "in 2 lines"
- **Short**: "short", "brief", "concise", "quick"
- **Steps**: "step", "steps", "step-by-step", "numbered"

#### 2. `question_rewrite.py`
Uses OpenAI (gpt-4o-mini) to rewrite vague questions while preserving:
- Original intent
- All constraints
- Specific requirements

**Fallback**: Returns original question if OpenAI unavailable.

#### 3. `answer_enforcer.py`
Post-processes answers to enforce constraints:
- **Line count**: Truncates to exact number of lines
- **Short mode**: Limits to 3 sentences if no line count
- **Steps mode**: Ensures numbered format

#### 4. `embedding_service.py` (Updated)
Enhanced `generate()` method now accepts:
- `lines`: Number of lines to limit answer
- `short`: Brief answer flag
- `steps`: Step-by-step format flag
- `context`: Document context (for strict RAG mode)
- `question`: User question (for strict RAG mode)

When `context` and `question` are provided, uses **strict RAG mode**:
- System prompt: "FounderGPT, senior AI tech lead"
- Rules: Use ONLY provided context
- Format: Enforces constraints in prompt
- Temperature: 0.2 (lower for constraint compliance)

## Usage

The system is **automatically active** on `/api/chat/message`. No changes needed to existing API calls.

### Example Requests

**With line constraint:**
```json
{
  "message": "Explain RAG in 3 lines",
  "user_id": "user123"
}
```

**With short constraint:**
```json
{
  "message": "Give me a brief summary of the architecture",
  "user_id": "user123"
}
```

**With steps constraint:**
```json
{
  "message": "How do I set this up? Give me steps",
  "user_id": "user123"
}
```

**Combined constraints:**
```json
{
  "message": "Explain the process in 5 short steps",
  "user_id": "user123"
}
```

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Required for question rewriting (uses gpt-4o-mini by default)
- `OPENAI_REWRITE_MODEL`: Optional, defaults to `gpt-4o-mini` (cheap model for rewriting)

### Model Selection

Question rewriting uses `gpt-4o-mini` (cheap, fast) by default. You can override:
```bash
OPENAI_REWRITE_MODEL=gpt-4o-mini
```

Answer generation uses your configured `OPENAI_MODEL` (from `.env`).

## Benefits

1. **Invisible to users**: No prompt engineering needed
2. **Handles vague questions**: Automatic clarification
3. **Strict constraint compliance**: Multi-layer enforcement
4. **Context-only answers**: Prevents hallucinations
5. **Production-ready**: Used in real SaaS AI products

## Technical Details

### Constraint Extraction
- Uses regex patterns to detect constraints
- Case-insensitive matching
- Supports natural language variations

### Question Rewriting
- Single OpenAI API call (gpt-4o-mini)
- Preserves all constraints and intent
- Falls back gracefully if OpenAI unavailable

### Answer Generation
- **Strict mode**: When context + question provided
- **Standard mode**: Backward compatible with old prompts
- Temperature: 0.2 for constrained answers, 0.3 for standard

### Post-Enforcement
- Line truncation: Takes first N non-empty lines
- Short mode: Limits to 3 sentences
- Steps mode: Adds numbering if missing

## Testing

Test with various constraint combinations:

```bash
# Line constraint
curl -X POST http://localhost:8000/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{"message": "What is RAG? Answer in 2 lines.", "user_id": "test"}'

# Short constraint
curl -X POST http://localhost:8000/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{"message": "Briefly explain embeddings", "user_id": "test"}'

# Steps constraint
curl -X POST http://localhost:8000/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I upload files? Give steps", "user_id": "test"}'
```

## Troubleshooting

**Question rewrite not working?**
- Check `OPENAI_API_KEY` is set
- Check OpenAI API quota/rate limits
- System falls back to original question if rewrite fails

**Constraints not enforced?**
- Check logs for constraint extraction
- Verify OpenAI model is responding correctly
- Post-enforcer should catch any missed constraints

**Answers too long despite constraints?**
- Post-enforcer truncates, but LLM should follow prompt
- Lower temperature (already 0.2) helps
- Check if constraints are being extracted correctly

