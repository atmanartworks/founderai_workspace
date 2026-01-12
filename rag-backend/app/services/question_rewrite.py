# app/services/question_rewrite.py

import os
import logging
from typing import Optional
# Import centralized config
from app.config import OPENAI_API_KEY, OPENAI_MODEL

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

# Initialize OpenAI client if available (lazy initialization)
_openai_client = None
_openai_initialized = False

def _get_openai_client():
    """Lazy initialization of OpenAI client"""
    global _openai_client, _openai_initialized
    if not _openai_initialized:
        if OpenAI is None:
            return None
        if not OPENAI_API_KEY:
            return None
        try:
            _openai_client = OpenAI(api_key=OPENAI_API_KEY)
            _openai_initialized = True
            logging.info("Question rewrite service initialized with OpenAI")
        except Exception as e:
            logging.warning(f"Failed to initialize OpenAI for question rewrite: {e}")
            _openai_initialized = True  # Mark as initialized to avoid retrying
    return _openai_client

async def rewrite_question(input_text: str) -> str:
    """
    Rewrites the user's question to be clearer while preserving intent and constraints.
    Uses a cheap OpenAI call (gpt-4o-mini) to clarify vague questions.
    """
    client = _get_openai_client()
    if not client:
        # Fallback: return original if OpenAI not available
        logging.warning("OpenAI not available for question rewrite, using original question")
        return input_text
    
    try:
        model = os.getenv("OPENAI_REWRITE_MODEL", "gpt-4o-mini")
        
        completion = client.chat.completions.create(
            model=model,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": "Rewrite the user's question clearly and precisely. Preserve all intent, constraints (like line counts, format requests), and specific requirements. Do NOT answer the question, only rewrite it to be clearer."
                },
                {
                    "role": "user",
                    "content": input_text
                }
            ],
            max_tokens=200
        )
        
        if completion.choices and completion.choices[0].message.content:
            rewritten = completion.choices[0].message.content.strip()
            logging.debug(f"Question rewritten: '{input_text}' -> '{rewritten}'")
            return rewritten
        else:
            return input_text
    except Exception as e:
        logging.error(f"Question rewrite failed: {e}, using original question")
        return input_text

