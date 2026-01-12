"""
Supabase Conversation Repository Implementation

Implements ConversationRepository using Supabase.
"""
import logging
from typing import Optional, List
from datetime import datetime
from domain.entities.conversation import Conversation
from domain.repositories.conversation_repository import ConversationRepository

try:
    from supabase import Client
except ImportError:
    Client = None


class SupabaseConversationRepository(ConversationRepository):
    """
    Supabase implementation of ConversationRepository.
    
    This is an INFRASTRUCTURE implementation of the Domain interface.
    """
    
    def __init__(self, client: 'Client'):
        """
        Initialize repository with Supabase client.
        
        Args:
            client: Supabase client instance
        """
        if Client is None:
            raise ImportError("supabase package not installed")
        
        self.client = client
        self.table_name = "conversations"
        
        logging.info("Supabase Conversation Repository initialized")
    
    async def get_by_id(self, conversation_id: str) -> Optional[Conversation]:
        """Get conversation by ID"""
        try:
            response = self.client.table(self.table_name)\
                .select("*")\
                .eq("id", conversation_id)\
                .execute()
            
            if not response.data or len(response.data) == 0:
                return None
            
            return self._to_entity(response.data[0])
            
        except Exception as e:
            logging.error(f"Error getting conversation {conversation_id}: {e}")
            raise
    
    async def get_by_user(self, user_id: str) -> List[Conversation]:
        """Get all conversations for a user"""
        try:
            response = self.client.table(self.table_name)\
                .select("*")\
                .eq("user_id", user_id)\
                .order("updated_at", desc=True)\
                .execute()
            
            if not response.data:
                return []
            
            return [self._to_entity(row) for row in response.data]
            
        except Exception as e:
            logging.error(f"Error getting conversations for user {user_id}: {e}")
            raise
    
    async def save(self, conversation: Conversation) -> Conversation:
        """Create or update a conversation"""
        try:
            # Check if exists
            existing = await self.exists(conversation.id)
            
            data = self._to_dict(conversation)
            
            if existing:
                # Update
                response = self.client.table(self.table_name)\
                    .update(data)\
                    .eq("id", conversation.id)\
                    .execute()
            else:
                # Insert
                response = self.client.table(self.table_name)\
                    .insert(data)\
                    .execute()
            
            if not response.data or len(response.data) == 0:
                raise RuntimeError("Failed to save conversation")
            
            return self._to_entity(response.data[0])
            
        except Exception as e:
            logging.error(f"Error saving conversation: {e}")
            raise
    
    async def delete(self, conversation_id: str) -> bool:
        """Delete a conversation"""
        try:
            response = self.client.table(self.table_name)\
                .delete()\
                .eq("id", conversation_id)\
                .execute()
            
            # Supabase returns deleted rows
            return response.data is not None and len(response.data) > 0
            
        except Exception as e:
            logging.error(f"Error deleting conversation {conversation_id}: {e}")
            return False
    
    async def exists(self, conversation_id: str) -> bool:
        """Check if conversation exists"""
        try:
            response = self.client.table(self.table_name)\
                .select("id")\
                .eq("id", conversation_id)\
                .execute()
            
            return response.data is not None and len(response.data) > 0
            
        except Exception as e:
            logging.error(f"Error checking conversation existence: {e}")
            return False
    
    def _to_entity(self, row: dict) -> Conversation:
        """Convert database row to Conversation entity"""
        return Conversation(
            id=row["id"],
            user_id=row["user_id"],
            title=row["title"],
            created_at=self._parse_datetime(row["created_at"]),
            updated_at=self._parse_datetime(row["updated_at"])
        )
    
    def _to_dict(self, conversation: Conversation) -> dict:
        """Convert Conversation entity to database dict"""
        return {
            "id": conversation.id,
            "user_id": conversation.user_id,
            "title": conversation.title,
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat()
        }
    
    def _parse_datetime(self, dt_str: str) -> datetime:
        """Parse datetime from database"""
        if isinstance(dt_str, datetime):
            return dt_str
        return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))

