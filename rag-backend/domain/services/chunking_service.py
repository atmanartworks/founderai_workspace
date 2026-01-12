"""
Chunking Domain Service

Pure business logic for splitting text into chunks.
NO external dependencies - just pure Python.
"""
import math
from typing import List, Tuple


class ChunkingDomainService:
    """
    Domain service for text chunking.
    
    Business Rules:
    - Chunks should be ~1000 characters for optimal embedding
    - Overlap between chunks preserves context
    - Break at sentence boundaries when possible
    - Each chunk tracks its position (index)
    """
    
    def __init__(self, max_chars: int = 1000, overlap: int = 200):
        """
        Initialize chunking service.
        
        Args:
            max_chars: Maximum characters per chunk
            overlap: Characters to overlap between chunks
        """
        if max_chars <= 0:
            raise ValueError("max_chars must be positive")
        if overlap < 0:
            raise ValueError("overlap must be non-negative")
        if overlap >= max_chars:
            raise ValueError("overlap must be less than max_chars")
        
        self.max_chars = max_chars
        self.overlap = overlap
    
    def chunk_text(self, text: str) -> List[Tuple[str, int]]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: The text to chunk
        
        Returns:
            List of tuples: (chunk_content, chunk_index)
        
        Business Logic:
        1. Start at position 0
        2. Take max_chars characters
        3. Try to break at sentence boundary (newline or period)
        4. Add chunk
        5. Move forward by (chunk_size - overlap)
        6. Repeat until end of text
        """
        if not text or not text.strip():
            return []
        
        text = text.strip()
        length = len(text)
        chunks = []
        start = 0
        index = 0
        
        while start < length:
            end = start + self.max_chars
            chunk_content = text[start:end]
            
            # Try to break at sentence boundary if not at end
            if end < length:
                # Look ahead up to 100 chars for a good break point
                next_break = self._find_sentence_boundary(text, end, min(end + 100, length))
                if next_break != -1:
                    chunk_content = text[start:next_break + 1]
                    end = next_break + 1
            
            chunks.append((chunk_content.strip(), index))
            index += 1
            
            # Move forward with overlap
            new_start = end - self.overlap
            if new_start <= start:
                # Prevent infinite loop
                start = end
            else:
                start = new_start
        
        return chunks
    
    def _find_sentence_boundary(self, text: str, start: int, end: int) -> int:
        """
        Find the best sentence boundary in the range [start, end].
        
        Priority:
        1. Newline (paragraph break)
        2. Period (sentence break)
        
        Returns:
            Index of boundary, or -1 if not found
        """
        # Look for newline first (stronger boundary)
        newline_pos = text.find("\n", start, end)
        if newline_pos != -1:
            return newline_pos
        
        # Fall back to period
        period_pos = text.find(".", start, end)
        if period_pos != -1:
            return period_pos
        
        return -1
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.
        
        Business Rule: Approximately 1 token per 4 characters
        (This is a heuristic - actual tokenization varies by model)
        
        Args:
            text: The text to estimate
        
        Returns:
            Estimated token count
        """
        if not text:
            return 0
        return max(1, math.ceil(len(text) / 4.0))
    
    def validate_chunk_size(self, text: str) -> bool:
        """
        Check if text is a valid chunk size.
        
        Returns:
            True if text is within acceptable size
        """
        return 0 < len(text) <= self.max_chars + 100  # Allow 100 char buffer

