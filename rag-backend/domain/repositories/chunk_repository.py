"""
Chunk Repository Interface

Defines the contract for chunk data access.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.chunk import Chunk


class ChunkRepository(ABC):
    """Repository interface for Chunk entity."""
    
    @abstractmethod
    async def get_by_id(self, chunk_id: str) -> Optional[Chunk]:
        """Get chunk by ID."""
        pass
    
    @abstractmethod
    async def get_by_document(self, document_id: str) -> List[Chunk]:
        """
        Get all chunks for a document.
        
        Returns:
            List of chunks, ordered by chunk_index asc
        """
        pass
    
    @abstractmethod
    async def save(self, chunk: Chunk) -> Chunk:
        """
        Create a chunk.
        
        Returns:
            The saved chunk
        """
        pass
    
    @abstractmethod
    async def save_batch(self, chunks: List[Chunk]) -> List[Chunk]:
        """
        Save multiple chunks at once (more efficient).
        
        Returns:
            List of saved chunks
        """
        pass
    
    @abstractmethod
    async def delete_by_document(self, document_id: str) -> int:
        """
        Delete all chunks for a document.
        
        Returns:
            Number of chunks deleted
        """
        pass
    
    @abstractmethod
    async def search_by_embedding(
        self, 
        query_embedding: List[float], 
        user_id: str,
        limit: int = 5
    ) -> List[Chunk]:
        """
        Semantic search using vector similarity.
        
        Args:
            query_embedding: The query vector
            user_id: Filter by user (for access control)
            limit: Maximum number of results
        
        Returns:
            List of most similar chunks, ordered by similarity desc
        """
        pass
    
    @abstractmethod
    async def count_by_document(self, document_id: str) -> int:
        """Count chunks for a document."""
        pass

