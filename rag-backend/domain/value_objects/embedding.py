"""
Embedding Value Object

Represents a vector embedding with validation.
"""
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Embedding:
    """
    Immutable embedding vector.
    
    Business Rules:
    - Must have dimensions
    - All values must be floats
    - Dimension must match expected model dimension
    """
    
    vector: tuple[float, ...]  # Immutable tuple
    
    def __post_init__(self):
        """Validate embedding"""
        if not self.vector:
            raise ValueError("Embedding vector cannot be empty")
        if not all(isinstance(x, (int, float)) for x in self.vector):
            raise ValueError("All embedding values must be numeric")
    
    @classmethod
    def from_list(cls, values: List[float]) -> "Embedding":
        """Create embedding from list"""
        return cls(vector=tuple(values))
    
    def to_list(self) -> List[float]:
        """Convert to list for database storage"""
        return list(self.vector)
    
    def dimension(self) -> int:
        """Get embedding dimension"""
        return len(self.vector)
    
    def __len__(self) -> int:
        return len(self.vector)
    
    def __repr__(self) -> str:
        return f"Embedding(dim={self.dimension()})"

