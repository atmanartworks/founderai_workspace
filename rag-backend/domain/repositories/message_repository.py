"""
Message Repository Interface

Defines the contract for message data access.
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from domain.entities.message import Message


class MessageRepository(ABC):
    """Repository interface for Message entity."""
    
    @abstractmethod
    async def get_by_id(self, message_id: str) -> Optional[Message]:
        """Get message by ID."""
        pass
    
    @abstractmethod
    async def get_by_conversation(self, conversation_id: str) -> List[Message]:
        """
        Get all messages in a conversation.
        
        Returns:
            List of messages, ordered by created_at asc
        """
        pass
    
    @abstractmethod
    async def save(self, message: Message) -> Message:
        """
        Create a message.
        
        Returns:
            The saved message
        """
        pass
    
    @abstractmethod
    async def delete(self, message_id: str) -> bool:
        """Delete a message."""
        pass
    
    @abstractmethod
    async def delete_by_conversation(self, conversation_id: str) -> int:
        """
        Delete all messages in a conversation.
        
        Returns:
            Number of messages deleted
        """
        pass
    
    @abstractmethod
    async def count_by_conversation(self, conversation_id: str) -> int:
        """Count messages in a conversation."""
        pass

