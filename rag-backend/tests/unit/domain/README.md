# Domain Layer Unit Tests

## How to Run

```bash
# Run all domain tests
pytest tests/unit/domain/

# Run specific test file
pytest tests/unit/domain/test_conversation_entity.py

# Run with verbose output
pytest tests/unit/domain/ -v

# Run and show print statements
pytest tests/unit/domain/ -s
```

## Test Files

1. **`test_conversation_entity.py`** - Conversation entity tests
2. **`test_chunking_service.py`** - Chunking business logic tests
3. **`test_text_cleaner.py`** - Text cleaning business logic tests

## Key Features

✅ **Zero Dependencies** - No database, no API, no mocks needed
✅ **Pure Logic** - Testing business rules only
✅ **Fast** - Run in milliseconds
✅ **Reliable** - No flaky tests

## Example

```python
def test_conversation_requires_user_id():
    """Test that user_id is required"""
    with pytest.raises(ValueError, match="user_id is required"):
        Conversation(user_id="", title="Test")
```

This is **true unit testing** - testing pure business logic!

