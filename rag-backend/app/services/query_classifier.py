# app/services/query_classifier.py

import re
from typing import Dict

def classify_query(query: str) -> Dict[str, bool]:
    """
    Classifies the query to determine if RAG retrieval is needed.
    
    Returns:
        {
            "needs_rag": bool,  # Whether to retrieve documents
            "is_greeting": bool,  # Simple greeting
            "is_conversational": bool,  # Conversational query
            "is_question": bool  # Actual question that needs answering
        }
    """
    query_lower = query.lower().strip()
    
    # Simple greetings - no RAG needed
    greetings = [
        r'^(hi|hello|hey|greetings|good morning|good afternoon|good evening)[\s!.,]*$',
        r'^(hi|hello|hey)\s+(there|everyone|all)[\s!.,]*$',
        r'^how\s+(are\s+you|do\s+you\s+do)[\s?.,]*$',
        r'^what\'?s\s+up[\s?.,]*$',
        r'^thanks?\s*(you|a\s+lot|so\s+much)?[\s!.,]*$',
        r'^(thank\s+you|thanks)[\s!.,]*$',
    ]
    
    is_greeting = any(re.match(pattern, query_lower) for pattern in greetings)
    
    # Very short queries (1-2 words) that aren't questions
    is_very_short = len(query.split()) <= 2 and not any(word in query_lower for word in ['what', 'how', 'why', 'when', 'where', 'who', 'which', '?'])
    
    # Conversational queries that don't need documents
    conversational = [
        r'^(ok|okay|alright|sure|yes|no|yep|nope)[\s!.,]*$',
        r'^(got\s+it|understood|i\s+see)[\s!.,]*$',
        r'^(please|pls)[\s!.,]*$',
    ]
    
    is_conversational = any(re.match(pattern, query_lower) for pattern in conversational)
    
    # Questions that need RAG (contain question words or question marks)
    has_question_word = any(word in query_lower for word in [
        'what', 'how', 'why', 'when', 'where', 'who', 'which', 'explain', 'tell', 'describe',
        'show', 'list', 'give', 'provide', 'find', 'search', 'document', 'file'
    ])
    has_question_mark = '?' in query
    
    # File listing queries - special handling (just listing, not overview)
    # Note: "overview" and "summary" queries should go through RAG to get content from all files
    is_file_list_query = any(phrase in query_lower for phrase in [
        'what files', 'which files', 'list files', 'show files', 'files you have',
        'files in vault', 'files do you have', 'files can you access',
        'what documents', 'which documents', 'list documents', 'show documents',
        'documents in vault', 'documents do you have', 'documents can you access'
    ]) and not any(phrase in query_lower for phrase in [
        'overview', 'summary', 'tell me about', 'describe', 'explain'
    ])
    
    is_question = has_question_word or has_question_mark
    
    # Determine if RAG is needed
    # RAG needed if: it's a question AND not a simple greeting
    needs_rag = is_question and not is_greeting and not is_very_short and not is_conversational
    
    return {
        "needs_rag": needs_rag,
        "is_greeting": is_greeting,
        "is_conversational": is_conversational,
        "is_question": is_question,
        "is_file_list_query": is_file_list_query
    }

