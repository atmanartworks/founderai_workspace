"""
Message Entity - Core Business Object

A message represents a single message in a conversation.
Can be from user or AI.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid


@dataclass
class Message:
    """
    Message entity representing a chat message.
    
    Business Rules:
    - Must belong to a conversation
    - Content cannot be empty
    - is_ai flag distinguishes user messages from AI responses
    - created_at is immutable
    - Can optionally reference documents used to generate response
    """
    
    conversation_id: str
    content: str
    is_ai: bool
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)
    file_urls: Optional[List[str]] = None
    used_documents: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validate business rules"""
        if not self.conversation_id:
            raise ValueError("conversation_id is required")
        if not self.content or not self.content.strip():
            raise ValueError("content cannot be empty")
        self.content = self.content.strip()
        
        # Ensure file_urls is a list if provided
        if self.file_urls is None:
            self.file_urls = []
    
    def is_from_user(self) -> bool:
        """Check if message is from user"""
        return not self.is_ai
    
    def is_from_ai(self) -> bool:
        """Check if message is from AI"""
        return self.is_ai
    
    def has_sources(self) -> bool:
        """Check if message has document sources"""
        return self.used_documents is not None and len(self.used_documents) > 0
    
    def get_source_files(self) -> List[str]:
        """Get list of source files used to generate this message"""
        if not self.used_documents:
            return []
        return self.used_documents.get("files", [])
    
    def get_source_chunks(self) -> List[str]:
        """Get list of chunk IDs used to generate this message"""
        if not self.used_documents:
            return []
        return self.used_documents.get("chunks", [])
    
    def add_file_url(self, file_url: str) -> None:
        """Add a file URL attachment to the message"""
        if not file_url:
            raise ValueError("file_url cannot be empty")
        if self.file_urls is None:
            self.file_urls = []
        self.file_urls.append(file_url)
    
    def __repr__(self) -> str:
        sender = "AI" if self.is_ai else "User"
        preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"Message(id={self.id}, from={sender}, content='{preview}')"

