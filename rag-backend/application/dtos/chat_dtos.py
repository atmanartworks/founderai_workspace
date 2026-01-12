"""
Chat DTOs - Data Transfer Objects for Chat Use Cases
"""
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class SendMessageRequest:
    """
    Input for SendMessage use case.
    
    This is what the presentation layer sends to the application layer.
    """
    conversation_id: Optional[str]  # None = create new conversation
    user_id: str
    message: str
    top_k: int = 5  # Number of relevant chunks to retrieve
    file_urls: Optional[List[str]] = None


@dataclass
class SendMessageResponse:
    """
    Output from SendMessage use case.
    
    This is what the application layer returns to the presentation layer.
    """
    response: str  # AI response
    sources: List[str]  # Source file names
    message_id: str  # ID of the AI message
    conversation_id: str  # ID of the conversation
    user_message_id: str  # ID of the user message

