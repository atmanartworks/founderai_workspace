"""
Chunk Entity - Core Business Object

A chunk represents a piece of a document used for RAG.
Documents are split into chunks for better retrieval.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import uuid


@dataclass
class Chunk:
    """
    Chunk entity representing a portion of a document.
    
    Business Rules:
    - Must belong to a document (vault_id)
    - Must have content
    - chunk_index indicates position in document
    - tokens is an estimate for context window management
    - embedding is the vector representation for similarity search
    - Must have user_id for access control
    """
    
    vault_id: str  # Document ID
    user_id: str
    content: str
    chunk_index: int
    tokens: int
    embedding: List[float]
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Validate business rules"""
        if not self.vault_id:
            raise ValueError("vault_id is required")
        if not self.user_id:
            raise ValueError("user_id is required")
        if not self.content or not self.content.strip():
            raise ValueError("content cannot be empty")
        if self.chunk_index < 0:
            raise ValueError("chunk_index must be non-negative")
        if self.tokens <= 0:
            raise ValueError("tokens must be positive")
        if not self.embedding or len(self.embedding) == 0:
            raise ValueError("embedding cannot be empty")
        
        self.content = self.content.strip()
    
    def is_owned_by(self, user_id: str) -> bool:
        """Check if chunk belongs to user"""
        return self.user_id == user_id
    
    def belongs_to_document(self, document_id: str) -> bool:
        """Check if chunk belongs to document"""
        return self.vault_id == document_id
    
    def get_embedding_dimension(self) -> int:
        """Get dimension of embedding vector"""
        return len(self.embedding)
    
    def get_content_preview(self, length: int = 100) -> str:
        """Get preview of chunk content"""
        if len(self.content) <= length:
            return self.content
        return self.content[:length] + "..."
    
    def __repr__(self) -> str:
        preview = self.get_content_preview(50)
        return f"Chunk(id={self.id}, index={self.chunk_index}, tokens={self.tokens}, content='{preview}')"

