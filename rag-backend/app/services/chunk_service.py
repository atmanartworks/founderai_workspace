# app/services/chunk_service.py
import math

class ChunkingService:
    @staticmethod
    def chunk_text(text: str, max_chars: int = 1000, overlap: int = 200):
        if not text:
            return []
        text = text.strip()
        length = len(text)
        chunks = []
        start = 0
        idx = 0
        while start < length:
            end = start + max_chars
            chunk_text = text[start:end]
            if end < length:
                # attempt to slice at sentence/newline boundary up to 100 chars forward
                next_break = text.find("\n", end, min(end+100, length))
                if next_break == -1:
                    next_break = text.find(".", end, min(end+100, length))
                if next_break != -1:
                    chunk_text = text[start:next_break+1]
                    end = next_break+1
            chunks.append({
                "content": chunk_text.strip(),
                "tokens": max(1, math.ceil(len(chunk_text) / 4)),
                "chunk_index": idx
            })
            idx += 1
            # advance with overlap
            new_start = end - overlap
            if new_start <= start:
                start = end
            else:
                start = new_start
        return chunks


# Wrapper function for backward compatibility
def chunk_text(text: str, max_chars: int = 1000, overlap: int = 200):
    return ChunkingService.chunk_text(text, max_chars, overlap)
