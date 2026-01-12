"""
Document Repository Interface

Defines the contract for document data access.
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from domain.entities.document import Document


class DocumentRepository(ABC):
    """Repository interface for Document entity."""
    
    @abstractmethod
    async def get_by_id(self, document_id: str) -> Optional[Document]:
        """Get document by ID."""
        pass
    
    @abstractmethod
    async def get_by_user(self, user_id: str) -> List[Document]:
        """
        Get all documents for a user.
        
        Returns:
            List of documents, ordered by created_at desc
        """
        pass
    
    @abstractmethod
    async def save(self, document: Document) -> Document:
        """
        Create or update a document.
        
        Returns:
            The saved document
        """
        pass
    
    @abstractmethod
    async def delete(self, document_id: str) -> bool:
        """Delete a document."""
        pass
    
    @abstractmethod
    async def exists(self, document_id: str) -> bool:
        """Check if document exists."""
        pass
    
    @abstractmethod
    async def get_by_storage_path(self, storage_path: str) -> Optional[Document]:
        """Get document by storage path."""
        pass

