# app/utils/sse.py

import json
from typing import Any, Dict

def sse_event(event: str, data: Dict[str, Any]) -> str:
    """
    Format data as Server-Sent Events (SSE) message.
    
    Args:
        event: Event type (e.g., "token", "done")
        data: Data to send (will be JSON serialized)
    
    Returns:
        Formatted SSE string
    """
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"
