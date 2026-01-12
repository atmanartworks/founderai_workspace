"""
OpenAI LLM Provider Implementation

Implements the LLMProvider interface using OpenAI API.
"""
import os
import logging
from typing import List, Dict, Optional
from application.interfaces.llm_provider import LLMProvider

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


class OpenAILLMProvider(LLMProvider):
    """
    OpenAI LLM Provider implementation.
    
    This is an INFRASTRUCTURE implementation of the Application interface.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """
        Initialize OpenAI provider.
        
        Args:
            api_key: OpenAI API key (defaults to env var)
            model: Model name to use (default: gpt-3.5-turbo)
        """
        if OpenAI is None:
            raise ImportError("openai package not installed. Run: pip install openai")
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not provided and not found in environment")
        
        self.model = model
        self.client = OpenAI(api_key=self.api_key)
        
        logging.info(f"OpenAI LLM Provider initialized with model: {self.model}")
    
    async def generate(
        self, 
        prompt: str,
        system_message: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate text completion using OpenAI.
        
        Implementation of LLMProvider interface.
        """
        try:
            messages = []
            
            if system_message:
                messages.append({"role": "system", "content": system_message})
            
            messages.append({"role": "user", "content": prompt})
            
            # Call OpenAI API
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Extract response
            if not completion.choices or len(completion.choices) == 0:
                raise ValueError("No response from OpenAI API")
            
            response_text = completion.choices[0].message.content
            
            if not response_text:
                raise ValueError("Empty response from OpenAI API")
            
            return response_text.strip()
            
        except Exception as e:
            logging.error(f"OpenAI generation error: {e}")
            raise RuntimeError(f"OpenAI API error: {str(e)}") from e
    
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
            # Call OpenAI API with full message history
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Extract response
            if not completion.choices or len(completion.choices) == 0:
                raise ValueError("No response from OpenAI API")
            
            response_text = completion.choices[0].message.content
            
            if not response_text:
                raise ValueError("Empty response from OpenAI API")
            
            return response_text.strip()
            
        except Exception as e:
            logging.error(f"OpenAI generation error: {e}")
            raise RuntimeError(f"OpenAI API error: {str(e)}") from e
    
    def get_model_name(self) -> str:
        """Get the model name being used"""
        return self.model

