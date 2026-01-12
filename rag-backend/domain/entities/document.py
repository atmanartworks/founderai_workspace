"""
Document Entity - Core Business Object

A document represents a file uploaded to the vault.
Can be PDF, DOCX, TXT, etc.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid


@dataclass
class Document:
    """
    Document entity representing an uploaded file.
    
    Business Rules:
    - Must have a user_id (owner)
    - Must have storage_path for retrieval
    - original_name preserves user's filename
    - file_size must be positive
    - content_type indicates MIME type
    - text_content stores extracted text
    """
    
    user_id: str
    storage_path: str
    original_name: str
    file_size: int
    content_type: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)
    text_content: Optional[str] = None
    
    def __post_init__(self):
        """Validate business rules"""
        if not self.user_id:
            raise ValueError("user_id is required")
        if not self.storage_path:
            raise ValueError("storage_path is required")
        if not self.original_name:
            raise ValueError("original_name is required")
        if self.file_size < 0:
            raise ValueError("file_size must be non-negative")
        if not self.content_type:
            raise ValueError("content_type is required")
    
    def is_owned_by(self, user_id: str) -> bool:
        """Check if document belongs to user"""
        return self.user_id == user_id
    
    def has_text_content(self) -> bool:
        """Check if text has been extracted"""
        return self.text_content is not None and len(self.text_content.strip()) > 0
    
    def set_text_content(self, text: str) -> None:
        """Set extracted text content"""
        if text is None:
            self.text_content = None
        else:
            self.text_content = text.strip()
    
    def get_file_extension(self) -> str:
        """Get file extension from original name"""
        if "." not in self.original_name:
            return ""
        return self.original_name.split(".")[-1].lower()
    
    def is_pdf(self) -> bool:
        """Check if document is PDF"""
        return self.get_file_extension() == "pdf"
    
    def is_docx(self) -> bool:
        """Check if document is DOCX"""
        return self.get_file_extension() == "docx"
    
    def is_text(self) -> bool:
        """Check if document is plain text"""
        return self.get_file_extension() in ["txt", "md", "json", "html", "htm"]
    
    def __repr__(self) -> str:
        return f"Document(id={self.id}, name='{self.original_name}', size={self.file_size})"

