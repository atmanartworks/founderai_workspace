"""
Unit Tests for TextCleaner

Pure business logic testing!
"""
import pytest
from domain.services.text_cleaner import TextCleaner


class TestTextCleaner:
    """Test text cleaning business logic"""
    
    def test_clean_removes_null_bytes(self):
        """Test that null bytes are removed"""
        text = "Hello\x00World"
        cleaned = TextCleaner.clean(text)
        
        assert "\x00" not in cleaned
        assert cleaned == "HelloWorld"
    
    def test_clean_handles_empty_string(self):
        """Test cleaning empty string"""
        cleaned = TextCleaner.clean("")
        assert cleaned == ""
    
    def test_clean_handles_none(self):
        """Test cleaning None"""
        cleaned = TextCleaner.clean(None)
        assert cleaned == ""
    
    def test_clean_strips_whitespace(self):
        """Test that whitespace is stripped"""
        text = "  Hello World  "
        cleaned = TextCleaner.clean(text)
        
        assert cleaned == "Hello World"
    
    def test_clean_handles_unicode_errors(self):
        """Test that Unicode errors are handled gracefully"""
        # This should not raise an exception
        text = "Hello\udcffWorld"  # Invalid Unicode
        cleaned = TextCleaner.clean(text)
        
        assert isinstance(cleaned, str)
    
    def test_is_valid_with_valid_text(self):
        """Test validation of valid text"""
        assert TextCleaner.is_valid("Hello World") is True
    
    def test_is_valid_with_empty_string(self):
        """Test validation of empty string"""
        assert TextCleaner.is_valid("") is False
    
    def test_is_valid_with_whitespace_only(self):
        """Test validation of whitespace-only string"""
        assert TextCleaner.is_valid("   ") is False
    
    def test_is_valid_with_null_bytes_only(self):
        """Test validation of null bytes only"""
        assert TextCleaner.is_valid("\x00\x00") is False
    
    def test_normalize_whitespace_converts_crlf(self):
        """Test that CRLF is converted to LF"""
        text = "Line1\r\nLine2\r\nLine3"
        normalized = TextCleaner.normalize_whitespace(text)
        
        assert "\r\n" not in normalized
        assert "Line1\nLine2\nLine3" == normalized
    
    def test_normalize_whitespace_removes_excessive_blank_lines(self):
        """Test that excessive blank lines are removed"""
        text = "Line1\n\n\n\nLine2"
        normalized = TextCleaner.normalize_whitespace(text)
        
        assert normalized == "Line1\n\nLine2"
    
    def test_normalize_whitespace_converts_tabs(self):
        """Test that tabs are converted to spaces"""
        text = "Hello\tWorld"
        normalized = TextCleaner.normalize_whitespace(text)
        
        assert "\t" not in normalized
        assert "    " in normalized  # 4 spaces
    
    def test_normalize_whitespace_strips_ends(self):
        """Test that leading/trailing whitespace is stripped"""
        text = "  \n\nHello\n\n  "
        normalized = TextCleaner.normalize_whitespace(text)
        
        assert normalized == "Hello"
    
    def test_remove_control_characters(self):
        """Test removal of control characters"""
        text = "Hello\x01\x02World"
        cleaned = TextCleaner.remove_control_characters(text)
        
        assert "\x01" not in cleaned
        assert "\x02" not in cleaned
        assert cleaned == "HelloWorld"
    
    def test_remove_control_characters_keeps_newlines(self):
        """Test that newlines are preserved"""
        text = "Line1\nLine2"
        cleaned = TextCleaner.remove_control_characters(text)
        
        assert "\n" in cleaned
        assert cleaned == "Line1\nLine2"
    
    def test_remove_control_characters_keeps_tabs(self):
        """Test that tabs are preserved"""
        text = "Hello\tWorld"
        cleaned = TextCleaner.remove_control_characters(text)
        
        assert "\t" in cleaned
        assert cleaned == "Hello\tWorld"

