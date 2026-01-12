"""
Groq LLM Provider Implementation

Implements the LLMProvider interface using Groq API.
"""
import os
import logging
from typing import List, Dict, Optional
from application.interfaces.llm_provider import LLMProvider

try:
    from groq import Groq
except ImportError:
    Groq = None


class GroqLLMProvider(LLMProvider):
    """
    Groq LLM Provider implementation.
    
    This is an INFRASTRUCTURE implementation of the Application interface.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "llama-3.1-8b-instant"):
        """
        Initialize Groq provider.
        
        Args:
            api_key: Groq API key (defaults to env var)
            model: Model name to use
        """
        if Groq is None:
            raise ImportError("groq package not installed. Run: pip install groq")
        
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not provided and not found in environment")
        
        self.model = model
        self.client = Groq(api_key=self.api_key)
        
        logging.info(f"Groq LLM Provider initialized with model: {self.model}")
    
    async def generate(
        self, 
        prompt: str,
        system_message: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate text completion using Groq.
        
        Implementation of LLMProvider interface.
        """
        try:
            messages = []
            
            if system_message:
                messages.append({"role": "system", "content": system_message})
            
            messages.append({"role": "user", "content": prompt})
            
            # Call Groq API
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Extract response
            if not completion.choices or len(completion.choices) == 0:
                raise ValueError("No response from Groq API")
            
            response_text = completion.choices[0].message.content
            
            if not response_text:
                raise ValueError("Empty response from Groq API")
            
            return response_text.strip()
            
        except Exception as e:
            logging.error(f"Groq generation error: {e}")
            raise RuntimeError(f"Groq API error: {str(e)}") from e
    
    async def generate_with_history(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.0,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate text with conversation history.
        
        Implementation of LLMProvider interface.
        """
        try:
            # Call Groq API with full message history
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Extract response
            if not completion.choices or len(completion.choices) == 0:
                raise ValueError("No response from Groq API")
            
            response_text = completion.choices[0].message.content
            
            if not response_text:
                raise ValueError("Empty response from Groq API")
            
            return response_text.strip()
            
        except Exception as e:
            logging.error(f"Groq generation error: {e}")
            raise RuntimeError(f"Groq API error: {str(e)}") from e
    
    def get_model_name(self) -> str:
        """Get the model name being used"""
        return self.model

