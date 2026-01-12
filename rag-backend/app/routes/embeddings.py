# app/routes/embeddings.py

import os
import tempfile
import numpy as np
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

def clean_text(text: str) -> str:
    if not text:
        return ""
    return text.replace("\x00", "").encode("utf-8", "ignore").decode("utf-8", "ignore").strip()

@router.post("/embed-document/{vault_id}")
async def embed_document(vault_id: str):
    rec = supabase.table("vault_files").select("*").eq("id", vault_id).execute()
    if not rec.data:
        raise HTTPException(404, "Vault file not found")
    file_info = rec.data[0]
    text_content = clean_text(file_info.get("text_content") or "")
    storage_path = file_info.get("storage_path")
    user_id = file_info.get("user_id")

    print(f"Processing vault_id: {vault_id}")
    print(f"File info: {file_info}")
    print(f"Storage path: {storage_path}")
    print(f"Bucket: {SUPABASE_BUCKET}")
    print(f"Text content length: {len(text_content)}")

    if len(text_content) < 20:
        if not storage_path:
            raise HTTPException(400, "No text_content or storage_path")
        try:
            print(f"Attempting to download from bucket '{SUPABASE_BUCKET}' path '{storage_path}'")
            
            # Try to list files first to verify path exists
            try:
                path_parts = storage_path.rsplit('/', 1)
                if len(path_parts) == 2:
                    folder_path = path_parts[0]
                    list_result = supabase.storage.from_(SUPABASE_BUCKET).list(folder_path)
                    print(f"Files in folder '{folder_path}': {list_result}")
            except Exception as list_err:
                print(f"Could not list files: {list_err}")
            
            file_bytes = supabase.storage.from_(SUPABASE_BUCKET).download(storage_path)
            print(f"Successfully downloaded {len(file_bytes)} bytes")
        except Exception as e:
            print(f"Storage download error: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            raise HTTPException(500, f"Storage download failed from bucket '{SUPABASE_BUCKET}' path '{storage_path}': {str(e)}")
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(storage_path)[1]) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name
        try:
            text_content = clean_text(extract_text_from_file(tmp_path))
        finally:
            try:
                os.remove(tmp_path)
            except:
                pass

    if not text_content.strip():
        raise HTTPException(400, "No usable text found")

    chunks = ChunkingService.chunk_text(text_content)
    if not chunks:
        raise HTTPException(400, "Chunking failed")
    contents = [c["content"] for c in chunks]
    
    # Get embeddings as numpy array (already normalized)
    embeddings = await embedding_service.embed_batch(contents)
    if len(embeddings) != len(chunks):
        raise HTTPException(500, "Embedding mismatch")
    
    # Convert to numpy array if not already
    if not isinstance(embeddings, np.ndarray):
        embeddings = np.array(embeddings, dtype=np.float32)
    
    # Clear old chunks for this vault from FAISS
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
    try:
        add_chunks(embeddings, chunks_metadata)
    except Exception as e:
        raise HTTPException(500, f"Failed adding chunks to FAISS: {e}")

    return {"success": True, "chunks": len(chunks_metadata), "vault_id": vault_id}


@router.get("/fix-storage-paths")
def fix_paths():
    return check_storage_paths()


@router.post("/auto-reupload-missing")
def auto_reupload():
    return auto_reupload_missing()
