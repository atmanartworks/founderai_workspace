"""
Create Conversation Use Case

Simple use case to create a new conversation.
"""
from domain.entities.conversation import Conversation
from domain.repositories.conversation_repository import ConversationRepository
from application.dtos.conversation_dtos import CreateConversationRequest, CreateConversationResponse


class CreateConversationUseCase:
    """
    Use Case: Create a new conversation.
    
    This is a simple use case but demonstrates the pattern.
    """
    
    def __init__(self, conversation_repo: ConversationRepository):
        self.conversation_repo = conversation_repo
    
    async def execute(self, request: CreateConversationRequest) -> CreateConversationResponse:
        """
        Execute the create conversation use case.
        
        Args:
            request: CreateConversationRequest DTO
        
        Returns:
            CreateConversationResponse DTO
        """
        # Create conversation entity
        conversation = Conversation(
            user_id=request.user_id,
            title=request.title
        )
        
        # Save via repository
        saved_conversation = await self.conversation_repo.save(conversation)
        
        # Return DTO
        return CreateConversationResponse(
            conversation_id=saved_conversation.id,
            title=saved_conversation.title,
            created_at=saved_conversation.created_at
        )

