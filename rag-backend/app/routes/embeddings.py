# app/routes/embeddings.py

import os
import tempfile
import numpy as np
import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException
from app.database import supabase
from app.config import SUPABASE_BUCKET
from app.services.text_extraction import extract_text_from_file
from app.services.embedding_service import embedding_service
from app.services.chunk_service import ChunkingService
from app.services.faiss_store import add_chunks, delete_chunks_by_vault
from app.utils.fix_storage_paths import check_storage_paths
from app.utils.auto_reupload_missing import auto_reupload_missing

router = APIRouter(prefix="/api/embeddings", tags=["embeddings"])
logger = logging.getLogger(__name__)

def clean_text(text: str) -> str:
    if not text:
        return ""
    return text.replace("\x00", "").encode("utf-8", "ignore").decode("utf-8", "ignore").strip()

@router.post("/embed-document/{vault_id}")
async def embed_document(vault_id: str):
    """
    Embed a document: extract text, chunk it, generate embeddings, and store in FAISS.
    Also saves extracted text to text_content column for direct access.
    """
    try:
        rec = supabase.table("vault_files").select("*").eq("id", vault_id).execute()
        if not rec.data:
            logger.error(f"Vault file not found: {vault_id}")
            raise HTTPException(404, f"Vault file not found: {vault_id}")
        file_info = rec.data[0]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching vault file {vault_id}: {e}", exc_info=True)
        raise HTTPException(500, f"Failed to fetch vault file: {str(e)}")
    
    # Try to get text_content, but handle if column doesn't exist
    text_content = ""
    try:
        text_content = clean_text(file_info.get("text_content") or "")
    except Exception:
        # Column might not exist, that's okay - we'll extract it
        text_content = ""
    
    storage_path = file_info.get("storage_path")
    user_id = file_info.get("user_id")
    original_name = file_info.get("original_name", "Unknown")
    file_ext = os.path.splitext(original_name)[1].lower()

    logger.info(f"Processing vault_id: {vault_id}, file: {original_name}, extension: {file_ext}")
    logger.info(f"Storage path: {storage_path}, Text content length: {len(text_content)}")

    if len(text_content) < 20:
        if not storage_path:
            raise HTTPException(400, "No text_content or storage_path")
        try:
            logger.info(f"Attempting to download from bucket '{SUPABASE_BUCKET}' path '{storage_path}'")
            
            # Try to list files first to verify path exists
            try:
                path_parts = storage_path.rsplit('/', 1)
                if len(path_parts) == 2:
                    folder_path = path_parts[0]
                    list_result = supabase.storage.from_(SUPABASE_BUCKET).list(folder_path)
                    logger.debug(f"Files in folder '{folder_path}': {list_result}")
            except Exception as list_err:
                logger.warning(f"Could not list files: {list_err}")
            
            file_bytes = supabase.storage.from_(SUPABASE_BUCKET).download(storage_path)
            logger.info(f"Successfully downloaded {len(file_bytes)} bytes")
        except Exception as e:
            logger.error(f"Storage download error for {storage_path}: {type(e).__name__}: {str(e)}", exc_info=True)
            raise HTTPException(500, f"Storage download failed from bucket '{SUPABASE_BUCKET}' path '{storage_path}': {str(e)}")
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(storage_path)[1]) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name
        try:
            logger.info(f"Extracting text from {tmp_path}")
            extracted_text = extract_text_from_file(tmp_path)
            if not extracted_text or len(extracted_text.strip()) == 0:
                logger.warning(f"No text extracted from {original_name}")
            else:
                logger.info(f"Extracted {len(extracted_text)} characters from {original_name}")
            
            text_content = clean_text(extracted_text)
            
            # Save extracted text to text_content column for future use
            if text_content and len(text_content.strip()) > 0:
                try:
                    # Check if text_content column exists by trying to update it
                    update_result = supabase.table("vault_files").update({
                        "text_content": text_content
                    }).eq("id", vault_id).execute()
                    logger.info(f"Saved text_content ({len(text_content)} chars) to vault_files for {vault_id}")
                except Exception as e:
                    error_msg = str(e).lower()
                    if "column" in error_msg and "does not exist" in error_msg:
                        logger.warning(f"text_content column does not exist in vault_files table. Run migration to add it.")
                    else:
                        logger.warning(f"Could not save text_content to database: {e}")
        except Exception as e:
            logger.error(f"Text extraction failed for {original_name}: {e}", exc_info=True)
            raise HTTPException(500, f"Text extraction failed: {str(e)}")
        finally:
            try:
                os.remove(tmp_path)
            except Exception as e:
                logger.warning(f"Failed to remove temp file {tmp_path}: {e}")

    if not text_content or not text_content.strip():
        error_msg = f"No usable text found in '{original_name}'. "
        if file_ext == ".docx":
            error_msg += "The DOCX file may be empty, password-protected, or contain only images. Please ensure the file contains readable text."
        elif file_ext == ".pdf":
            error_msg += "The PDF may be scanned (image-only), password-protected, or corrupted. Please ensure it contains selectable text."
        else:
            error_msg += "The file may be empty, corrupted, or in an unsupported format."
        raise HTTPException(400, error_msg)

    try:
        logger.info(f"Chunking text for {original_name} ({len(text_content)} chars)")
        chunks = ChunkingService.chunk_text(text_content)
        if not chunks:
            logger.error(f"Chunking failed for {original_name}")
            raise HTTPException(400, "Chunking failed - no chunks created")
        logger.info(f"Created {len(chunks)} chunks")
        
        contents = [c["content"] for c in chunks]
        
        # Get embeddings as numpy array (already normalized)
        logger.info(f"Generating embeddings for {len(contents)} chunks")
        embeddings = await embedding_service.embed_batch(contents)
        if len(embeddings) != len(chunks):
            logger.error(f"Embedding mismatch: {len(embeddings)} embeddings for {len(chunks)} chunks")
            raise HTTPException(500, f"Embedding mismatch: {len(embeddings)} embeddings for {len(chunks)} chunks")
        
        # Convert to numpy array if not already
        if not isinstance(embeddings, np.ndarray):
            embeddings = np.array(embeddings, dtype=np.float32)
        
        # Clear old chunks for this vault from FAISS
        logger.info(f"Clearing old chunks for vault_id: {vault_id}")
        delete_chunks_by_vault(vault_id)
        
        # Prepare metadata for FAISS
        chunks_metadata = []
        for idx, c in enumerate(chunks):
            chunks_metadata.append({
                "vault_id": vault_id,
                "user_id": user_id,
                "chunk_index": idx,
                "content": c["content"],
                "tokens": c["tokens"],
            })
        
        # Add to FAISS index
        logger.info(f"Adding {len(chunks_metadata)} chunks to FAISS")
        try:
            add_chunks(embeddings, chunks_metadata)
            logger.info(f"Successfully embedded document {vault_id} with {len(chunks_metadata)} chunks")
        except Exception as e:
            logger.error(f"Failed adding chunks to FAISS: {e}", exc_info=True)
            raise HTTPException(500, f"Failed adding chunks to FAISS: {str(e)}")

        return {"success": True, "chunks": len(chunks_metadata), "vault_id": vault_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error embedding document {vault_id}: {e}", exc_info=True)
        raise HTTPException(500, f"Failed to embed document: {str(e)}")


@router.get("/fix-storage-paths")
def fix_paths():
    return check_storage_paths()


@router.post("/auto-reupload-missing")
def auto_reupload():
    return auto_reupload_missing()
