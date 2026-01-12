"""
Supabase Document Repository Implementation

Implements DocumentRepository using Supabase.
"""
import logging
from typing import Optional, List
from datetime import datetime
from domain.entities.document import Document
from domain.repositories.document_repository import DocumentRepository

try:
    from supabase import Client
except ImportError:
    Client = None


class SupabaseDocumentRepository(DocumentRepository):
    """
    Supabase implementation of DocumentRepository.
    """
    
    def __init__(self, client: 'Client'):
        if Client is None:
            raise ImportError("supabase package not installed")
        
        self.client = client
        self.table_name = "vault_files"
        
        logging.info("Supabase Document Repository initialized")
    
    async def get_by_id(self, document_id: str) -> Optional[Document]:
        """Get document by ID"""
        try:
            response = self.client.table(self.table_name)\
                .select("*")\
                .eq("id", document_id)\
                .execute()
            
            if not response.data or len(response.data) == 0:
                return None
            
            return self._to_entity(response.data[0])
            
        except Exception as e:
            logging.error(f"Error getting document {document_id}: {e}")
            raise
    
    async def get_by_user(self, user_id: str) -> List[Document]:
        """Get all documents for a user"""
        try:
            response = self.client.table(self.table_name)\
                .select("*")\
                .eq("user_id", user_id)\
                .order("created_at", desc=True)\
                .execute()
            
            if not response.data:
                return []
            
            return [self._to_entity(row) for row in response.data]
            
        except Exception as e:
            logging.error(f"Error getting documents for user {user_id}: {e}")
            raise
    
    async def save(self, document: Document) -> Document:
        """Create or update a document"""
        try:
            # Check if exists
            existing = await self.exists(document.id)
            
            data = self._to_dict(document)
            
            if existing:
                # Update
                response = self.client.table(self.table_name)\
                    .update(data)\
                    .eq("id", document.id)\
                    .execute()
            else:
                # Insert
                response = self.client.table(self.table_name)\
                    .insert(data)\
                    .execute()
            
            if not response.data or len(response.data) == 0:
                raise RuntimeError("Failed to save document")
            
            return self._to_entity(response.data[0])
            
        except Exception as e:
            logging.error(f"Error saving document: {e}")
            raise
    
    async def delete(self, document_id: str) -> bool:
        """Delete a document"""
        try:
            response = self.client.table(self.table_name)\
                .delete()\
                .eq("id", document_id)\
                .execute()
            
            return response.data is not None and len(response.data) > 0
            
        except Exception as e:
            logging.error(f"Error deleting document {document_id}: {e}")
            return False
    
    async def exists(self, document_id: str) -> bool:
        """Check if document exists"""
        try:
            response = self.client.table(self.table_name)\
                .select("id")\
                .eq("id", document_id)\
                .execute()
            
            return response.data is not None and len(response.data) > 0
            
        except Exception as e:
            logging.error(f"Error checking document existence: {e}")
            return False
    
    async def get_by_storage_path(self, storage_path: str) -> Optional[Document]:
        """Get document by storage path"""
        try:
            response = self.client.table(self.table_name)\
                .select("*")\
                .eq("storage_path", storage_path)\
                .execute()
            
            if not response.data or len(response.data) == 0:
                return None
            
            return self._to_entity(response.data[0])
            
        except Exception as e:
            logging.error(f"Error getting document by storage path: {e}")
            raise
    
    def _to_entity(self, row: dict) -> Document:
        """Convert database row to Document entity"""
        return Document(
            id=row["id"],
            user_id=row["user_id"],
            storage_path=row["storage_path"],
            original_name=row["original_name"],
            file_size=row["file_size"],
            content_type=row["content_type"],
            created_at=self._parse_datetime(row["created_at"]),
            text_content=row.get("text_content")
        )
    
    def _to_dict(self, document: Document) -> dict:
        """Convert Document entity to database dict"""
        return {
            "id": document.id,
            "user_id": document.user_id,
            "storage_path": document.storage_path,
            "original_name": document.original_name,
            "file_size": document.file_size,
            "content_type": document.content_type,
            "created_at": document.created_at.isoformat(),
            "text_content": document.text_content
        }
    
    def _parse_datetime(self, dt_str: str) -> datetime:
        """Parse datetime from database"""
        if isinstance(dt_str, datetime):
            return dt_str
        return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))

