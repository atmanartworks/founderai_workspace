# app/routes/vault.py

import os
import tempfile
import logging
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.database import supabase
from app.config import SUPABASE_BUCKET
from app.services.faiss_store import delete_chunks_by_vault

router = APIRouter(prefix="/api/vault", tags=["vault"])

@router.post("/upload")
async def upload_vault_file(user_id: str = Form(...), file: UploadFile = File(...), folder: Optional[str] = Form("")):
    ext = os.path.splitext(file.filename)[1].lower()
    allowed = [".txt", ".pdf", ".docx", ".md", ".html", ".json"]
    if ext not in allowed:
        raise HTTPException(400, "Unsupported file type")
    storage_path = f"{user_id}/{file.filename}" if not folder else f"{folder}/{file.filename}"
    content = await file.read()
    try:
        supabase.storage.from_(SUPABASE_BUCKET).upload(path=storage_path, file=content)
    except Exception as e:
        raise HTTPException(500, f"Upload failed: {e}")
    rec = {
        "user_id": user_id,
        "storage_path": storage_path,
        "original_name": file.filename,
        "file_size": len(content),
        "content_type": file.content_type
    }
    inserted = supabase.table("vault_files").insert(rec).execute()
    if not inserted.data:
        raise HTTPException(500, "Failed to insert vault metadata")
    vault_id = inserted.data[0]["id"]
    return {"success": True, "vault_id": vault_id, "storage_path": storage_path}

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
