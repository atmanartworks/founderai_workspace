"""
Conversation Repository Interface

Defines the contract for conversation data access.
Implementations will be in the infrastructure layer.
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from domain.entities.conversation import Conversation


class ConversationRepository(ABC):
    """
    Repository interface for Conversation entity.
    
    This is a CONTRACT - implementations must provide these methods.
    The domain layer doesn't care HOW data is stored (Supabase, Postgres, etc.)
    """
    
    @abstractmethod
    async def get_by_id(self, conversation_id: str) -> Optional[Conversation]:
        """
        Get conversation by ID.
        
        Returns:
            Conversation if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_by_user(self, user_id: str) -> List[Conversation]:
        """
        Get all conversations for a user.
        
        Returns:
            List of conversations, ordered by updated_at desc
        """
        pass
    
    @abstractmethod
    async def save(self, conversation: Conversation) -> Conversation:
        """
        Create or update a conversation.
        
        Returns:
            The saved conversation (with any DB-generated fields)
        """
        pass
    
    @abstractmethod
    async def delete(self, conversation_id: str) -> bool:
        """
        Delete a conversation.
        
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    async def exists(self, conversation_id: str) -> bool:
        """
        Check if conversation exists.
        
        Returns:
            True if exists, False otherwise
        """
        pass

