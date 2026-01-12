"""
Embedding Provider Interface

Contract for embedding providers (SentenceTransformers, OpenAI, etc.)
"""
from abc import ABC, abstractmethod
from typing import List
from domain.value_objects.embedding import Embedding


class EmbeddingProvider(ABC):
    """
    Interface for embedding providers.
    
    Implementations will be in infrastructure layer.
    """
    
    @abstractmethod
    async def embed_text(self, text: str) -> Embedding:
        """
        Generate embedding for single text.
        
        Args:
            text: The text to embed
        
        Returns:
            Embedding vector
        
        Raises:
            Exception if embedding fails
        """
        pass
    
    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[Embedding]:
        """
        Generate embeddings for multiple texts (more efficient).
        
        Args:
            texts: List of texts to embed
        
        Returns:
            List of embedding vectors
        
        Raises:
            Exception if embedding fails
        """
        pass
    
    @abstractmethod
    def get_dimension(self) -> int:
        """Get embedding dimension (e.g., 384 for MiniLM)"""
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """Get the embedding model name"""
        pass

