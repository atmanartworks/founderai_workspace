"""
Validation Exception

Raised when business rules are violated.
"""
from .domain_exception import DomainException


class ValidationException(DomainException):
    """
    Raised when validation fails.
    
    Examples:
    - Empty required field
    - Invalid format
    - Business rule violation
    """
    
    def __init__(self, message: str, field: str = None):
        super().__init__(message, "VALIDATION_ERROR")
        self.field = field
    
    def __str__(self) -> str:
        if self.field:
            return f"[{self.error_code}] {self.field}: {self.message}"
        return f"[{self.error_code}] {self.message}"

