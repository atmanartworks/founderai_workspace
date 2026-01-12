"""
Supabase Message Repository Implementation

Implements MessageRepository using Supabase.
"""
import logging
from typing import Optional, List
from datetime import datetime
from domain.entities.message import Message
from domain.repositories.message_repository import MessageRepository

try:
    from supabase import Client
except ImportError:
    Client = None


class SupabaseMessageRepository(MessageRepository):
    """
    Supabase implementation of MessageRepository.
    """
    
    def __init__(self, client: 'Client'):
        if Client is None:
            raise ImportError("supabase package not installed")
        
        self.client = client
        self.table_name = "messages"
        
        logging.info("Supabase Message Repository initialized")
    
    async def get_by_id(self, message_id: str) -> Optional[Message]:
        """Get message by ID"""
        try:
            response = self.client.table(self.table_name)\
                .select("*")\
                .eq("id", message_id)\
                .execute()
            
            if not response.data or len(response.data) == 0:
                return None
            
            return self._to_entity(response.data[0])
            
        except Exception as e:
            logging.error(f"Error getting message {message_id}: {e}")
            raise
    
    async def get_by_conversation(self, conversation_id: str) -> List[Message]:
        """Get all messages in a conversation, ordered by created_at"""
        try:
            response = self.client.table(self.table_name)\
                .select("*")\
                .eq("conversation_id", conversation_id)\
                .order("created_at", desc=False)\
                .execute()
            
            if not response.data:
                return []
            
            return [self._to_entity(row) for row in response.data]
            
        except Exception as e:
            logging.error(f"Error getting messages for conversation {conversation_id}: {e}")
            raise
    
    async def save(self, message: Message) -> Message:
        """Create a message"""
        try:
            data = self._to_dict(message)
            
            response = self.client.table(self.table_name)\
                .insert(data)\
                .execute()
            
            if not response.data or len(response.data) == 0:
                raise RuntimeError("Failed to save message")
            
            return self._to_entity(response.data[0])
            
        except Exception as e:
            logging.error(f"Error saving message: {e}")
            raise
    
    async def delete(self, message_id: str) -> bool:
        """Delete a message"""
        try:
            response = self.client.table(self.table_name)\
                .delete()\
                .eq("id", message_id)\
                .execute()
            
            return response.data is not None and len(response.data) > 0
            
        except Exception as e:
            logging.error(f"Error deleting message {message_id}: {e}")
            return False
    
    async def delete_by_conversation(self, conversation_id: str) -> int:
        """Delete all messages in a conversation"""
        try:
            response = self.client.table(self.table_name)\
                .delete()\
                .eq("conversation_id", conversation_id)\
                .execute()
            
            return len(response.data) if response.data else 0
            
        except Exception as e:
            logging.error(f"Error deleting messages for conversation {conversation_id}: {e}")
            return 0
    
    async def count_by_conversation(self, conversation_id: str) -> int:
        """Count messages in a conversation"""
        try:
            response = self.client.table(self.table_name)\
                .select("id", count="exact")\
                .eq("conversation_id", conversation_id)\
                .execute()
            
            return response.count if hasattr(response, 'count') else len(response.data or [])
            
        except Exception as e:
            logging.error(f"Error counting messages: {e}")
            return 0
    
    def _to_entity(self, row: dict) -> Message:
        """Convert database row to Message entity"""
        return Message(
            id=row["id"],
            conversation_id=row["conversation_id"],
            content=row["content"],
            is_ai=row["is_ai"],
            created_at=self._parse_datetime(row["created_at"]),
            file_urls=row.get("file_urls"),
            used_documents=row.get("used_documents")
        )
    
    def _to_dict(self, message: Message) -> dict:
        """Convert Message entity to database dict"""
        return {
            "id": message.id,
            "conversation_id": message.conversation_id,
            "content": message.content,
            "is_ai": message.is_ai,
            "created_at": message.created_at.isoformat(),
            "file_urls": message.file_urls,
            "used_documents": message.used_documents
        }
    
    def _parse_datetime(self, dt_str: str) -> datetime:
        """Parse datetime from database"""
        if isinstance(dt_str, datetime):
            return dt_str
        return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))

