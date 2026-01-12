"""
Document DTOs - Data Transfer Objects for Document Use Cases
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class UploadDocumentRequest:
    """Input for UploadDocument use case"""
    user_id: str
    file_content: bytes
    filename: str
    content_type: str
    folder: Optional[str] = None


@dataclass
class UploadDocumentResponse:
    """Output from UploadDocument use case"""
    document_id: str  # vault_id
    storage_path: str
    filename: str
    file_size: int


@dataclass
class EmbedDocumentRequest:
    """Input for EmbedDocument use case"""
    document_id: str


@dataclass
class EmbedDocumentResponse:
    """Output from EmbedDocument use case"""
    document_id: str
    chunks_created: int
    success: bool

