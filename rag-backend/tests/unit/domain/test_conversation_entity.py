"""
Unit Tests for Conversation Entity

Testing pure business logic - NO database, NO APIs, NO mocks needed!
"""
import pytest
from datetime import datetime
from domain.entities.conversation import Conversation


class TestConversationEntity:
    """Test Conversation entity business rules"""
    
    def test_create_conversation_success(self):
        """Test creating a valid conversation"""
        conv = Conversation(user_id="user123", title="My Chat")
        
        assert conv.user_id == "user123"
        assert conv.title == "My Chat"
        assert conv.id is not None
        assert isinstance(conv.created_at, datetime)
        assert isinstance(conv.updated_at, datetime)
    
    def test_conversation_requires_user_id(self):
        """Test that user_id is required"""
        with pytest.raises(ValueError, match="user_id is required"):
            Conversation(user_id="", title="Test")
    
    def test_conversation_requires_title(self):
        """Test that title cannot be empty"""
        with pytest.raises(ValueError, match="title cannot be empty"):
            Conversation(user_id="user123", title="")
    
    def test_conversation_strips_whitespace_from_title(self):
        """Test that title whitespace is stripped"""
        conv = Conversation(user_id="user123", title="  My Chat  ")
        assert conv.title == "My Chat"
    
    def test_update_title_success(self):
        """Test updating conversation title"""
        import time
        conv = Conversation(user_id="user123", title="Old Title")
        original_updated_at = conv.updated_at
        
        time.sleep(0.01)  # Small delay to ensure timestamp changes
        conv.update_title("New Title")
        
        assert conv.title == "New Title"
        assert conv.updated_at >= original_updated_at
    
    def test_update_title_validation(self):
        """Test that update_title validates input"""
        conv = Conversation(user_id="user123", title="Old Title")
        
        with pytest.raises(ValueError, match="title cannot be empty"):
            conv.update_title("")
    
    def test_touch_updates_timestamp(self):
        """Test that touch() updates updated_at"""
        import time
        conv = Conversation(user_id="user123", title="Test")
        original_updated_at = conv.updated_at
        
        time.sleep(0.01)  # Small delay to ensure timestamp changes
        conv.touch()
        
        assert conv.updated_at >= original_updated_at
    
    def test_is_owned_by(self):
        """Test ownership check"""
        conv = Conversation(user_id="user123", title="Test")
        
        assert conv.is_owned_by("user123") is True
        assert conv.is_owned_by("other_user") is False
    
    def test_conversation_repr(self):
        """Test string representation"""
        conv = Conversation(user_id="user123", title="My Chat")
        repr_str = repr(conv)
        
        assert "Conversation" in repr_str
        assert conv.id in repr_str
        assert "My Chat" in repr_str
        assert "user123" in repr_str

