# app/services/constraint_extractor.py

import re
from typing import Dict

def extract_constraints(input_text: str) -> Dict[str, any]:
    """
    Extracts constraints from user input:
    - lines: Number of lines requested (e.g., "3 lines", "5 lines")
    - short: Whether user wants a short/brief answer
    - steps: Whether user wants step-by-step format
    """
    input_lower = input_text.lower()
    
    # Extract line count (e.g., "3 lines", "5 lines", "in 2 lines")
    lines_match = re.search(r'(\d+)\s*lines?', input_lower)
    lines = int(lines_match.group(1)) if lines_match else 0
    
    # Check for short/brief requests
    short = bool(re.search(r'\b(short|brief|concise|quick)\b', input_lower))
    
    # Check for step-by-step requests
    steps = bool(re.search(r'\b(step|steps|step-by-step|numbered)\b', input_lower))
    
    return {
        "lines": lines,
        "short": short,
        "steps": steps
    }

