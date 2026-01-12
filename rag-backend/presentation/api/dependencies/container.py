"""
Dependency Injection Container

Simple container that wires up all dependencies.
This is where Clean Architecture comes together!
"""
import os
from dotenv import load_dotenv

# Infrastructure implementations
from infrastructure.ai.openai_provider import OpenAILLMProvider
from infrastructure.ai.sentence_transformer_provider import SentenceTransformerEmbeddingProvider
from infrastructure.storage.supabase_storage_provider import SupabaseStorageProvider
from infrastructure.database.supabase.conversation_repository_impl import SupabaseConversationRepository
from infrastructure.text_extraction.text_extractor import TextExtractor

# Application use cases
from application.use_cases.chat.send_message import SendMessageUseCase

# Database client
from app.database import supabase

load_dotenv()


class DependencyContainer:
    """
    Simple dependency injection container.
    
    In a larger app, you might use a library like dependency-injector,
    but this simple approach works great for our needs!
    """
    
    def __init__(self):
        """Initialize all dependencies"""
        self._init_providers()
        self._init_repositories()
        self._init_use_cases()
    
    def _init_providers(self):
        """Initialize provider implementations"""
        # LLM Provider (OpenAI - required)
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY is required. Please set it in .env file")
        
        self.llm_provider = OpenAILLMProvider(
            api_key=openai_api_key,
            model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        )
        
        # Embedding Provider (SentenceTransformers)
        self.embedding_provider = SentenceTransformerEmbeddingProvider(
            model_name=os.getenv("LOCAL_EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        )
        
        # Storage Provider (Supabase)
        self.storage_provider = SupabaseStorageProvider(
            client=supabase,
            bucket_name=os.getenv("SUPABASE_BUCKET", "vault")
        )
        
        # Text Extractor
        self.text_extractor = TextExtractor()
    
    def _init_repositories(self):
        """Initialize repository implementations"""
        # For now, we'll create a simplified repository for demo
        # In Phase 3 completion, you'd use the full implementations
        self.conversation_repository = SupabaseConversationRepository(supabase)
        
        # TODO: Add other repositories when Phase 3 is complete
        # self.message_repository = SupabaseMessageRepository(supabase)
        # self.document_repository = SupabaseDocumentRepository(supabase)
        # self.chunk_repository = SupabaseChunkRepository(supabase)
    
    def _init_use_cases(self):
        """Initialize use cases with their dependencies"""
        # For demo, we'll create a simplified SendMessageUseCase
        # In full implementation, all dependencies would be injected
        pass
    
    def get_send_message_use_case(self) -> SendMessageUseCase:
        """
        Get SendMessage use case with all dependencies injected.
        
        This is where dependency injection magic happens!
        """
        # Note: This is a simplified version for demonstration
        # Full implementation would inject all 5 dependencies
        
        # For now, return None to show the pattern
        # You'll complete this when Phase 3 repositories are done
        return None


# Global container instance
_container: DependencyContainer = None


def get_container() -> DependencyContainer:
    """
    Get the global dependency container.
    
    Singleton pattern - creates once, reuses everywhere.
    """
    global _container
    if _container is None:
        _container = DependencyContainer()
    return _container


# FastAPI dependencies
def get_send_message_use_case() -> SendMessageUseCase:
    """FastAPI dependency for SendMessage use case"""
    container = get_container()
    return container.get_send_message_use_case()

