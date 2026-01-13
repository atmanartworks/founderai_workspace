# app/services/faiss_store.py

"""
FAISS-based vector store for RAG.
Stores embeddings locally using FAISS and metadata in pickle files.
Supports multi-user isolation via user_id filtering.
"""

import os
import pickle
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import numpy as np

import faiss

# Storage directory for FAISS indices and metadata
STORAGE_DIR = Path(__file__).parent.parent.parent / "faiss_storage"
STORAGE_DIR.mkdir(exist_ok=True)

# Global index and metadata (loaded on demand)
_global_index: Optional[faiss.Index] = None
_chunks_metadata: List[Dict] = []
_index_loaded = False

def get_index_path() -> Path:
    """Get path to FAISS index file"""
    return STORAGE_DIR / "foundergpt.index"

def get_metadata_path() -> Path:
    """Get path to chunks metadata file"""
    return STORAGE_DIR / "chunks_metadata.pkl"

def load_index() -> Tuple[faiss.Index, List[Dict]]:
    """Load FAISS index and metadata from disk"""
    global _global_index, _chunks_metadata, _index_loaded
    
    if _index_loaded and _global_index is not None:
        return _global_index, _chunks_metadata
    
    index_path = get_index_path()
    metadata_path = get_metadata_path()
    
    if not index_path.exists() or not metadata_path.exists():
        # Create new empty index
        # Detect embedding dimension from config or default to 1536 (OpenAI) or 768 (nomic)
        from app.config import LOCAL_EMBEDDING_MODEL
        # OpenAI embeddings are 1536, nomic is 768
        if "openai" in LOCAL_EMBEDDING_MODEL.lower() or LOCAL_EMBEDDING_MODEL.lower().startswith("text-embedding"):
            EMBED_DIM = 1536
        else:
            EMBED_DIM = 768  # Default for nomic and other models
        _global_index = faiss.IndexFlatIP(EMBED_DIM)  # Inner product for cosine similarity
        _chunks_metadata = []
        _index_loaded = True
        logging.info(f"Created new empty FAISS index with dimension {EMBED_DIM}")
        return _global_index, _chunks_metadata
    
    try:
        # Load index
        _global_index = faiss.read_index(str(index_path))
        
        # Load metadata
        with open(metadata_path, "rb") as f:
            _chunks_metadata = pickle.load(f)
        
        _index_loaded = True
        logging.info(f"Loaded FAISS index with {len(_chunks_metadata)} chunks (dimension: {_global_index.d})")
        return _global_index, _chunks_metadata
    except Exception as e:
        logging.error(f"Error loading FAISS index: {e}")
        # Create new empty index
        from app.config import LOCAL_EMBEDDING_MODEL
        # OpenAI embeddings are 1536, nomic is 768
        if "openai" in LOCAL_EMBEDDING_MODEL.lower() or LOCAL_EMBEDDING_MODEL.lower().startswith("text-embedding"):
            EMBED_DIM = 1536
        else:
            EMBED_DIM = 768  # Default for nomic and other models
        _global_index = faiss.IndexFlatIP(EMBED_DIM)
        _chunks_metadata = []
        _index_loaded = True
        logging.info(f"Created new empty FAISS index with dimension {EMBED_DIM} after error")
        return _global_index, _chunks_metadata

def save_index(index: faiss.Index, metadata: List[Dict]):
    """Save FAISS index and metadata to disk"""
    index_path = get_index_path()
    metadata_path = get_metadata_path()
    
    try:
        # Save index
        faiss.write_index(index, str(index_path))
        
        # Save metadata
        with open(metadata_path, "wb") as f:
            pickle.dump(metadata, f)
        
        logging.info(f"Saved FAISS index with {len(metadata)} chunks")
    except Exception as e:
        logging.error(f"Error saving FAISS index: {e}")
        raise

def add_chunks(embeddings: np.ndarray, chunks_metadata: List[Dict]):
    """
    Add new chunks to the FAISS index.
    
    Args:
        embeddings: numpy array of shape (n_chunks, embed_dim) - must be normalized
                    embed_dim is 768 for nomic, 1536 for OpenAI
        chunks_metadata: List of dicts with keys: content, vault_id, user_id, chunk_index
    """
    global _global_index, _chunks_metadata, _index_loaded
    
    if len(embeddings) == 0:
        logging.warning("No embeddings to add")
        return
    
    # Detect embedding dimension from the actual embeddings
    embed_dim = embeddings.shape[1] if len(embeddings.shape) > 1 else len(embeddings[0])
    logging.info(f"Detected embedding dimension: {embed_dim}")
    
    index, metadata = load_index()
    
    # Check if index dimension matches embedding dimension
    if index.d != embed_dim:
        logging.warning(f"Index dimension ({index.d}) doesn't match embedding dimension ({embed_dim}). Creating new index.")
        # Create new index with correct dimension
        _global_index = faiss.IndexFlatIP(embed_dim)
        _chunks_metadata = []
        _index_loaded = True
        index = _global_index
        metadata = _chunks_metadata
        # Remove old index files to start fresh
        try:
            get_index_path().unlink(missing_ok=True)
            get_metadata_path().unlink(missing_ok=True)
            logging.info("Removed old index files with mismatched dimension")
        except Exception as e:
            logging.warning(f"Could not remove old index files: {e}")
    
    # Normalize embeddings for cosine similarity (FAISS IndexFlatIP expects normalized vectors)
    faiss.normalize_L2(embeddings)
    
    # Add to index
    index.add(embeddings)
    
    # Add metadata
    metadata.extend(chunks_metadata)
    
    # Save
    save_index(index, metadata)
    
    # Update global state
    _global_index = index
    _chunks_metadata = metadata
    
    logging.info(f"Added {len(chunks_metadata)} chunks to FAISS index")

def delete_chunks_by_vault(vault_id: str):
    """
    Delete all chunks for a specific vault_id.
    Note: This removes metadata but doesn't rebuild the index.
    The index will be inconsistent until new chunks are added.
    For production, implement proper index rebuild or store embeddings separately.
    """
    index, metadata = load_index()
    
    if not metadata:
        return
    
    # Filter out chunks for this vault
    filtered_metadata = [m for m in metadata if m.get("vault_id") != vault_id]
    
    if len(filtered_metadata) == len(metadata):
        # No chunks to delete
        return
    
    # Count how many we're deleting
    deleted_count = len(metadata) - len(filtered_metadata)
    
    # For MVP: Just update metadata
    # The index will have orphaned vectors, but they won't be returned since metadata is filtered
    # This is acceptable for MVP - in production, rebuild the index properly
    save_index(index, filtered_metadata)
    
    global _global_index, _chunks_metadata
    _chunks_metadata = filtered_metadata
    
    logging.info(f"Deleted {deleted_count} chunks for vault_id {vault_id} (metadata updated, index has orphaned vectors)")

def search(
    query_embedding: np.ndarray,
    user_id: str,
    top_k: int = 5,
    vault_id: Optional[str] = None
) -> List[Dict]:
    """
    Search for similar chunks in FAISS index.
    
    Args:
        query_embedding: numpy array of shape (1, embed_dim) - must be normalized
                        embed_dim is 768 for nomic, 1536 for OpenAI
        user_id: Filter results by user_id
        top_k: Number of results to return
        vault_id: Optional filter by vault_id
    
    Returns:
        List of dicts with keys: content, vault_id, user_id, chunk_index, score
    """
    index, metadata = load_index()
    
    if index.ntotal == 0:
        return []
    
    # Normalize query embedding
    query_embedding = query_embedding.astype(np.float32)
    faiss.normalize_L2(query_embedding)
    
    # Search (get more results to filter by user_id/vault_id)
    search_k = top_k * 10  # Get more candidates for filtering
    scores, indices = index.search(query_embedding, min(search_k, index.ntotal))
    
    # Filter by user_id and optionally vault_id
    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < 0 or idx >= len(metadata):
            continue
        
        chunk_meta = metadata[idx]
        
        # Filter by user_id
        if chunk_meta.get("user_id") != user_id:
            continue
        
        # Filter by vault_id if specified
        if vault_id and chunk_meta.get("vault_id") != vault_id:
            continue
        
        # Add score to result
        result = chunk_meta.copy()
        result["score"] = float(score)
        results.append(result)
        
        if len(results) >= top_k:
            break
    
    return results

def get_stats() -> Dict:
    """Get statistics about the FAISS index"""
    index, metadata = load_index()
    
    # Count by user_id
    user_counts = {}
    vault_counts = {}
    
    for chunk in metadata:
        user_id = chunk.get("user_id", "unknown")
        vault_id = chunk.get("vault_id", "unknown")
        user_counts[user_id] = user_counts.get(user_id, 0) + 1
        vault_counts[vault_id] = vault_counts.get(vault_id, 0) + 1
    
    return {
        "total_chunks": len(metadata),
        "index_size": index.ntotal,
        "users": len(user_counts),
        "vaults": len(vault_counts),
        "user_counts": user_counts,
        "vault_counts": vault_counts
    }

