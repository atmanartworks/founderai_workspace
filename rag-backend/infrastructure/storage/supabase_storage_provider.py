"""
Supabase Storage Provider Implementation

Implements the StorageProvider interface using Supabase Storage.
"""
import os
import logging
from typing import Optional
from application.interfaces.storage_provider import StorageProvider

try:
    from supabase import Client
except ImportError:
    Client = None


class SupabaseStorageProvider(StorageProvider):
    """
    Supabase Storage provider implementation.
    
    This is an INFRASTRUCTURE implementation of the Application interface.
    """
    
    def __init__(self, client: 'Client', bucket_name: str = "vault"):
        """
        Initialize Supabase storage provider.
        
        Args:
            client: Supabase client instance
            bucket_name: Storage bucket name
        """
        if Client is None:
            raise ImportError("supabase package not installed")
        
        self.client = client
        self.bucket_name = bucket_name
        
        logging.info(f"Supabase Storage Provider initialized with bucket: {self.bucket_name}")
    
    async def upload_file(
        self, 
        file_content: bytes, 
        path: str,
        content_type: Optional[str] = None
    ) -> str:
        """
        Upload file to Supabase Storage.
        
        Implementation of StorageProvider interface.
        """
        try:
            # Upload to Supabase Storage
            self.client.storage.from_(self.bucket_name).upload(
                path=path,
                file=file_content,
                file_options={"content-type": content_type} if content_type else None
            )
            
            logging.info(f"File uploaded successfully: {path}")
            return path
            
        except Exception as e:
            logging.error(f"File upload error: {e}")
            raise RuntimeError(f"File upload failed: {str(e)}") from e
    
    async def download_file(self, path: str) -> bytes:
        """
        Download file from Supabase Storage.
        
        Implementation of StorageProvider interface.
        """
        try:
            # Download from Supabase Storage
            file_bytes = self.client.storage.from_(self.bucket_name).download(path)
            
            if not file_bytes:
                raise FileNotFoundError(f"File not found: {path}")
            
            logging.info(f"File downloaded successfully: {path}")
            return file_bytes
            
        except Exception as e:
            logging.error(f"File download error: {e}")
            if "not found" in str(e).lower():
                raise FileNotFoundError(f"File not found: {path}") from e
            raise RuntimeError(f"File download failed: {str(e)}") from e
    
    async def delete_file(self, path: str) -> bool:
        """
        Delete file from Supabase Storage.
        
        Implementation of StorageProvider interface.
        """
        try:
            # Delete from Supabase Storage
            self.client.storage.from_(self.bucket_name).remove([path])
            
            logging.info(f"File deleted successfully: {path}")
            return True
            
        except Exception as e:
            logging.error(f"File deletion error: {e}")
            if "not found" in str(e).lower():
                return False
            raise RuntimeError(f"File deletion failed: {str(e)}") from e
    
    async def file_exists(self, path: str) -> bool:
        """
        Check if file exists in Supabase Storage.
        
        Implementation of StorageProvider interface.
        """
        try:
            # Try to get file info
            files = self.client.storage.from_(self.bucket_name).list(path=os.path.dirname(path))
            filename = os.path.basename(path)
            
            return any(f.get("name") == filename for f in files)
            
        except Exception as e:
            logging.warning(f"File exists check error: {e}")
            return False
    
    def get_public_url(self, path: str) -> str:
        """
        Get public URL for file.
        
        Implementation of StorageProvider interface.
        """
        try:
            # Get public URL from Supabase
            url_response = self.client.storage.from_(self.bucket_name).get_public_url(path)
            return url_response
            
        except Exception as e:
            logging.error(f"Get public URL error: {e}")
            raise RuntimeError(f"Failed to get public URL: {str(e)}") from e

