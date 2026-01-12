"""
Not Found Exceptions

Raised when an entity is not found.
"""
from .domain_exception import DomainException


class NotFoundException(DomainException):
    """Base exception for entity not found errors."""
    
    def __init__(self, entity_type: str, entity_id: str):
        message = f"{entity_type} with id '{entity_id}' not found"
        super().__init__(message, f"{entity_type.upper()}_NOT_FOUND")
        self.entity_type = entity_type
        self.entity_id = entity_id


class ConversationNotFoundException(NotFoundException):
    """Raised when conversation is not found."""
    
    def __init__(self, conversation_id: str):
        super().__init__("Conversation", conversation_id)


class MessageNotFoundException(NotFoundException):
    """Raised when message is not found."""
    
    def __init__(self, message_id: str):
        super().__init__("Message", message_id)


class DocumentNotFoundException(NotFoundException):
    """Raised when document is not found."""
    
    def __init__(self, document_id: str):
        super().__init__("Document", document_id)


class ChunkNotFoundException(NotFoundException):
    """Raised when chunk is not found."""
    
    def __init__(self, chunk_id: str):
        super().__init__("Chunk", chunk_id)

