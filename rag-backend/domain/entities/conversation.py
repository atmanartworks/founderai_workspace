"""
Conversation Entity - Core Business Object

A conversation represents a chat session between a user and the AI.
Contains pure business logic with NO infrastructure dependencies.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid


@dataclass
class Conversation:
    """
    Conversation entity representing a chat session.
    
    Business Rules:
    - Every conversation must have a user_id
    - Title cannot be empty
    - Created_at is immutable
    - Updated_at changes on any modification
    """
    
    user_id: str
    title: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Validate business rules"""
        if not self.user_id:
            raise ValueError("user_id is required")
        if not self.title or not self.title.strip():
            raise ValueError("title cannot be empty")
        self.title = self.title.strip()
    
    def update_title(self, new_title: str) -> None:
        """
        Update conversation title.
        
        Business Rule: Title must not be empty
        """
        if not new_title or not new_title.strip():
            raise ValueError("title cannot be empty")
        self.title = new_title.strip()
        self.touch()
    
    def touch(self) -> None:
        """Update the updated_at timestamp"""
        self.updated_at = datetime.utcnow()
    
    def is_owned_by(self, user_id: str) -> bool:
        """Check if conversation belongs to user"""
        return self.user_id == user_id
    
    def __repr__(self) -> str:
        return f"Conversation(id={self.id}, title='{self.title}', user_id={self.user_id})"

