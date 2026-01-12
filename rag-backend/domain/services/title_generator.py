"""
Title Generator Domain Service

Pure business logic for generating conversation titles.
"""


class TitleGenerator:
    """
    Domain service for generating conversation titles.
    
    Business Rules:
    - Titles should be descriptive but concise
    - Extract key topics from first message
    - Maximum 50 characters
    - Fallback to "New Conversation" if extraction fails
    """
    
    MAX_TITLE_LENGTH = 50
    
    @staticmethod
    def generate_from_message(message: str) -> str:
        """
        Generate a conversation title from the first message.
        
        Args:
            message: The first message in the conversation
        
        Returns:
            Generated title (max 50 chars)
        
        Business Logic:
        1. Take first sentence or 50 chars
        2. Remove questions marks and formatting
        3. Capitalize properly
        4. Fallback to "New Conversation" if too short
        """
        if not message or not message.strip():
            return "New Conversation"
        
        message = message.strip()
        
        # Take first sentence (up to . or ?)
        title = message
        for delimiter in [".", "?", "!", "\n"]:
            if delimiter in message:
                title = message.split(delimiter)[0]
                break
        
        # Limit length
        if len(title) > TitleGenerator.MAX_TITLE_LENGTH:
            title = title[:TitleGenerator.MAX_TITLE_LENGTH].rsplit(" ", 1)[0]
        
        # Clean up
        title = title.strip()
        
        # Ensure it starts with capital letter
        if title:
            title = title[0].upper() + title[1:]
        
        # Fallback if too short
        if len(title) < 3:
            return "New Conversation"
        
        return title
    
    @staticmethod
    def extract_keywords(message: str, max_keywords: int = 3) -> list[str]:
        """
        Extract key words from message (simple implementation).
        
        Args:
            message: The message to analyze
            max_keywords: Maximum keywords to extract
        
        Returns:
            List of keywords
        
        Note: This is a simple implementation.
        Could be enhanced with NLP libraries in infrastructure layer.
        """
        if not message:
            return []
        
        # Remove common words
        common_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", 
            "for", "of", "with", "is", "are", "was", "were", "be", "been",
            "have", "has", "had", "do", "does", "did", "will", "would",
            "can", "could", "should", "may", "might", "must", "i", "you",
            "he", "she", "it", "we", "they", "my", "your", "his", "her",
            "what", "how", "why", "when", "where", "who", "which"
        }
        
        # Split into words and clean
        words = message.lower().split()
        words = [word.strip(".,!?;:") for word in words]
        
        # Filter common words and short words
        keywords = [
            word for word in words 
            if word not in common_words and len(word) > 3
        ]
        
        # Return first N unique keywords
        unique_keywords = []
        for word in keywords:
            if word not in unique_keywords:
                unique_keywords.append(word)
            if len(unique_keywords) >= max_keywords:
                break
        
        return unique_keywords

