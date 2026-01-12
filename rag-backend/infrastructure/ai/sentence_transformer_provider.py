"""
SentenceTransformer Embedding Provider Implementation

Implements the EmbeddingProvider interface using sentence-transformers.
"""
import os
import logging
from typing import List
from application.interfaces.embedding_provider import EmbeddingProvider
from domain.value_objects.embedding import Embedding

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None


class SentenceTransformerEmbeddingProvider(EmbeddingProvider):
    """
    SentenceTransformer embedding provider implementation.
    
    Uses local embedding models (all-MiniLM-L6-v2 by default).
    This is an INFRASTRUCTURE implementation of the Application interface.
    """
    
    def __init__(self, model_name: str = "nomic-ai/nomic-embed-text-v1"):
        """
        Initialize SentenceTransformer provider.
        
        Args:
            model_name: Model name (default: nomic-ai/nomic-embed-text-v1, 768 dimensions)
        """
        if SentenceTransformer is None:
            raise ImportError("sentence-transformers not installed. Run: pip install sentence-transformers")
        
        # Allow override from environment
        self.model_name = os.getenv("LOCAL_EMBEDDING_MODEL", model_name)
        
        try:
            # Nomic models require trust_remote_code=True
            self.model = SentenceTransformer(self.model_name, trust_remote_code=True)
            logging.info(f"SentenceTransformer loaded: {self.model_name}")
        except Exception as e:
            logging.error(f"Failed to load embedding model: {e}")
            raise RuntimeError(f"Failed to load embedding model: {str(e)}") from e
        
        # Get embedding dimension
        self._dimension = self.model.get_sentence_embedding_dimension()
        logging.info(f"Embedding dimension: {self._dimension}")
    
    async def embed_text(self, text: str) -> Embedding:
        """
        Generate embedding for single text.
        
        Implementation of EmbeddingProvider interface.
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        try:
            # Generate embedding
            vector = self.model.encode([text.strip()])[0]
            
            # Convert to Embedding value object
            return Embedding.from_list(vector.tolist())
            
        except Exception as e:
            logging.error(f"Embedding error: {e}")
            raise RuntimeError(f"Embedding generation failed: {str(e)}") from e
    
    async def embed_batch(self, texts: List[str]) -> List[Embedding]:
        """
        Generate embeddings for multiple texts.
        
        Implementation of EmbeddingProvider interface.
        More efficient than calling embed_text multiple times.
        """
        if not texts:
            return []
        
        # Filter empty texts
        clean_texts = [t.strip() for t in texts if t and t.strip()]
        if not clean_texts:
            return []
        
        try:
            # Generate embeddings in batch (more efficient)
            vectors = self.model.encode(clean_texts)
            
            # Convert to Embedding value objects
            embeddings = [Embedding.from_list(v.tolist()) for v in vectors]
            
            return embeddings
            
        except Exception as e:
            logging.error(f"Batch embedding error: {e}")
            raise RuntimeError(f"Batch embedding generation failed: {str(e)}") from e
    
    def get_dimension(self) -> int:
        """Get embedding dimension"""
        return self._dimension
    
    def get_model_name(self) -> str:
        """Get the embedding model name"""
        return self.model_name

