"""
Text Cleaner Domain Service

Pure business logic for cleaning and sanitizing text.
"""


class TextCleaner:
    """
    Domain service for text cleaning.
    
    Business Rules:
    - Remove null bytes (cause database errors)
    - Handle Unicode encoding issues
    - Normalize whitespace
    - Preserve meaningful content
    """
    
    @staticmethod
    def clean(text: str) -> str:
        """
        Clean text for database storage and processing.
        
        Args:
            text: The text to clean
        
        Returns:
            Cleaned text
        
        Business Logic:
        1. Remove null bytes (\x00)
        2. Handle Unicode encoding errors
        3. Strip leading/trailing whitespace
        4. Return empty string if nothing left
        """
        if not text:
            return ""
        
        # Remove null bytes (PostgreSQL doesn't allow them)
        text = text.replace("\x00", "")
        
        # Handle Unicode encoding issues
        text = text.encode("utf-8", "ignore").decode("utf-8", "ignore")
        
        # Strip whitespace
        text = text.strip()
        
        return text
    
    @staticmethod
    def is_valid(text: str) -> bool:
        """
        Check if text is valid (not empty after cleaning).
        
        Args:
            text: The text to validate
        
        Returns:
            True if valid, False if empty/invalid
        """
        if not text:
            return False
        cleaned = TextCleaner.clean(text)
        return len(cleaned) > 0
    
    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """
        Normalize whitespace in text.
        
        Business Rules:
        - Convert CRLF to LF
        - Remove excessive blank lines
        - Preserve paragraph structure
        
        Args:
            text: The text to normalize
        
        Returns:
            Text with normalized whitespace
        """
        if not text:
            return ""
        
        # Convert Windows line endings to Unix
        text = text.replace("\r\n", "\n")
        
        # Replace multiple blank lines with double newline
        while "\n\n\n" in text:
            text = text.replace("\n\n\n", "\n\n")
        
        # Replace tabs with spaces
        text = text.replace("\t", "    ")
        
        return text.strip()
    
    @staticmethod
    def remove_control_characters(text: str) -> str:
        """
        Remove control characters except newlines and tabs.
        
        Args:
            text: The text to clean
        
        Returns:
            Text without control characters
        """
        if not text:
            return ""
        
        # Keep only printable characters, newlines, and tabs
        return "".join(
            char for char in text 
            if char.isprintable() or char in ["\n", "\t"]
        )

