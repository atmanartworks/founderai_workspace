"""
Supabase Chunk Repository Implementation

Implements ChunkRepository using Supabase with vector search support.
"""
import logging
from typing import Optional, List
from datetime import datetime
from domain.entities.chunk import Chunk
from domain.repositories.chunk_repository import ChunkRepository

try:
    from supabase import Client
except ImportError:
    Client = None


class SupabaseChunkRepository(ChunkRepository):
    """
    Supabase implementation of ChunkRepository.
    
    Includes vector similarity search using Supabase's pgvector extension.
    """
    
    def __init__(self, client: 'Client'):
        if Client is None:
            raise ImportError("supabase package not installed")
        
        self.client = client
        self.table_name = "document_chunks"
        
        logging.info("Supabase Chunk Repository initialized")
    
    async def get_by_id(self, chunk_id: str) -> Optional[Chunk]:
        """Get chunk by ID"""
        try:
            response = self.client.table(self.table_name)\
                .select("*")\
                .eq("id", chunk_id)\
                .execute()
            
            if not response.data or len(response.data) == 0:
                return None
            
            return self._to_entity(response.data[0])
            
        except Exception as e:
            logging.error(f"Error getting chunk {chunk_id}: {e}")
            raise
    
    async def get_by_document(self, document_id: str) -> List[Chunk]:
        """Get all chunks for a document, ordered by chunk_index"""
        try:
            response = self.client.table(self.table_name)\
                .select("*")\
                .eq("vault_id", document_id)\
                .order("chunk_index", desc=False)\
                .execute()
            
            if not response.data:
                return []
            
            return [self._to_entity(row) for row in response.data]
            
        except Exception as e:
            logging.error(f"Error getting chunks for document {document_id}: {e}")
            raise
    
    async def save(self, chunk: Chunk) -> Chunk:
        """Create a chunk"""
        try:
            data = self._to_dict(chunk)
            
            response = self.client.table(self.table_name)\
                .insert(data)\
                .execute()
            
            if not response.data or len(response.data) == 0:
                raise RuntimeError("Failed to save chunk")
            
            return self._to_entity(response.data[0])
            
        except Exception as e:
            logging.error(f"Error saving chunk: {e}")
            raise
    
    async def save_batch(self, chunks: List[Chunk]) -> List[Chunk]:
        """Save multiple chunks at once (more efficient)"""
        try:
            if not chunks:
                return []
            
            data_list = [self._to_dict(chunk) for chunk in chunks]
            
            response = self.client.table(self.table_name)\
                .insert(data_list)\
                .execute()
            
            if not response.data:
                raise RuntimeError("Failed to save chunks")
            
            return [self._to_entity(row) for row in response.data]
            
        except Exception as e:
            logging.error(f"Error saving chunks batch: {e}")
            raise
    
    async def delete_by_document(self, document_id: str) -> int:
        """Delete all chunks for a document"""
        try:
            response = self.client.table(self.table_name)\
                .delete()\
                .eq("vault_id", document_id)\
                .execute()
            
            return len(response.data) if response.data else 0
            
        except Exception as e:
            logging.error(f"Error deleting chunks for document {document_id}: {e}")
            return 0
    
    async def search_by_embedding(
        self, 
        query_embedding: List[float], 
        user_id: str,
        limit: int = 5
    ) -> List[Chunk]:
        """
        Semantic search using vector similarity.
        
        Uses Supabase RPC function 'search_embeddings' which performs
        cosine similarity search using pgvector.
        """
        try:
            # Call Supabase RPC function for vector search
            response = self.client.rpc(
                "search_embeddings",
                {
                    "query_embedding": query_embedding,
                    "user_id_input": user_id,
                    "match_count": limit
                }
            ).execute()
            
            if not response.data:
                return []
            
            return [self._to_entity(row) for row in response.data]
            
        except Exception as e:
            logging.error(f"Error performing vector search: {e}")
            # Return empty list instead of raising to gracefully handle search failures
            return []
    
    async def count_by_document(self, document_id: str) -> int:
        """Count chunks for a document"""
        try:
            response = self.client.table(self.table_name)\
                .select("id", count="exact")\
                .eq("vault_id", document_id)\
                .execute()
            
            return response.count if hasattr(response, 'count') else len(response.data or [])
            
        except Exception as e:
            logging.error(f"Error counting chunks: {e}")
            return 0
    
    def _to_entity(self, row: dict) -> Chunk:
        """Convert database row to Chunk entity"""
        return Chunk(
            id=row["id"],
            vault_id=row["vault_id"],
            user_id=row["user_id"],
            content=row["content"],
            chunk_index=row["chunk_index"],
            tokens=row["tokens"],
            embedding=row["embedding"],
            created_at=self._parse_datetime(row["created_at"])
        )
    
    def _to_dict(self, chunk: Chunk) -> dict:
        """Convert Chunk entity to database dict"""
        return {
            "id": chunk.id,
            "vault_id": chunk.vault_id,
            "user_id": chunk.user_id,
            "content": chunk.content,
            "chunk_index": chunk.chunk_index,
            "tokens": chunk.tokens,
            "embedding": chunk.embedding,
            "created_at": chunk.created_at.isoformat()
        }
    
    def _parse_datetime(self, dt_str: str) -> datetime:
        """Parse datetime from database"""
        if isinstance(dt_str, datetime):
            return dt_str
        return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))

