# app/services/answer_enforcer.py

import re
from typing import Optional

def enforce_constraints(answer: str, lines: int = 0, short: bool = False, steps: bool = False) -> str:
    """
    Post-processes the answer to enforce user constraints.
    This is a fail-safe to ensure constraints are met even if the LLM doesn't follow them perfectly.
    """
    if not answer:
        return answer
    
    # Enforce line count if specified (STRICT enforcement)
    if lines > 0:
        # Split by newlines and filter empty lines
        answer_lines = [line.strip() for line in answer.split("\n") if line.strip()]
        
        # If we have more lines than requested, truncate strictly
        if len(answer_lines) > lines:
            answer_lines = answer_lines[:lines]
        
        # Also limit each line to ~20 words max (as per prompt requirement)
        trimmed_lines = []
        for line in answer_lines:
            words = line.split()
            if len(words) > 20:
                line = " ".join(words[:20])
            trimmed_lines.append(line)
        
        answer = "\n".join(trimmed_lines)
    
    # If short was requested but no line count, limit to first 3 sentences
    if short and lines == 0:
        sentences = re.split(r'[.!?]+', answer)
        sentences = [s.strip() for s in sentences if s.strip()]
        if len(sentences) > 3:
            answer = ". ".join(sentences[:3]) + "."
    
    # If steps requested, ensure numbered format
    if steps:
        lines_list = answer.split("\n")
        numbered_lines = []
        step_num = 1
        for line in lines_list:
            line = line.strip()
            if not line:
                continue
            # If already numbered, keep it; otherwise add number
            if re.match(r'^\d+[\.\)]\s*', line):
                numbered_lines.append(line)
            else:
                numbered_lines.append(f"{step_num}. {line}")
                step_num += 1
        answer = "\n".join(numbered_lines)
    
    return answer.strip()

