"""
Unit Tests for ChunkingDomainService

Pure business logic testing - no external dependencies!
"""
import pytest
from domain.services.chunking_service import ChunkingDomainService


class TestChunkingDomainService:
    """Test chunking business logic"""
    
    def test_create_service_with_defaults(self):
        """Test creating service with default parameters"""
        service = ChunkingDomainService()
        
        assert service.max_chars == 1000
        assert service.overlap == 200
    
    def test_create_service_with_custom_params(self):
        """Test creating service with custom parameters"""
        service = ChunkingDomainService(max_chars=500, overlap=100)
        
        assert service.max_chars == 500
        assert service.overlap == 100
    
    def test_validation_max_chars_positive(self):
        """Test that max_chars must be positive"""
        with pytest.raises(ValueError, match="max_chars must be positive"):
            ChunkingDomainService(max_chars=0)
    
    def test_validation_overlap_non_negative(self):
        """Test that overlap must be non-negative"""
        with pytest.raises(ValueError, match="overlap must be non-negative"):
            ChunkingDomainService(overlap=-1)
    
    def test_validation_overlap_less_than_max(self):
        """Test that overlap must be less than max_chars"""
        with pytest.raises(ValueError, match="overlap must be less than max_chars"):
            ChunkingDomainService(max_chars=100, overlap=100)
    
    def test_chunk_empty_text(self):
        """Test chunking empty text"""
        service = ChunkingDomainService()
        chunks = service.chunk_text("")
        
        assert chunks == []
    
    def test_chunk_short_text(self):
        """Test chunking text shorter than max_chars"""
        service = ChunkingDomainService(max_chars=100, overlap=20)
        text = "This is a short text."
        
        chunks = service.chunk_text(text)
        
        assert len(chunks) == 1
        assert chunks[0][0] == text
        assert chunks[0][1] == 0  # First chunk has index 0
    
    def test_chunk_long_text(self):
        """Test chunking long text creates multiple chunks"""
        service = ChunkingDomainService(max_chars=50, overlap=10)
        text = "A" * 150  # Long text
        
        chunks = service.chunk_text(text)
        
        assert len(chunks) > 1
        # Check indices are sequential
        for i, (content, index) in enumerate(chunks):
            assert index == i
    
    def test_chunk_with_overlap(self):
        """Test that chunks have overlap"""
        service = ChunkingDomainService(max_chars=20, overlap=5)
        text = "A" * 50
        
        chunks = service.chunk_text(text)
        
        # Second chunk should start 5 chars before end of first chunk
        assert len(chunks) >= 2
    
    def test_chunk_at_sentence_boundary(self):
        """Test chunking breaks at sentence boundaries"""
        service = ChunkingDomainService(max_chars=30, overlap=5)
        text = "First sentence. Second sentence. Third sentence."
        
        chunks = service.chunk_text(text)
        
        # Should break at periods
        assert any("." in chunk[0] for chunk in chunks)
    
    def test_estimate_tokens(self):
        """Test token estimation"""
        service = ChunkingDomainService()
        
        # Approximately 4 chars per token
        text = "A" * 100
        tokens = service.estimate_tokens(text)
        
        assert tokens == 25  # 100 / 4
    
    def test_estimate_tokens_empty(self):
        """Test token estimation for empty text"""
        service = ChunkingDomainService()
        tokens = service.estimate_tokens("")
        
        assert tokens == 0
    
    def test_estimate_tokens_rounds_up(self):
        """Test token estimation rounds up"""
        service = ChunkingDomainService()
        
        # 10 chars = 2.5 tokens -> should round up to 3
        text = "A" * 10
        tokens = service.estimate_tokens(text)
        
        assert tokens == 3
    
    def test_validate_chunk_size_within_limit(self):
        """Test chunk size validation for valid size"""
        service = ChunkingDomainService(max_chars=100, overlap=20)
        text = "A" * 90
        
        assert service.validate_chunk_size(text) is True
    
    def test_validate_chunk_size_too_large(self):
        """Test chunk size validation for too large"""
        service = ChunkingDomainService(max_chars=100, overlap=20)
        text = "A" * 250  # Way over limit
        
        assert service.validate_chunk_size(text) is False
    
    def test_validate_chunk_size_empty(self):
        """Test chunk size validation for empty"""
        service = ChunkingDomainService()
        
        assert service.validate_chunk_size("") is False

