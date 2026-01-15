# app/routes/vault.py

import os
import tempfile
import logging
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.database import supabase
from app.config import SUPABASE_BUCKET
from app.services.faiss_store import delete_chunks_by_vault
from app.services.text_extraction import extract_text_from_file

router = APIRouter(prefix="/api/vault", tags=["vault"])
logger = logging.getLogger(__name__)

@router.post("/upload")
async def upload_vault_file(user_id: str = Form(...), file: UploadFile = File(...), folder: Optional[str] = Form("")):
    ext = os.path.splitext(file.filename)[1].lower()
    allowed = [".txt", ".pdf", ".docx", ".md", ".html", ".json"]
    if ext not in allowed:
        raise HTTPException(400, "Unsupported file type")
    storage_path = f"{user_id}/{file.filename}" if not folder else f"{folder}/{file.filename}"
    content = await file.read()
    
    # Upload to storage
    try:
        supabase.storage.from_(SUPABASE_BUCKET).upload(path=storage_path, file=content)
        logger.info(f"Uploaded file to storage: {storage_path}")
    except Exception as e:
        logger.error(f"Storage upload failed: {e}", exc_info=True)
        raise HTTPException(500, f"Upload failed: {e}")
    
    # Try to extract text content immediately during upload
    # This ensures text_content is available even if embedding fails later
    text_content = None
    if ext in [".txt", ".pdf", ".docx", ".md", ".html"]:
        try:
            # Save to temp file for extraction
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                tmp.write(content)
                tmp_path = tmp.name
            
            try:
                extracted_text = extract_text_from_file(tmp_path)
                if extracted_text and len(extracted_text.strip()) > 0:
                    # Clean the text
                    text_content = extracted_text.replace("\x00", "").encode("utf-8", "ignore").decode("utf-8", "ignore").strip()
                    logger.info(f"Extracted {len(text_content)} characters from {file.filename}")
                else:
                    logger.warning(f"No text extracted from {file.filename}")
            finally:
                try:
                    os.remove(tmp_path)
                except:
                    pass
        except Exception as e:
            logger.warning(f"Text extraction failed during upload for {file.filename}: {e}")
            # Don't fail the upload if extraction fails - embedding can try again later
    
    # Prepare record with text_content if available
    rec = {
        "user_id": user_id,
        "storage_path": storage_path,
        "original_name": file.filename,
        "file_size": len(content),
        "content_type": file.content_type
    }
    
    # Add text_content if we extracted it
    if text_content:
        try:
            rec["text_content"] = text_content
        except Exception:
            # Column might not exist, that's okay
            pass
    
    # Insert into database
    try:
        inserted = supabase.table("vault_files").insert(rec).execute()
        if not inserted.data:
            raise HTTPException(500, "Failed to insert vault metadata")
        vault_id = inserted.data[0]["id"]
        logger.info(f"Created vault_file record: {vault_id} with text_content: {text_content is not None}")
        return {"success": True, "vault_id": vault_id, "storage_path": storage_path, "text_extracted": text_content is not None}
    except Exception as e:
        logger.error(f"Database insert failed: {e}", exc_info=True)
        # If insert fails but we have text_content, try without it
        if text_content:
            try:
                rec.pop("text_content", None)
                inserted = supabase.table("vault_files").insert(rec).execute()
                if inserted.data:
                    vault_id = inserted.data[0]["id"]
                    logger.warning(f"Inserted without text_content (column may not exist): {vault_id}")
                    return {"success": True, "vault_id": vault_id, "storage_path": storage_path, "text_extracted": False}
            except:
                pass
        raise HTTPException(500, f"Failed to insert vault metadata: {str(e)}")

@router.get("/list")
async def list_files():
    res = supabase.table("vault_files").select("*").execute()
    return {"files": res.data or []}

@router.delete("/delete/{vault_id}")
async def delete_vault_file(vault_id: str):
    """Delete a file from vault, including storage and embeddings."""
    try:
        # Get file info first
        file_rec = supabase.table("vault_files").select("*").eq("id", vault_id).execute()
        if not file_rec.data:
            raise HTTPException(404, "File not found")
        
        file_info = file_rec.data[0]
        storage_path = file_info.get("storage_path")
        
        # Delete from storage if path exists
        if storage_path:
            try:
                supabase.storage.from_(SUPABASE_BUCKET).remove([storage_path])
                logging.info(f"Deleted file from storage: {storage_path}")
            except Exception as e:
                logging.warning(f"Failed to delete from storage (may not exist): {e}")
        
        # Delete chunks from FAISS
        try:
            delete_chunks_by_vault(vault_id)
            logging.info(f"Deleted chunks from FAISS for vault_id: {vault_id}")
        except Exception as e:
            logging.warning(f"Failed to delete chunks from FAISS: {e}")
        
        # Delete from database
        supabase.table("vault_files").delete().eq("id", vault_id).execute()
        
        return {"success": True, "message": "File deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error deleting file {vault_id}: {e}")
        raise HTTPException(500, f"Failed to delete file: {str(e)}")
