# app/services/llm_stream.py

import logging
from typing import Generator, Optional
from openai import OpenAI
from app.config import OPENAI_API_KEY, OPENAI_MODEL

logger = logging.getLogger(__name__)

# Initialize OpenAI client (singleton pattern)
_openai_client: Optional[OpenAI] = None

def _get_openai_client() -> Optional[OpenAI]:
    """Get or initialize OpenAI client."""
    global _openai_client
    if _openai_client is None:
        if not OPENAI_API_KEY:
            logger.error("OPENAI_API_KEY not set - streaming will fail")
            return None
        try:
            _openai_client = OpenAI(api_key=OPENAI_API_KEY)
            logger.info("OpenAI client initialized for streaming")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            return None
    return _openai_client

def stream_llm(
    system_prompt: str,
    user_prompt: str,
    model: Optional[str] = None,
    temperature: float = 0.4,
    max_tokens: int = 2000
) -> Generator[str, None, None]:
    """
    Stream LLM tokens from OpenAI.
    
    Args:
        system_prompt: System message for the LLM
        user_prompt: User message/question
        model: Model to use (defaults to OPENAI_MODEL from config)
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate
    
    Yields:
        Token strings as they are generated
    """
    client = _get_openai_client()
    if not client:
        logger.error("OpenAI client not available for streaming")
        yield "[Error: OpenAI client not initialized]"
        return
    
    model = model or OPENAI_MODEL or "gpt-3.5-turbo"
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True
        )
        
        for chunk in response:
            if chunk.choices and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    yield delta.content
                    
    except Exception as e:
        logger.error(f"Error streaming LLM response: {e}", exc_info=True)
        yield f"[Error: {str(e)}]"
