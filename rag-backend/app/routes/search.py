from fastapi import APIRouter
from app.database import supabase
from app.services.embedding_service import embedding_service

router = APIRouter(prefix="/api/search", tags=["search"])

@router.post("/semantic-search")
async def semantic_search(query: str, user_id: str, top_k: int = 5):
    emb = await embedding_service.embed_text(query)
    rpc = supabase.rpc("search_embeddings", {"query_embedding": emb, "user_id_input": user_id, "match_count": top_k}).execute()
    return {"results": rpc.data}
