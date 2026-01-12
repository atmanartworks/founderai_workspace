"""
LLM Provider Interface

Contract for Language Model providers (Groq, OpenAI, etc.)
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class LLMProvider(ABC):
    """
    Interface for LLM (Large Language Model) providers.
    
    Implementations will be in infrastructure layer (Groq, OpenAI, etc.)
    """
    
    @abstractmethod
    async def generate(
        self, 
        prompt: str,
        system_message: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate text completion.
        
        Args:
            prompt: The user prompt
            system_message: Optional system message for context
            temperature: Randomness (0.0 = deterministic)
            max_tokens: Maximum tokens to generate
        
        Returns:
            Generated text
        
        Raises:
            Exception if generation fails
        """
        pass
    
    @abstractmethod
    async def generate_with_history(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.0,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate text with conversation history.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Randomness
            max_tokens: Maximum tokens
        
        Returns:
            Generated text
        """
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """Get the model name being used"""
        pass

