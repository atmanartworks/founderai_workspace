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
    Works with FAISS chunks if available, otherwise splits text_content.
    """
    try:
        # Verify document exists and belongs to user
        doc_result = supabase.table("vault_files")\
            .select("id, original_name, user_id, text_content")\
            .eq("id", document_id)\
            .eq("user_id", user_id)\
            .execute()
        
        if not doc_result.data:
            raise HTTPException(404, "Document not found or access denied")
        
        document = doc_result.data[0]
        text_content = document.get("text_content", "")
        
        # Try to get chunks from FAISS first (if embedded)
        document_chunks = []
        faiss_chunks_found = False
        
        try:
            index, metadata = load_index()
            if index.ntotal > 0:
                # Filter chunks by document_id (vault_id)
                for chunk_meta in metadata:
                    if chunk_meta.get("vault_id") == document_id and chunk_meta.get("user_id") == user_id:
                        document_chunks.append({
                            "chunk_id": str(chunk_meta.get("chunk_index", 0)),
                            "content": chunk_meta.get("content", ""),
                            "chunk_index": chunk_meta.get("chunk_index", 0)
                        })
                        faiss_chunks_found = True
                
                # Sort by chunk_index
                document_chunks.sort(key=lambda x: x["chunk_index"])
                logging.info(f"Found {len(document_chunks)} chunks in FAISS for document {document_id}")
        except Exception as e:
            logging.warning(f"Could not load FAISS chunks: {e}")
        
        # If no chunks from FAISS but we have text_content, split it into chunks
        if len(document_chunks) == 0 and text_content and len(text_content.strip()) > 0:
            logging.info(f"No FAISS chunks found, splitting text_content into chunks for document {document_id}")
            # Split text_content into chunks (similar to embedding process)
            # Use ~500 character chunks with overlap
            chunk_size = 500
            overlap = 50
            text = text_content.strip()
            
            for i in range(0, len(text), chunk_size - overlap):
                chunk_text = text[i:i + chunk_size]
                if chunk_text.strip():
                    document_chunks.append({
                        "chunk_id": str(len(document_chunks)),
                        "content": chunk_text.strip(),
                        "chunk_index": len(document_chunks)
                    })
            
            logging.info(f"Created {len(document_chunks)} chunks from text_content")
        
        return {
            "document_id": document_id,
            "document_name": document["original_name"],
            "chunks": document_chunks,
            "has_text_content": bool(text_content and len(text_content.strip()) > 0),
            "chunks_from_faiss": faiss_chunks_found,
            "chunks_from_text": len(document_chunks) > 0 and not faiss_chunks_found
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error retrieving document chunks: {e}", exc_info=True)
        raise HTTPException(500, f"Failed to retrieve document chunks: {str(e)}")

@router.get("/{document_id}/status")
async def get_document_status(document_id: str, user_id: str):
    """
    Get document embedding status and chunk information.
    Useful for debugging why chunks might not be available.
    """
    try:
        # Verify document exists
        doc_result = supabase.table("vault_files")\
            .select("id, original_name, user_id, text_content, file_size, content_type")\
            .eq("id", document_id)\
            .eq("user_id", user_id)\
            .execute()
        
        if not doc_result.data:
            raise HTTPException(404, "Document not found or access denied")
        
        document = doc_result.data[0]
        text_content = document.get("text_content", "")
        
        # Check FAISS for chunks
        faiss_chunk_count = 0
        try:
            index, metadata = load_index()
            if index.ntotal > 0:
                for chunk_meta in metadata:
                    if chunk_meta.get("vault_id") == document_id and chunk_meta.get("user_id") == user_id:
                        faiss_chunk_count += 1
        except Exception as e:
            logging.warning(f"Error checking FAISS: {e}")
        
        return {
            "document_id": document_id,
            "document_name": document["original_name"],
            "has_text_content": bool(text_content and len(text_content.strip()) > 0),
            "text_content_length": len(text_content) if text_content else 0,
            "faiss_chunk_count": faiss_chunk_count,
            "is_embedded": faiss_chunk_count > 0,
            "file_size": document.get("file_size", 0),
            "content_type": document.get("content_type", ""),
            "recommendation": "embed" if faiss_chunk_count == 0 and text_content else "ready"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error checking document status: {e}", exc_info=True)
        raise HTTPException(500, f"Failed to check document status: {str(e)}")
