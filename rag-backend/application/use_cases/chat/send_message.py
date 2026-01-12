"""
Send Message Use Case

Orchestrates the RAG chat flow:
1. Get or create conversation
2. Save user message
3. Embed query
4. Search relevant chunks
5. Build context
6. Generate AI response
7. Save AI message
8. Return response
"""
from typing import List
from domain.entities.conversation import Conversation
from domain.entities.message import Message
from domain.entities.chunk import Chunk
from domain.repositories.conversation_repository import ConversationRepository
from domain.repositories.message_repository import MessageRepository
from domain.repositories.chunk_repository import ChunkRepository
from domain.services.title_generator import TitleGenerator
from domain.exceptions import ConversationNotFoundException
from application.dtos.chat_dtos import SendMessageRequest, SendMessageResponse
from application.interfaces.llm_provider import LLMProvider
from application.interfaces.embedding_provider import EmbeddingProvider


class SendMessageUseCase:
    """
    Use Case: Send a message and get AI response using RAG.
    
    This orchestrates domain logic and infrastructure services
    to implement the chat feature.
    """
    
    def __init__(
        self,
        conversation_repo: ConversationRepository,
        message_repo: MessageRepository,
        chunk_repo: ChunkRepository,
        embedding_provider: EmbeddingProvider,
        llm_provider: LLMProvider
    ):
        """
        Initialize use case with dependencies.
        
        Note: All dependencies are interfaces (dependency inversion)
        """
        self.conversation_repo = conversation_repo
        self.message_repo = message_repo
        self.chunk_repo = chunk_repo
        self.embedding_provider = embedding_provider
        self.llm_provider = llm_provider
    
    async def execute(self, request: SendMessageRequest) -> SendMessageResponse:
        """
        Execute the send message use case.
        
        Args:
            request: SendMessageRequest DTO
        
        Returns:
            SendMessageResponse DTO
        
        Raises:
            DomainException: If business rules are violated
        """
        # Step 1: Get or create conversation
        conversation = await self._get_or_create_conversation(
            request.conversation_id,
            request.user_id,
            request.message
        )
        
        # Step 2: Save user message
        user_message = Message(
            conversation_id=conversation.id,
            content=request.message,
            is_ai=False,
            file_urls=request.file_urls or []
        )
        saved_user_message = await self.message_repo.save(user_message)
        
        # Step 3: Embed query
        query_embedding = await self.embedding_provider.embed_text(request.message)
        
        # Step 4: Search relevant chunks
        relevant_chunks = await self.chunk_repo.search_by_embedding(
            query_embedding=query_embedding.to_list(),
            user_id=request.user_id,
            limit=request.top_k
        )
        
        # Step 5: Build context from chunks
        context, source_files = self._build_context(relevant_chunks)
        
        # Step 6: Generate AI response
        ai_response_text = await self._generate_response(
            context=context,
            question=request.message
        )
        
        # Step 7: Save AI message with sources
        ai_message = Message(
            conversation_id=conversation.id,
            content=ai_response_text,
            is_ai=True,
            used_documents={
                "chunks": [chunk.id for chunk in relevant_chunks],
                "files": source_files
            }
        )
        saved_ai_message = await self.message_repo.save(ai_message)
        
        # Step 8: Update conversation timestamp
        conversation.touch()
        await self.conversation_repo.save(conversation)
        
        # Step 9: Return response
        return SendMessageResponse(
            response=ai_response_text,
            sources=source_files,
            message_id=saved_ai_message.id,
            conversation_id=conversation.id,
            user_message_id=saved_user_message.id
        )
    
    async def _get_or_create_conversation(
        self,
        conversation_id: str | None,
        user_id: str,
        first_message: str
    ) -> Conversation:
        """
        Get existing conversation or create a new one.
        
        Business Rule: If conversation_id is None, create new conversation
        with a smart title based on the first message.
        """
        if conversation_id:
            # Get existing conversation
            conversation = await self.conversation_repo.get_by_id(conversation_id)
            if not conversation:
                raise ConversationNotFoundException(conversation_id)
            return conversation
        else:
            # Create new conversation with smart title
            title = TitleGenerator.generate_from_message(first_message)
            new_conversation = Conversation(
                user_id=user_id,
                title=title
            )
            return await self.conversation_repo.save(new_conversation)
    
    def _build_context(self, chunks: List[Chunk]) -> tuple[str, List[str]]:
        """
        Build context string from relevant chunks.
        
        Returns:
            Tuple of (context_string, source_file_names)
        
        Business Rule: Each chunk is labeled with its source for citation
        """
        if not chunks:
            return "No relevant documents found.", []
        
        context_pieces = []
        source_files = []
        
        for chunk in chunks:
            # Get source file name (would come from document)
            # For now, use vault_id as placeholder
            source_file = f"Document {chunk.vault_id}"
            if source_file not in source_files:
                source_files.append(source_file)
            
            # Build labeled context
            context_pieces.append(
                f"[{source_file}] (chunk {chunk.chunk_index}):\n{chunk.content[:1000]}"
            )
        
        context = "\n\n---\n\n".join(context_pieces)
        return context, source_files
    
    async def _generate_response(self, context: str, question: str) -> str:
        """
        Generate AI response using LLM.
        
        Business Rule: AI must answer ONLY using provided context
        """
        prompt = f"""You must answer only using the document context below.
If the answer is not present in the context, say "I cannot find that in your documents."

Document context:
{context}

User question:
{question}

Answer:"""
        
        system_message = "You are a helpful assistant. Answer ONLY based on the provided document context."
        
        response = await self.llm_provider.generate(
            prompt=prompt,
            system_message=system_message,
            temperature=0.0
        )
        
        return response.strip()

