"""
Upload Document Use Case

Handles file upload to storage and metadata creation.
"""
from domain.entities.document import Document
from domain.repositories.document_repository import DocumentRepository
from domain.exceptions import ValidationException
from application.dtos.document_dtos import UploadDocumentRequest, UploadDocumentResponse
from application.interfaces.storage_provider import StorageProvider


# Allowed file extensions
ALLOWED_EXTENSIONS = [".txt", ".pdf", ".docx", ".md", ".html", ".htm", ".json"]


class UploadDocumentUseCase:
    """
    Use Case: Upload a document to storage.
    
    Business Rules:
    - Only allowed file types
    - File must have content
    - Metadata stored in database
    """
    
    def __init__(
        self,
        document_repo: DocumentRepository,
        storage_provider: StorageProvider
    ):
        self.document_repo = document_repo
        self.storage_provider = storage_provider
    
    async def execute(self, request: UploadDocumentRequest) -> UploadDocumentResponse:
        """
        Execute the upload document use case.
        
        Args:
            request: UploadDocumentRequest DTO
        
        Returns:
            UploadDocumentResponse DTO
        
        Raises:
            ValidationException: If file type not allowed or file empty
        """
        # Validate file type
        file_ext = self._get_file_extension(request.filename)
        if file_ext not in ALLOWED_EXTENSIONS:
            raise ValidationException(
                f"File type {file_ext} not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
                field="filename"
            )
        
        # Validate file content
        if not request.file_content or len(request.file_content) == 0:
            raise ValidationException("File content cannot be empty", field="file_content")
        
        # Build storage path
        if request.folder:
            storage_path = f"{request.folder}/{request.filename}"
        else:
            storage_path = f"{request.user_id}/{request.filename}"
        
        # Upload to storage
        await self.storage_provider.upload_file(
            file_content=request.file_content,
            path=storage_path,
            content_type=request.content_type
        )
        
        # Create document entity
        document = Document(
            user_id=request.user_id,
            storage_path=storage_path,
            original_name=request.filename,
            file_size=len(request.file_content),
            content_type=request.content_type
        )
        
        # Save metadata
        saved_document = await self.document_repo.save(document)
        
        # Return response
        return UploadDocumentResponse(
            document_id=saved_document.id,
            storage_path=saved_document.storage_path,
            filename=saved_document.original_name,
            file_size=saved_document.file_size
        )
    
    def _get_file_extension(self, filename: str) -> str:
        """Extract file extension (lowercase with dot)"""
        if "." not in filename:
            return ""
        return "." + filename.split(".")[-1].lower()

