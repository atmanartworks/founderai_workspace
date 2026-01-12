"""
Embed Document Use Case

Extracts text, chunks it, generates embeddings, and stores chunks.
"""
import tempfile
import os
from typing import List
from domain.entities.document import Document
from domain.entities.chunk import Chunk
from domain.repositories.document_repository import DocumentRepository
from domain.repositories.chunk_repository import ChunkRepository
from domain.services.chunking_service import ChunkingDomainService
from domain.services.text_cleaner import TextCleaner
from domain.exceptions import DocumentNotFoundException, ValidationException
from application.dtos.document_dtos import EmbedDocumentRequest, EmbedDocumentResponse
from application.interfaces.embedding_provider import EmbeddingProvider
from application.interfaces.storage_provider import StorageProvider


class EmbedDocumentUseCase:
    """
    Use Case: Extract text from document, chunk it, and generate embeddings.
    
    Business Flow:
    1. Get document from database
    2. Download file from storage if needed
    3. Extract text
    4. Clean text
    5. Chunk text
    6. Generate embeddings
    7. Save chunks with embeddings
    """
    
    def __init__(
        self,
        document_repo: DocumentRepository,
        chunk_repo: ChunkRepository,
        embedding_provider: EmbeddingProvider,
        storage_provider: StorageProvider,
        text_extractor  # Will be interface in infrastructure
    ):
        self.document_repo = document_repo
        self.chunk_repo = chunk_repo
        self.embedding_provider = embedding_provider
        self.storage_provider = storage_provider
        self.text_extractor = text_extractor
        self.chunking_service = ChunkingDomainService()
    
    async def execute(self, request: EmbedDocumentRequest) -> EmbedDocumentResponse:
        """
        Execute the embed document use case.
        
        Args:
            request: EmbedDocumentRequest DTO
        
        Returns:
            EmbedDocumentResponse DTO
        
        Raises:
            DocumentNotFoundException: If document not found
            ValidationException: If no text extracted
        """
        # Step 1: Get document
        document = await self.document_repo.get_by_id(request.document_id)
        if not document:
            raise DocumentNotFoundException(request.document_id)
        
        # Step 2: Get text content
        text_content = await self._get_text_content(document)
        
        # Step 3: Clean text
        cleaned_text = TextCleaner.clean(text_content)
        if not TextCleaner.is_valid(cleaned_text):
            raise ValidationException("No usable text found in document")
        
        # Step 4: Chunk text
        chunks_data = self.chunking_service.chunk_text(cleaned_text)
        if not chunks_data:
            raise ValidationException("Failed to chunk document")
        
        # Step 5: Extract content for embedding
        chunk_contents = [content for content, _ in chunks_data]
        
        # Step 6: Generate embeddings
        embeddings = await self.embedding_provider.embed_batch(chunk_contents)
        
        # Step 7: Create chunk entities
        chunk_entities = []
        for (content, index), embedding in zip(chunks_data, embeddings):
            chunk = Chunk(
                vault_id=document.id,
                user_id=document.user_id,
                content=content,
                chunk_index=index,
                tokens=self.chunking_service.estimate_tokens(content),
                embedding=embedding.to_list()
            )
            chunk_entities.append(chunk)
        
        # Step 8: Delete old chunks (if re-embedding)
        await self.chunk_repo.delete_by_document(document.id)
        
        # Step 9: Save new chunks
        await self.chunk_repo.save_batch(chunk_entities)
        
        # Return response
        return EmbedDocumentResponse(
            document_id=document.id,
            chunks_created=len(chunk_entities),
            success=True
        )
    
    async def _get_text_content(self, document: Document) -> str:
        """
        Get text content from document.
        
        Strategy:
        1. If document.text_content exists, use it
        2. Otherwise, download file and extract text
        """
        # Check if text already extracted
        if document.has_text_content():
            return document.text_content
        
        # Download file from storage
        file_bytes = await self.storage_provider.download_file(document.storage_path)
        
        # Save to temp file for extraction
        file_ext = document.get_file_extension()
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_ext}") as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name
        
        try:
            # Extract text
            text = self.text_extractor.extract_text_from_file(tmp_path)
            
            # Update document with extracted text
            document.set_text_content(text)
            await self.document_repo.save(document)
            
            return text
        finally:
            # Clean up temp file
            try:
                os.remove(tmp_path)
            except:
                pass

