"""
Conversation DTOs - Data Transfer Objects for Conversation Use Cases
"""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CreateConversationRequest:
    """Input for CreateConversation use case"""
    user_id: str
    title: str


@dataclass
class CreateConversationResponse:
    """Output from CreateConversation use case"""
    conversation_id: str
    title: str
    created_at: datetime

