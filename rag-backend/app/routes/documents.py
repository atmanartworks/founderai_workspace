# app/routes/documents.py

"""
API routes for retrieving document chunks for viewing.
"""

import logging
from fastapi import APIRouter, HTTPException
from typing import List, Dict
from app.database import supabase
from app.services.faiss_store import load_index

router = APIRouter(prefix="/api/documents", tags=["documents"])

@router.get("/{document_id}/chunks")
async def get_document_chunks(document_id: str, user_id: str):
    """
    Get all chunks for a specific document.
    
    Returns chunks with their content, chunk_index, and metadata.
    """
    try:
        # Verify document exists and belongs to user
        doc_result = supabase.table("vault_files")\
            .select("id, original_name, user_id")\
            .eq("id", document_id)\
            .eq("user_id", user_id)\
            .execute()
        
        if not doc_result.data:
            raise HTTPException(404, "Document not found or access denied")
        
        document = doc_result.data[0]
        
        # Load FAISS index and metadata
        index, metadata = load_index()
        
        if index.ntotal == 0:
            return {
                "document_id": document_id,
                "document_name": document["original_name"],
                "chunks": []
            }
        
        # Filter chunks by document_id (vault_id)
        document_chunks = []
        for chunk_meta in metadata:
            if chunk_meta.get("vault_id") == document_id and chunk_meta.get("user_id") == user_id:
                document_chunks.append({
                    "chunk_id": str(chunk_meta.get("chunk_index", 0)),
                    "content": chunk_meta.get("content", ""),
                    "chunk_index": chunk_meta.get("chunk_index", 0)
                })
        
        # Sort by chunk_index
        document_chunks.sort(key=lambda x: x["chunk_index"])
        
        logging.info(f"Retrieved {len(document_chunks)} chunks for document {document_id}")
        
        return {
            "document_id": document_id,
            "document_name": document["original_name"],
            "chunks": document_chunks
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error retrieving document chunks: {e}", exc_info=True)
        raise HTTPException(500, f"Failed to retrieve document chunks: {str(e)}")
