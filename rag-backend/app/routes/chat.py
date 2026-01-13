# app/routes/chat.py

import uuid
import logging
import random
import numpy as np
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from app.database import supabase
from app.services.embedding_service import embedding_service
from app.services.constraint_extractor import extract_constraints
from app.services.question_rewrite import rewrite_question
from app.services.answer_enforcer import enforce_constraints
from app.services.query_classifier import classify_query
from app.services.faiss_store import search as faiss_search

router = APIRouter(prefix="/api/chat", tags=["chat"])

class ChatRequest(BaseModel):
    conversation_id: str = None
    message: str
    user_id: str
    top_k: int = 5
    vault_id: str = None  # Optional: specify which document to query

class ChatResponse(BaseModel):
    response: str
    sources: List[str]
    message_id: str
    conversation_id: str

@router.post("/message", response_model=ChatResponse)
async def send_message(payload: ChatRequest):
    try:
        try:
            conversation_id = str(uuid.UUID(payload.conversation_id)) if payload.conversation_id else str(uuid.uuid4())
        except Exception:
            conversation_id = str(uuid.uuid4())

        # Validate user_id
        if not payload.user_id:
            raise HTTPException(400, "user_id is required")
        
        # ensure conversation exists
        try:
            existing = supabase.table("conversations").select("id").eq("id", conversation_id).execute()
            if not existing.data:
                supabase.table("conversations").insert({
                    "id": conversation_id,
                    "user_id": payload.user_id,
                    "created_at": datetime.utcnow().isoformat()
                }).execute()
        except Exception as e:
            logging.error(f"Error ensuring conversation exists: {e}", exc_info=True)
            raise HTTPException(500, f"Database error: {str(e)}")

        # 1. Classify query to determine if RAG is needed
        query_classification = classify_query(payload.message)
        logging.info(f"Query classification: {query_classification} for message: '{payload.message}'")
        
        # Handle simple greetings and conversational queries without RAG
        if query_classification["is_greeting"]:
            greeting_responses = [
                "Hello! How can I help you today?",
                "Hi there! What would you like to know?",
                "Hello! I'm here to help. What can I assist you with?",
            ]
            response_text = random.choice(greeting_responses)
            
            msg = supabase.table("messages").insert({
                "conversation_id": conversation_id,
                "user_message": payload.message,
                "assistant_message": response_text,
                "used_documents": {"chunks": [], "files": []},
                "created_at": datetime.utcnow().isoformat()
            }).execute()
            mid = msg.data[0]["id"] if msg.data else "unknown"
            return ChatResponse(
                response=response_text,
                sources=[],
                message_id=mid,
                conversation_id=conversation_id
            )
        
        if query_classification["is_conversational"] and not query_classification["is_question"]:
            response_text = "Got it! How can I help you?"
            
            msg = supabase.table("messages").insert({
                "conversation_id": conversation_id,
                "user_message": payload.message,
                "assistant_message": response_text,
                "used_documents": {"chunks": [], "files": []},
                "created_at": datetime.utcnow().isoformat()
            }).execute()
            mid = msg.data[0]["id"] if msg.data else "unknown"
            return ChatResponse(
                response=response_text,
                sources=[],
                message_id=mid,
                conversation_id=conversation_id
            )
        
        # Handle file list queries - return user's vault files with embedding status
        if query_classification["is_file_list_query"]:
            try:
                # Get user's vault files
                files_res = supabase.table("vault_files")\
                    .select("id, original_name, file_size, content_type, created_at")\
                    .eq("user_id", payload.user_id)\
                    .order("created_at")\
                    .execute()
                
                # Reverse to get newest first
                if files_res.data:
                    files_res.data.reverse()
                
                files = files_res.data or []
                
                if not files:
                    response_text = "You don't have any files in your vault yet. Upload some files to get started."
                else:
                    # Check embedding status for each file
                    embedded_count = 0
                    total_chunks = 0
                    file_details = []
                    
                    for f in files:
                        file_name = f.get("original_name", "Unknown")
                        file_size = f.get("file_size", 0)
                        vault_id = f.get("id")
                        
                        # Format file size
                        if file_size < 1024:
                            size_str = f"{file_size} B"
                        elif file_size < 1024 * 1024:
                            size_str = f"{file_size / 1024:.1f} KB"
                        else:
                            size_str = f"{file_size / (1024 * 1024):.1f} MB"
                        
                        # Check if file is embedded (has chunks in FAISS)
                        chunk_count = 0
                        try:
                            from app.services.faiss_store import load_index
                            _, metadata = load_index()
                            chunk_count = sum(1 for m in metadata if m.get("vault_id") == vault_id)
                            
                            if chunk_count > 0:
                                embedded_count += 1
                                total_chunks += chunk_count
                        except Exception as e:
                            logging.warning(f"Error checking chunks for {vault_id}: {e}")
                        
                        # Get file type
                        file_ext = file_name.split('.')[-1].upper() if '.' in file_name else "UNKNOWN"
                        
                        # Store file details
                        file_details.append({
                            "name": file_name,
                            "size": size_str,
                            "type": file_ext,
                            "chunks": chunk_count,
                            "embedded": chunk_count > 0
                        })
                    
                    # Build clean text response (no markdown, no bullet points)
                    response_text = f"I have access to {len(files)} file(s) in your vault.\n\n"
                    
                    # Add each file with clean paragraph format
                    for file_info in file_details:
                        response_text += f"{file_info['name']} ({file_info['size']}, {file_info['type']})\n"
                        if file_info['embedded']:
                            response_text += f"This file is embedded in the vector database with {file_info['chunks']} chunks. The file is ready for querying.\n\n"
                        else:
                            response_text += f"This file is not yet embedded. Embed this file to enable question-answering based on its content.\n\n"
                    
                    # Add summary
                    response_text += f"\nSummary: {embedded_count} file(s) are embedded in the vector database with a total of {total_chunks} chunks. {len(files) - embedded_count} file(s) need embedding before they can be searched and queried. Only embedded files can be used to answer questions."
                
                msg = supabase.table("messages").insert({
                    "conversation_id": conversation_id,
                    "user_message": payload.message,
                    "assistant_message": response_text,
                    "used_documents": {"chunks": [], "files": [f.get("original_name") for f in files]},
                    "created_at": datetime.utcnow().isoformat()
                }).execute()
                mid = msg.data[0]["id"] if msg.data else "unknown"
                return ChatResponse(
                    response=response_text,
                    sources=[f.get("original_name") for f in files],
                    message_id=mid,
                    conversation_id=conversation_id
                )
            except Exception as e:
                logging.error(f"Error fetching vault files: {e}")
                response_text = "I encountered an error while fetching your files. Please try again."
                
                msg = supabase.table("messages").insert({
                    "conversation_id": conversation_id,
                    "user_message": payload.message,
                    "assistant_message": response_text,
                    "used_documents": {"chunks": [], "files": []},
                    "created_at": datetime.utcnow().isoformat()
                }).execute()
                mid = msg.data[0]["id"] if msg.data else "unknown"
                return ChatResponse(
                    response=response_text,
                    sources=[],
                    message_id=mid,
                    conversation_id=conversation_id
                )
        
        # 1. Extract constraints from user input
        constraints = extract_constraints(payload.message)
        logging.info(f"Extracted constraints: {constraints} from message: '{payload.message}'")
        
        # 2. Detect vague queries and infer document context
        message_lower = payload.message.lower()
        is_vague_query = any(phrase in message_lower for phrase in [
            "this document", "this file", "this doc", "the document", "the file",
            "explain this", "what is this", "tell me about this"
        ])
        
        target_vault_id = payload.vault_id
        
        # If vague query and no vault_id provided, try to infer from conversation history or recent uploads
        if is_vague_query and not target_vault_id:
            try:
                # Strategy 1: Check conversation history for most recently used document
                recent_messages = supabase.table("messages")\
                    .select("used_documents, created_at")\
                    .eq("conversation_id", conversation_id)\
                    .order("created_at")\
                    .limit(10)\
                    .execute()
                
                # Reverse to get newest first
                if recent_messages.data:
                    recent_messages.data.reverse()
                
                # Find the most recently used document
                for msg in recent_messages.data or []:
                    used_docs = msg.get("used_documents")
                    if not used_docs or not isinstance(used_docs, dict):
                        continue
                    files = used_docs.get("files", [])
                    if files:
                        # Get vault_id from the most recent file
                        file_name = files[0]
                        file_rec = supabase.table("vault_files")\
                            .select("id")\
                            .eq("original_name", file_name)\
                            .eq("user_id", payload.user_id)\
                            .limit(1)\
                            .execute()
                        if file_rec.data:
                            target_vault_id = file_rec.data[0]["id"]
                            logging.info(f"Inferred vault_id: {target_vault_id} from conversation history")
                            break
                
                # Strategy 2: If no conversation history, use most recently uploaded file (within last hour)
                if not target_vault_id:
                    one_hour_ago = (datetime.utcnow() - timedelta(hours=1)).isoformat()
                    recent_files = supabase.table("vault_files")\
                        .select("id, original_name, created_at")\
                        .eq("user_id", payload.user_id)\
                        .gte("created_at", one_hour_ago)\
                        .order("created_at")\
                        .limit(1)\
                        .execute()
                    
                    if recent_files.data:
                        target_vault_id = recent_files.data[0]["id"]
                        logging.info(f"Inferred vault_id: {target_vault_id} from recent uploads")
            except Exception as e:
                logging.warning(f"Failed to infer vault_id from conversation: {e}")
        
        # 2. Rewrite question for clarity (preserves constraints)
        # Don't rewrite if it's a vague "this document" query - keep original intent
        if is_vague_query and target_vault_id:
            rewritten_question = payload.message  # Keep original for better document-specific search
        else:
            rewritten_question = await rewrite_question(payload.message)
        logging.info(f"Rewritten question: '{rewritten_question}' (vague={is_vague_query}, vault_id={target_vault_id})")
        
        # 3. Embed the rewritten query for better semantic search
        try:
            query_embedding_list = await embedding_service.embed_text(rewritten_question)
            if not query_embedding_list or len(query_embedding_list) == 0:
                raise HTTPException(500, "Failed to generate query embedding: Empty embedding returned")
            
            # Convert to numpy array for FAISS (normalize for cosine similarity)
            query_embedding = np.array([query_embedding_list], dtype=np.float32)
            
            # Validate embedding dimension
            if query_embedding.shape[1] not in [768, 1536]:
                logging.warning(f"Unexpected embedding dimension: {query_embedding.shape[1]}, expected 768 or 1536")
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"Error generating query embedding: {e}")
            raise HTTPException(500, f"Failed to generate query embedding: {str(e)}")

        # Only perform RAG retrieval if needed
        chunks = []
        if query_classification["needs_rag"]:
            # For "overview of documents" queries, retrieve from ALL files
            is_overview_query = any(phrase in message_lower for phrase in [
                "overview of documents", "overview of files", "summary of documents", "summary of files",
                "documents available", "files available", "all documents", "all files"
            ])
            
            # If asking for overview/summary of all documents, get chunks from all files
            if is_overview_query and not target_vault_id:
                # Get all user's files first
                try:
                    all_files = supabase.table("vault_files")\
                        .select("id")\
                        .eq("user_id", payload.user_id)\
                        .eq("is_folder", False)\
                        .execute()
                    
                    if all_files.data:
                        # Retrieve chunks from each file - ensure we get representative chunks from ALL files
                        all_chunks = []
                        chunks_per_file = max(3, (payload.top_k * 2) // len(all_files.data))  # Get more chunks per file for overview
                        
                        for file_info in all_files.data:
                            file_chunks = faiss_search(
                                query_embedding=query_embedding,
                                user_id=payload.user_id,
                                top_k=chunks_per_file,
                                vault_id=file_info["id"]
                            )
                            # Add chunks with file identifier to ensure representation
                            for chunk in file_chunks:
                                chunk["_file_id"] = file_info["id"]  # Mark which file it's from
                            all_chunks.extend(file_chunks)
                        
                        # For overview queries, ensure we have chunks from ALL files
                        # Group by file and ensure at least 2 chunks per file
                        chunks_by_file = {}
                        for chunk in all_chunks:
                            file_id = chunk.get("_file_id")
                            if file_id not in chunks_by_file:
                                chunks_by_file[file_id] = []
                            chunks_by_file[file_id].append(chunk)
                        
                        # Take top chunks from each file to ensure all files are represented
                        chunks = []
                        for file_id, file_chunks in chunks_by_file.items():
                            # Sort by score within each file and take top chunks
                            file_chunks.sort(key=lambda x: x.get("score", 0), reverse=True)
                            chunks.extend(file_chunks[:chunks_per_file])
                        
                        logging.info(f"Overview query: Retrieved {len(chunks)} chunks from {len(chunks_by_file)} files (ensuring representation from all files)")
                    else:
                        # No files, use regular search
                        chunks = faiss_search(
                            query_embedding=query_embedding,
                            user_id=payload.user_id,
                            top_k=payload.top_k,
                            vault_id=target_vault_id
                        )
                except Exception as e:
                    logging.warning(f"Error retrieving chunks from all files: {e}, falling back to regular search")
                    chunks = faiss_search(
                        query_embedding=query_embedding,
                        user_id=payload.user_id,
                        top_k=payload.top_k,
                        vault_id=target_vault_id
                    )
            else:
                # Regular search - already filters by user_id and optionally vault_id
                try:
                    logging.info(f"Searching FAISS index for user_id: {payload.user_id}, top_k: {payload.top_k}, vault_id: {target_vault_id}")
                    
                    chunks = faiss_search(
                        query_embedding=query_embedding,
                        user_id=payload.user_id,
                        top_k=payload.top_k * 2 if target_vault_id else payload.top_k,  # Get more if filtering by vault
                        vault_id=target_vault_id
                    )
                    
                    logging.info(f"FAISS search returned {len(chunks)} chunks")
                    
                    # Log which files were found
                    if chunks:
                        found_files = set()
                        for chunk in chunks:
                            v_id = chunk.get("vault_id")
                            if v_id:
                                try:
                                    file_rec = supabase.table("vault_files").select("original_name").eq("id", v_id).limit(1).execute()
                                    if file_rec.data:
                                        found_files.add(file_rec.data[0]["original_name"])
                                except:
                                    pass
                        logging.info(f"Found chunks from files: {list(found_files)}")
                    else:
                        logging.warning("No chunks found in FAISS index - file may not be embedded")
                        
                except Exception as e:
                    logging.error(f"FAISS search failed: {e}")
                    raise HTTPException(500, f"FAISS search failed: {e}")
        else:
            logging.info("Skipping RAG retrieval for non-question query")
        
        # NOTE: We no longer return early if no chunks found
        # The LLM can answer using general knowledge even without document context

        context_pieces = []
        used_files = []
        used_chunk_ids = []
        vault_id_to_filename = {}  # Cache filenames
        
        for c in chunks:
            v_id = c.get("vault_id", "Unknown")
            chunk_content = c.get("content", "").strip()
            
            # Skip empty or minimal chunks
            if not chunk_content or len(chunk_content) < 10:
                continue
            
            used_chunk_ids.append(c.get("id"))
            
            # Get filename from vault_files table
            if v_id not in vault_id_to_filename:
                try:
                    file_rec = supabase.table("vault_files").select("original_name").eq("id", v_id).execute()
                    if file_rec.data:
                        vault_id_to_filename[v_id] = file_rec.data[0]["original_name"]
                    else:
                        vault_id_to_filename[v_id] = f"File {v_id}"
                except:
                    vault_id_to_filename[v_id] = f"File {v_id}"
            
            filename = vault_id_to_filename[v_id]
            used_files.append(filename)
            snippet = chunk_content[:1000]
            context_pieces.append(f"[{filename}] (chunk {c.get('chunk_index', 0)}):\n{snippet}")

        # Build context - if no chunks found, context will be empty and LLM will use general knowledge
        context = "\n\n---\n\n".join(context_pieces) if context_pieces else "No relevant documents found in vault."
        
        # Fetch conversation history for context
        conversation_history = ""
        try:
            prev_messages = supabase.table("messages")\
                .select("user_message, assistant_message")\
                .eq("conversation_id", conversation_id)\
                .order("created_at", desc=False)\
                .limit(5)\
                .execute()
            
            if prev_messages.data:
                history_parts = []
                for msg in prev_messages.data:
                    user_msg = msg.get("user_message", "")
                    assistant_msg = msg.get("assistant_message", "")
                    if user_msg and assistant_msg:
                        history_parts.append(f"User: {user_msg}\nAssistant: {assistant_msg}")
                if history_parts:
                    conversation_history = "\n\n".join(history_parts)
                    logging.info(f"Retrieved {len(history_parts)} previous messages from conversation history")
        except Exception as e:
            logging.warning(f"Error fetching conversation history: {e}")
        
        # Add conversation history to context if available
        if conversation_history:
            context = f"CONVERSATION HISTORY:\n{conversation_history}\n\n---\n\nDOCUMENT CONTEXT:\n{context}"
        
        # 4. Generate answer with strict constraints and context
        # For overview queries, add special instruction to cover all documents
        is_overview_query = any(phrase in message_lower for phrase in [
            "overview of documents", "overview of files", "summary of documents", "summary of files",
            "documents available", "files available", "all documents", "all files"
        ])
        
        if is_overview_query and not target_vault_id:
            # Add instruction to the question to ensure all documents are covered
            rewritten_question = f"{rewritten_question}\n\nIMPORTANT: Provide information about ALL documents/files mentioned in the context. Do not focus on just one document. Give a comprehensive overview covering each document separately."
        
        assistant_text = await embedding_service.generate(
            prompt="",  # Not used when context/question provided
            lines=constraints["lines"],
            short=constraints["short"],
            steps=constraints["steps"],
            context=context,
            question=rewritten_question
        )
        if not assistant_text:
            raise HTTPException(500, "AI generation failed")
        
        # 5. Enforce constraints as fail-safe (post-processing)
        assistant_text = enforce_constraints(
            assistant_text,
            lines=constraints["lines"],
            short=constraints["short"],
            steps=constraints["steps"]
        )

        used_documents = {"chunks": used_chunk_ids, "files": list(dict.fromkeys(used_files))}

        try:
            saved = supabase.table("messages").insert({
                "conversation_id": conversation_id,
                "user_message": payload.message,
                "assistant_message": assistant_text,
                "used_documents": used_documents,
                "created_at": datetime.utcnow().isoformat()
            }).execute()
            message_id = saved.data[0]["id"] if saved.data else "unknown"
        except Exception:
            message_id = "unknown"

        return ChatResponse(response=assistant_text, sources=used_documents["files"], message_id=message_id, conversation_id=conversation_id)

    except Exception as e:
        raise HTTPException(500, str(e))
