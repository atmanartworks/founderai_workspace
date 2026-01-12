"""
Base Domain Exception

All domain exceptions inherit from this.
"""


class DomainException(Exception):
    """
    Base exception for all domain-level errors.
    
    These represent business rule violations, not technical errors.
    """
    
    def __init__(self, message: str, error_code: str = "DOMAIN_ERROR"):
        """
        Initialize domain exception.
        
        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
    
    def __str__(self) -> str:
        return f"[{self.error_code}] {self.message}"

