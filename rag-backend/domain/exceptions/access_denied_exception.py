"""
Access Denied Exception

Raised when user tries to access resource they don't own.
"""
from .domain_exception import DomainException


class AccessDeniedException(DomainException):
    """
    Raised when user doesn't have permission to access a resource.
    
    Business Rule: Users can only access their own data.
    """
    
    def __init__(self, resource_type: str, resource_id: str, user_id: str):
        message = f"User '{user_id}' does not have access to {resource_type} '{resource_id}'"
        super().__init__(message, "ACCESS_DENIED")
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.user_id = user_id

