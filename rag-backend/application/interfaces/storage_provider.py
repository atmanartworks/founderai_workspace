"""
Storage Provider Interface

Contract for file storage (Supabase Storage, S3, local, etc.)
"""
from abc import ABC, abstractmethod
from typing import Optional


class StorageProvider(ABC):
    """
    Interface for file storage providers.
    
    Implementations will be in infrastructure layer.
    """
    
    @abstractmethod
    async def upload_file(
        self, 
        file_content: bytes, 
        path: str,
        content_type: Optional[str] = None
    ) -> str:
        """
        Upload file to storage.
        
        Args:
            file_content: The file bytes
            path: Storage path (e.g., "user123/file.pdf")
            content_type: MIME type
        
        Returns:
            Storage URL or path
        
        Raises:
            Exception if upload fails
        """
        pass
    
    @abstractmethod
    async def download_file(self, path: str) -> bytes:
        """
        Download file from storage.
        
        Args:
            path: Storage path
        
        Returns:
            File bytes
        
        Raises:
            Exception if file not found or download fails
        """
        pass
    
    @abstractmethod
    async def delete_file(self, path: str) -> bool:
        """
        Delete file from storage.
        
        Args:
            path: Storage path
        
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    async def file_exists(self, path: str) -> bool:
        """
        Check if file exists.
        
        Args:
            path: Storage path
        
        Returns:
            True if exists, False otherwise
        """
        pass
    
    @abstractmethod
    def get_public_url(self, path: str) -> str:
        """
        Get public URL for file (if supported).
        
        Args:
            path: Storage path
        
        Returns:
            Public URL
        """
        pass

