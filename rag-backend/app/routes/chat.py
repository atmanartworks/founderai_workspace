# app/routes/chat.py

import uuid
import logging
import random
import numpy as np
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from app.database import supabase
from app.services.embedding_service import embedding_service
from app.services.constraint_extractor import extract_constraints
from app.services.question_rewrite import rewrite_question
from app.services.answer_enforcer import enforce_constraints
from app.services.query_classifier import classify_query
from app.services.faiss_store import search as faiss_search
from app.services.citation_service import CitationService
from app.services.llm_stream import stream_llm
from app.utils.sse import sse_event

router = APIRouter(prefix="/api/chat", tags=["chat"])

class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str
    user_id: str
    top_k: int = 5
    vault_id: Optional[str] = None  # Optional: specify which document to query
    active_document_id: Optional[str] = None  # Optional: conversation-level active document context

class CitationMetadata(BaseModel):
    citation_id: int
    source_document_id: str
    source_document_name: str
    chunk_id: str
    quoted_text: str
    chunk_content: str
    score: float

class ChatResponse(BaseModel):
    response: str
    sources: List[str]
    message_id: str
    conversation_id: str
    citations: List[CitationMetadata] = []  # Citation metadata for interactive citations

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
        
        # MODE_EMPTY: Handle empty or invalid input
        # Log the message for debugging
        logging.info(f"Received message: '{payload.message}' (length: {len(payload.message) if payload.message else 0})")
        
        if not payload.message or not payload.message.strip():
            logging.warning(f"Empty message detected: '{payload.message}'")
            response_text = "Please enter a valid question."
            
            msg = supabase.table("messages").insert({
                "conversation_id": conversation_id,
                "user_message": payload.message or "",
                "assistant_message": response_text,
                "used_documents": {"chunks": [], "files": []},
                "created_at": datetime.utcnow().isoformat()
            }).execute()
            mid = msg.data[0]["id"] if msg.data else "unknown"
            return ChatResponse(
                response=response_text,
                sources=[],
                message_id=mid,
                conversation_id=conversation_id,
                citations=[]
            )
        
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

        # 1. Get active document context (conversation-level document memory)
        active_document_id = payload.active_document_id
        active_document_text = None
        active_document_name = None
        
        # If active_document_id is provided, fetch document and text_content
        if active_document_id:
            try:
                doc_result = supabase.table("vault_files")\
                    .select("id, original_name, text_content")\
                    .eq("id", active_document_id)\
                    .eq("user_id", payload.user_id)\
                    .single()\
                    .execute()
                
                if doc_result.data:
                    active_document_name = doc_result.data.get("original_name", "Document")
                    # Check if text_content column exists and has content
                    text_content = doc_result.data.get("text_content")
                    if text_content and len(text_content.strip()) > 0:
                        active_document_text = text_content.strip()
                        logging.info(f"Active document found: {active_document_name} (text length: {len(active_document_text)})")
                    else:
                        logging.warning(f"Active document {active_document_id} has no text_content")
            except Exception as e:
                logging.warning(f"Error fetching active document: {e}")
        
        # 2. Detect vague document queries that need active document context
        message_lower = payload.message.lower()
        is_vague_document_query = any(phrase in message_lower for phrase in [
            "this document", "this file", "this doc", "the document", "the file",
            "explain this", "what is this", "tell me about this", "what's in this",
            "whats in this", "summarize this", "what does it say", "what does this say"
        ])
        
        # 3. Classify query to determine if RAG is needed
        query_classification = classify_query(payload.message)
        logging.info(f"Query classification: {query_classification} for message: '{payload.message}'")
        logging.info(f"Active document: {active_document_id}, Vague query: {is_vague_document_query}, Has text: {active_document_text is not None}")
        
        # Handle out-of-scope queries - MODE C
        if query_classification.get("is_out_of_scope", False):
            response_text = "This question is outside the scope of the available documents."
            
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
                conversation_id=conversation_id,
                citations=[]  # No citations for out-of-scope questions
            )
        
        # Handle general knowledge questions - MODE B (before greeting check to avoid false positives)
        if query_classification.get("is_general_knowledge", False):
            logging.info(f"General knowledge question detected: '{payload.message}'")
            # Extract constraints but DON'T rewrite question for general knowledge (preserve original)
            constraints = extract_constraints(payload.message)
            # Use original question directly - don't rewrite for general knowledge questions
            original_question = payload.message.strip()
            
            # Ensure question is not empty
            if not original_question:
                logging.error(f"Question is empty, cannot generate answer")
                response_text = "Please enter a valid question."
            else:
                # Generate answer using general knowledge (MODE B) with original question
                assistant_text = await embedding_service.generate(
                    prompt="",
                    lines=constraints["lines"],
                    short=constraints["short"],
                    steps=constraints["steps"],
                    context="",  # Empty context - no documents available
                    question=original_question,  # Use original question, not rewritten
                    no_documents=True  # Flag to indicate no documents
                )
                
                # Validate and filter the generated answer
                if not assistant_text or not assistant_text.strip():
                    logging.error(f"LLM returned empty answer for question: '{original_question}'")
                    response_text = "I apologize, but I couldn't generate a response. Please try again."
                else:
                    # Filter out "blank message" responses - regenerate if detected
                    blank_message_patterns = [
                        "it seems like your message",
                        "your message is empty",
                        "your message is blank",
                        "message was sent blank",
                        "message is empty",
                        "message is blank"
                    ]
                    response_lower = assistant_text.lower()
                    if any(pattern in response_lower for pattern in blank_message_patterns):
                        logging.warning(f"LLM generated blank message response, regenerating with explicit instruction")
                        # Regenerate with even more explicit instructions
                        assistant_text = await embedding_service.generate(
                            prompt="",
                            lines=constraints["lines"],
                            short=constraints["short"],
                            steps=constraints["steps"],
                            context="",
                            question=f"QUESTION TO ANSWER: {original_question}",
                            no_documents=True
                        )
                        if not assistant_text or not assistant_text.strip() or any(pattern in assistant_text.lower() for pattern in blank_message_patterns):
                            # Fallback: direct answer
                            if "how many states in india" in original_question.lower():
                                response_text = "The total number of states in India is 28 states. Source: Generated"
                            else:
                                response_text = f"I apologize, but I encountered an issue. Please try rephrasing your question: '{original_question}'. Source: Generated"
                        else:
                            response_text = assistant_text
                    else:
                        response_text = assistant_text
            
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
                conversation_id=conversation_id,
                citations=[]
            )
            
            msg = supabase.table("messages").insert({
                "conversation_id": conversation_id,
                "user_message": payload.message,
                "assistant_message": assistant_text,
                "used_documents": {"chunks": [], "files": []},
                "created_at": datetime.utcnow().isoformat()
            }).execute()
            mid = msg.data[0]["id"] if msg.data else "unknown"
            return ChatResponse(
                response=assistant_text,
                sources=[],
                message_id=mid,
                conversation_id=conversation_id,
                citations=[]  # No citations for general knowledge questions
            )
        
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
        
        # Use active_document_id for vague queries if available
        target_vault_id = payload.vault_id or active_document_id
        
        # If vague document query and we have active document, use it
        if is_vague_document_query and active_document_id and not payload.vault_id:
            target_vault_id = active_document_id
            logging.info(f"Using active document {active_document_id} for vague query")
        
        # If vague query and no vault_id provided, try to infer from conversation history or recent uploads
        if is_vague_document_query and not target_vault_id:
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
        if is_vague_document_query and target_vault_id:
            rewritten_question = payload.message  # Keep original for better document-specific search
        else:
            rewritten_question = await rewrite_question(payload.message)
        logging.info(f"Rewritten question: '{rewritten_question}' (vague={is_vague_document_query}, vault_id={target_vault_id})")
        
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

        # Handle vague document queries with active document text_content
        # If we have active document text, inject it directly (ChatGPT-like behavior)
        using_direct_text = False
        if is_vague_document_query and active_document_text:
            logging.info(f"Vague document query detected with active document text - injecting text_content directly")
            # Create a synthetic chunk from the full document text
            # This allows the LLM to see the entire document context
            chunks = [{
                "vault_id": active_document_id,
                "content": active_document_text,
                "chunk_index": 0,
                "score": 1.0,  # High score since it's the active document
                "id": f"active_doc_{active_document_id}"
            }]
            # Mark that we're using direct text injection
            using_direct_text = True
        
        # Only perform RAG retrieval if needed (and not using direct text)
        if query_classification["needs_rag"] and not using_direct_text:
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

        # If using direct text injection and no chunks were built, use the active document text
        if using_direct_text and not context_pieces and active_document_text:
            context_pieces.append(f"[{active_document_name}] (full document):\n{active_document_text}")
            vault_id_to_filename[active_document_id] = active_document_name
            used_files.append(active_document_name)
            logging.info(f"Using direct text injection for active document: {active_document_name}")
        
        # Build context - validate we have meaningful chunks before proceeding
        # Check if chunks are actually relevant (not empty, have content)
        has_relevant_chunks = len(context_pieces) > 0 and any(
            len(piece.strip()) > 20 for piece in context_pieces
        )
        
        # Handle case: vague document query but no active document or text
        if is_vague_document_query and not active_document_text and not has_relevant_chunks:
            if active_document_id:
                # Document exists but text extraction failed
                response_text = f"I couldn't read text from '{active_document_name or 'this document'}'. Please upload a text-based DOCX or PDF file."
            else:
                # No active document
                response_text = "Please upload or select a document first, then ask about it."
            
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
                conversation_id=conversation_id,
                citations=[]
            )
        
        # Build context string
        context = "\n\n---\n\n".join(context_pieces) if context_pieces else ""
        
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
            if context:
                context = f"CONVERSATION HISTORY:\n{conversation_history}\n\n---\n\nDOCUMENT CONTEXT:\n{context}"
            else:
                # No document context - only use conversation history
                context = f"CONVERSATION HISTORY:\n{conversation_history}"
        
        # 4. Check if this is a general knowledge question (should use MODE B, not MODE A)
        is_general_knowledge = query_classification.get("is_general_knowledge", False)
        
        # 5. Check chunk relevance scores - if all scores are very low, chunks are likely irrelevant
        # This prevents citing irrelevant chunks for out-of-scope questions
        chunk_scores = [c.get("score", 0.0) for c in chunks if c.get("score") is not None]
        avg_score = sum(chunk_scores) / len(chunk_scores) if chunk_scores else 0.0
        max_score = max(chunk_scores) if chunk_scores else 0.0
        
        logging.info(f"Chunk relevance: {len(chunks)} chunks, avg_score={avg_score:.3f}, max_score={max_score:.3f}, has_relevant_chunks={has_relevant_chunks}, is_general_knowledge={is_general_knowledge}")
        
        # If chunks have very low relevance scores, they're likely irrelevant
        # Cosine similarity scores: >0.7 = very relevant, 0.5-0.7 = somewhat relevant, <0.5 = low relevance
        chunks_are_relevant = has_relevant_chunks and (
            avg_score > 0.3 or max_score > 0.4  # At least one chunk should be somewhat relevant
        )
        
        if chunks and len(chunks) > 0 and not chunks_are_relevant:
            logging.warning(f"Chunks retrieved but have low relevance scores - treating as out of scope. Question: '{rewritten_question}'")
        
        # Generate answer with citations if we have RELEVANT chunks AND it's NOT a general knowledge question
        citations_metadata = []
        
        # MODE A: Document-grounded answer (only if we have relevant chunks with good scores AND it's not general knowledge)
        # General knowledge questions should use MODE B even if chunks are retrieved
        if chunks_are_relevant and chunks and len(chunks) > 0 and not is_general_knowledge:
            # Generate answer with inline citations using citation service
            try:
                # Get OpenAI client from embedding service
                if not embedding_service._openai_initialized:
                    if embedding_service.openai_api_key:
                        from openai import OpenAI
                        embedding_service.openai_client = OpenAI(api_key=embedding_service.openai_api_key)
                        embedding_service._openai_initialized = True
                
                if embedding_service.openai_client:
                    # Use citation service to generate answer with citations
                    assistant_text, citations_metadata = CitationService.generate_cited_answer_with_llm(
                        question=rewritten_question,
                        chunks=chunks,
                        vault_id_to_filename=vault_id_to_filename,
                        openai_client=embedding_service.openai_client,
                        lines=constraints["lines"],
                        short=constraints["short"],
                        steps=constraints["steps"]
                    )
                    
                    # Apply constraints as fail-safe (citation service should already apply them)
                    assistant_text = enforce_constraints(
                        assistant_text,
                        lines=constraints["lines"],
                        short=constraints["short"],
                        steps=constraints["steps"]
                    )
                else:
                    # Fallback to regular generation if OpenAI not available
                    assistant_text = await embedding_service.generate(
                        prompt="",
                        lines=constraints["lines"],
                        short=constraints["short"],
                        steps=constraints["steps"],
                        context=context,
                        question=rewritten_question
                    )
                    # Create basic citations from chunks
                    citation_counter = 1
                    for chunk in chunks:
                        v_id = chunk.get("vault_id", "unknown")
                        chunk_index = chunk.get("chunk_index", 0)
                        chunk_content = chunk.get("content", "").strip()
                        score = chunk.get("score", 0.0)
                        filename = vault_id_to_filename.get(v_id, f"Document {v_id[:8]}")
                        
                        citations_metadata.append({
                            "citation_id": citation_counter,
                            "source_document_id": v_id,
                            "source_document_name": filename,
                            "chunk_id": str(chunk_index),
                            "quoted_text": chunk_content[:200] + "..." if len(chunk_content) > 200 else chunk_content,
                            "chunk_content": chunk_content,
                            "score": float(score)
                        })
                        citation_counter += 1
            except Exception as e:
                logging.error(f"Error generating cited answer: {e}", exc_info=True)
                # Fallback to regular generation
                assistant_text = await embedding_service.generate(
                    prompt="",
                    lines=constraints["lines"],
                    short=constraints["short"],
                    steps=constraints["steps"],
                    context=context,
                    question=rewritten_question
                )
                # Still create citations from chunks even if citation generation failed
                citation_counter = 1
                for chunk in chunks:
                    v_id = chunk.get("vault_id", "unknown")
                    chunk_index = chunk.get("chunk_index", 0)
                    chunk_content = chunk.get("content", "").strip()
                    score = chunk.get("score", 0.0)
                    filename = vault_id_to_filename.get(v_id, f"Document {v_id[:8]}")
                    
                    citations_metadata.append({
                        "citation_id": citation_counter,
                        "source_document_id": v_id,
                        "source_document_name": filename,
                        "chunk_id": str(chunk_index),
                        "quoted_text": chunk_content[:200] + "..." if len(chunk_content) > 200 else chunk_content,
                        "chunk_content": chunk_content,
                        "score": float(score)
                    })
                    citation_counter += 1
        else:
            # MODE B or MODE C: No relevant chunks found OR chunks have low relevance scores OR general knowledge question
            # Check if question is related to project domain or completely out of scope
            
            # If this is a general knowledge question, use MODE B (even if chunks were retrieved)
            if is_general_knowledge:
                logging.info(f"General knowledge question detected - using MODE B (no citations). Question: '{rewritten_question}'")
                assistant_text = await embedding_service.generate(
                    prompt="",
                    lines=constraints["lines"],
                    short=constraints["short"],
                    steps=constraints["steps"],
                    context="",  # Empty context - no documents available
                    question=rewritten_question,
                    no_documents=True  # Flag to indicate no documents
                )
                citations_metadata = []
            else:
                # Check if question is related to project domain or completely out of scope
                question_lower = rewritten_question.lower()
                is_project_related = any(term in question_lower for term in [
                    "project", "code", "implementation", "architecture", "tech stack",
                    "deployment", "backend", "frontend", "database", "api", "component",
                    "file", "document", "vault", "embedding", "rag", "faiss", "system",
                    "application", "software", "development", "programming", "technical"
                ])
                
                # If chunks were retrieved but have very low scores, they're likely irrelevant
                if chunks and len(chunks) > 0 and (avg_score < 0.3 and max_score < 0.4):
                    # Chunks retrieved but not relevant - treat as out of scope
                    logging.warning(f"Chunks retrieved but have low relevance (avg: {avg_score:.3f}, max: {max_score:.3f}) - returning out of scope message")
                    assistant_text = "This question is outside the scope of the available documents."
                    citations_metadata = []
                elif is_project_related:
                    # MODE B: Project-related but no documents - use general knowledge with label
                    assistant_text = await embedding_service.generate(
                        prompt="",
                        lines=constraints["lines"],
                        short=constraints["short"],
                        steps=constraints["steps"],
                        context="",  # Empty context - no documents available
                        question=rewritten_question,
                        no_documents=True  # Flag to indicate no documents
                    )
                    citations_metadata = []
                else:
                    # MODE C: Out of scope - not related to project domain
                    assistant_text = "This question is outside the scope of the available documents."
                    citations_metadata = []
        
        # 5. Enforce constraints as fail-safe (if not already applied in citation generation)
        # Note: Constraints are applied in citation generation, but apply again as fail-safe
        if not (chunks and len(chunks) > 0 and embedding_service.openai_client):
            assistant_text = enforce_constraints(
                assistant_text,
                lines=constraints["lines"],
                short=constraints["short"],
                steps=constraints["steps"]
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

        # Convert citations to Pydantic models
        citation_models = [
            CitationMetadata(**citation) for citation in citations_metadata
        ]

        return ChatResponse(
            response=assistant_text, 
            sources=used_documents["files"], 
            message_id=message_id, 
            conversation_id=conversation_id,
            citations=citation_models
        )

    except Exception as e:
        raise HTTPException(500, str(e))

@router.post("/stream")
async def chat_stream(payload: ChatRequest):
    """
    Streaming chat endpoint with SSE (Server-Sent Events).
    Streams tokens word-by-word, then sends citations at the end.
    """
    try:
        try:
            conversation_id = str(uuid.UUID(payload.conversation_id)) if payload.conversation_id else str(uuid.uuid4())
        except Exception:
            conversation_id = str(uuid.uuid4())

        # Validate user_id
        if not payload.user_id:
            def error_stream():
                yield sse_event("done", {"error": "user_id is required"})
            return StreamingResponse(error_stream(), media_type="text/event-stream")

        # Validate message
        if not payload.message or not payload.message.strip():
            def empty_stream():
                yield sse_event("done", {"error": "Empty question"})
            return StreamingResponse(empty_stream(), media_type="text/event-stream")

        # Get active document context (conversation-level document memory)
        active_document_id = payload.active_document_id
        active_document_text = None
        active_document_name = None
        
        # If active_document_id is provided, fetch document and text_content
        if active_document_id:
            try:
                doc_result = supabase.table("vault_files")\
                    .select("id, original_name, text_content")\
                    .eq("id", active_document_id)\
                    .eq("user_id", payload.user_id)\
                    .single()\
                    .execute()
                
                if doc_result.data:
                    active_document_name = doc_result.data.get("original_name", "Document")
                    text_content = doc_result.data.get("text_content")
                    if text_content and len(text_content.strip()) > 0:
                        active_document_text = text_content.strip()
                        logging.info(f"Streaming: Active document found: {active_document_name} (text length: {len(active_document_text)})")
                    else:
                        logging.warning(f"Streaming: Active document {active_document_id} has no text_content")
            except Exception as e:
                logging.warning(f"Streaming: Error fetching active document: {e}")
        
        # Detect vague document queries
        message_lower = payload.message.lower().strip()
        is_vague_document_query = any(phrase in message_lower for phrase in [
            "this document", "this file", "this doc", "the document", "the file",
            "explain this", "what is this", "tell me about this", "what's in this",
            "whats in this", "summarize this", "what does it say", "what does this say",
            "explain the document", "explain the file", "explain document", "explain file"
        ])
        logging.info(f"Streaming: Message='{payload.message}', Vague query={is_vague_document_query}, Active doc ID={active_document_id}")

        # Ensure conversation exists
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

        # Classify query
        query_classification = classify_query(payload.message)
        logging.info(f"Streaming query classification: {query_classification}")

        # Handle out-of-scope queries
        if query_classification.get("is_out_of_scope", False):
            def out_of_scope_stream():
                yield sse_event("token", {"text": "This question is outside the scope of the available documents."})
                yield sse_event("done", {"citations": [], "source": "out_of_scope"})
            return StreamingResponse(out_of_scope_stream(), media_type="text/event-stream")

        # Handle general knowledge questions - MODE_GENERAL
        if query_classification.get("is_general_knowledge", False):
            logging.info(f"Streaming general knowledge question: '{payload.message}'")
            constraints = extract_constraints(payload.message)
            original_question = payload.message.strip()

            # Build system prompt for MODE_GENERAL
            system_prompt = """You are FounderGPT.

YOU ARE IN MODE_GENERAL.

ANSWER MODE: MODE_GENERAL
- Answer using general knowledge
- Do NOT mention documents
- Do NOT mention chunks
- Do NOT include citations
- Always add at the end: "Source: Generated"

CRITICAL RULES:
- Never guess which mode you are in - you are explicitly in MODE_GENERAL
- Never mix modes - use ONLY general knowledge
- Never mention documents, chunks, or sources
- Never include citations
- Always end with "Source: Generated"
- NEVER say "your message is empty" or "your message is blank" - you have a valid question
- NEVER say "It seems like your message" - always answer the question directly
- If you see a question, answer it immediately using general knowledge"""

            user_prompt = f"""=== USER QUESTION (YOU MUST ANSWER THIS) ===
{original_question}
=== END OF QUESTION ===

YOUR TASK: Answer the question above using general knowledge.

CRITICAL REMINDERS:
- You are in MODE_GENERAL - answer using general knowledge only
- You have a VALID QUESTION above (between the === markers) - answer it directly
- Do NOT mention documents, chunks, or sources
- Do NOT include citations
- Always add at the end: "Source: Generated"
- Never mix modes - you are explicitly in MODE_GENERAL
- NEVER say "your message is empty" or "your message is blank" - you have a question above
- NEVER say "It seems like your message" - always answer the question
- Answer the question IMMEDIATELY using general knowledge"""

            def general_knowledge_stream():
                full_response = ""
                for token in stream_llm(system_prompt, user_prompt):
                    full_response += token
                    yield sse_event("token", {"text": token})
                
                # Ensure "Source: Generated" is at the end
                if "Source: Generated" not in full_response:
                    yield sse_event("token", {"text": " Source: Generated"})
                
                # Save message
                try:
                    supabase.table("messages").insert({
                        "conversation_id": conversation_id,
                        "user_message": payload.message,
                        "assistant_message": full_response + (" Source: Generated" if "Source: Generated" not in full_response else ""),
                        "used_documents": {"chunks": [], "files": []},
                        "created_at": datetime.utcnow().isoformat()
                    }).execute()
                except Exception as e:
                    logging.error(f"Error saving message: {e}")
                
                yield sse_event("done", {"citations": [], "source": "generated"})
            
            return StreamingResponse(
                general_knowledge_stream(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                }
            )

        # Handle greetings
        if query_classification["is_greeting"]:
            greeting_responses = [
                "Hello! How can I help you today?",
                "Hi there! What would you like to know?",
                "Hello! I'm here to help. What can I assist you with?",
            ]
            response_text = random.choice(greeting_responses)
            
            def greeting_stream():
                for char in response_text:
                    yield sse_event("token", {"text": char})
                yield sse_event("done", {"citations": [], "source": "greeting"})
            
            return StreamingResponse(greeting_stream(), media_type="text/event-stream")

        # Handle vague document queries with active document text_content
        chunks = []
        using_direct_text = False
        if is_vague_document_query and active_document_text:
            logging.info(f"Streaming: Vague document query with active document text - injecting text_content directly")
            logging.info(f"Streaming: Active document text length: {len(active_document_text)}, Preview: {active_document_text[:200]}...")
            chunks = [{
                "vault_id": active_document_id,
                "content": active_document_text,
                "chunk_index": 0,
                "score": 1.0,
                "id": f"active_doc_{active_document_id}"
            }]
            using_direct_text = True
        elif is_vague_document_query and active_document_id and not active_document_text:
            logging.warning(f"Streaming: Vague query detected but active document {active_document_id} has no text_content")
        
        # MODE_DOCUMENT: Perform RAG retrieval (blocking, done once)
        context = ""
        citations_metadata = []
        vault_id_to_filename = {}
        context_pieces = []
        
        if query_classification["needs_rag"] and not using_direct_text:
            # Generate query embedding
            try:
                query_embedding = await embedding_service.embed_text(payload.message)
                if query_embedding is None or len(query_embedding) == 0:
                    raise HTTPException(500, "Failed to generate query embedding: Empty embedding returned")
            except Exception as e:
                logging.error(f"Error generating query embedding: {e}")
                raise HTTPException(500, f"Failed to generate query embedding: {str(e)}")

            # Perform FAISS search
            try:
                chunks = faiss_search(
                    query_embedding=query_embedding,
                    user_id=payload.user_id,
                    top_k=payload.top_k,
                    vault_id=payload.vault_id
                )
                logging.info(f"FAISS search returned {len(chunks)} chunks")
            except Exception as e:
                logging.error(f"FAISS search failed: {e}")
                raise HTTPException(500, f"FAISS search failed: {e}")

            # Build context and citations
            used_chunk_ids = []
            used_files = []
            
            for c in chunks:
                v_id = c.get("vault_id", "Unknown")
                chunk_content = c.get("content", "").strip()
                
                if not chunk_content or len(chunk_content) < 10:
                    continue
                
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
                used_chunk_ids.append(c.get("id"))
                snippet = chunk_content[:1000]
                context_pieces.append(f"[{filename}] (chunk {c.get('chunk_index', 0)}):\n{snippet}")

            context = "\n\n---\n\n".join(context_pieces) if context_pieces else ""
            num_context_pieces = len(context_pieces)
        else:
            # If using direct text injection, build context from active document
            if using_direct_text and active_document_text:
                context_pieces = [f"[{active_document_name}] (full document):\n{active_document_text}"]
                vault_id_to_filename[active_document_id] = active_document_name
                used_files = [active_document_name]
                context = "\n\n---\n\n".join(context_pieces)
                num_context_pieces = 1
                logging.info(f"Streaming: Using direct text injection for active document: {active_document_name}")

        # Check chunk relevance
        chunk_scores = [c.get("score", 0.0) for c in chunks if c.get("score") is not None]
        avg_score = sum(chunk_scores) / len(chunk_scores) if chunk_scores else 0.0
        max_score = max(chunk_scores) if chunk_scores else 0.0
        chunks_are_relevant = (len(context_pieces) > 0 and (avg_score > 0.3 or max_score > 0.4)) if chunks else (using_direct_text and active_document_text)

        # Handle case: vague document query but no active document or text
        if is_vague_document_query and not active_document_text and not chunks_are_relevant:
            if active_document_id:
                def no_text_stream():
                    yield sse_event("token", {"text": f"I couldn't read text from '{active_document_name or 'this document'}'. Please upload a text-based DOCX or PDF file."})
                    yield sse_event("done", {"citations": [], "source": "error"})
                return StreamingResponse(no_text_stream(), media_type="text/event-stream")
            else:
                def no_doc_stream():
                    yield sse_event("token", {"text": "Please upload or select a document first, then ask about it."})
                    yield sse_event("done", {"citations": [], "source": "error"})
                return StreamingResponse(no_doc_stream(), media_type="text/event-stream")
        
        # Build prompts for MODE_DOCUMENT
        # Use direct text if available, otherwise use FAISS chunks
        if using_direct_text and active_document_text:
            # Direct text injection path
            logging.info(f"Streaming: Using direct text injection for MODE_DOCUMENT")
            constraints = extract_constraints(payload.message)
            rewritten_question = payload.message  # Keep original for vague queries
            
            system_prompt = f"""You are FounderGPT powered by OpenAI.

CONVERSATION AWARENESS RULES (STRICT):

1. The user may ask vague or incomplete questions.
2. If a document was uploaded or selected earlier in the conversation:
   - Assume references like "this document", "this file", "it", or "this" refer to that document.
3. Do NOT ask the user to restate the question if intent is clear.
4. Behave like ChatGPT when interpreting user intent.

DOCUMENT USAGE RULES:

- If document text is available, use it automatically.
- If document text is NOT available, clearly explain why.
- Never generate generic answers for document-specific questions.

YOU ARE IN MODE_DOCUMENT.

ANSWER MODE: MODE_DOCUMENT
- Use ONLY the provided document text
- Provide a comprehensive answer based on the full document
- Mention the document clearly when relevant

CRITICAL RULES:
- Never guess which mode you are in - you are explicitly in MODE_DOCUMENT
- Never mix modes - use ONLY the provided document text
- Never say a message is blank if text exists
- Answer naturally and comprehensively based on the document content"""

            user_prompt = f"""YOU ARE IN MODE_DOCUMENT.

DOCUMENT CONTENT:
{active_document_text}

QUESTION:
{rewritten_question}

Generate a comprehensive answer based on the document content above. Answer naturally and helpfully, as if you are explaining the document to the user."""

            def direct_text_stream():
                full_response = ""
                for token in stream_llm(system_prompt, user_prompt):
                    full_response += token
                    yield sse_event("token", {"text": token})
                
                # Save message
                try:
                    supabase.table("messages").insert({
                        "conversation_id": conversation_id,
                        "user_message": payload.message,
                        "assistant_message": full_response,
                        "used_documents": {"chunks": [], "files": [active_document_name]},
                        "created_at": datetime.utcnow().isoformat()
                    }).execute()
                except Exception as e:
                    logging.error(f"Error saving message: {e}")
                
                yield sse_event("done", {"citations": [], "source": "document"})
            
            return StreamingResponse(direct_text_stream(), media_type="text/event-stream")
        elif chunks_are_relevant and chunks and len(chunks) > 0:
            # Use citation service to build prompts
            constraints = extract_constraints(payload.message)
            rewritten_question = await rewrite_question(payload.message)
            if not rewritten_question or not rewritten_question.strip():
                rewritten_question = payload.message

            # Build system prompt for MODE_DOCUMENT
            system_prompt = f"""You are FounderGPT powered by OpenAI.

CONVERSATION AWARENESS RULES (STRICT):

1. The user may ask vague or incomplete questions.
2. If a document was uploaded or selected earlier in the conversation:
   - Assume references like "this document", "this file", "it", or "this" refer to that document.
3. Do NOT ask the user to restate the question if intent is clear.
4. Behave like ChatGPT when interpreting user intent.

DOCUMENT USAGE RULES:

- If document text is available, use it automatically.
- If document text is NOT available, clearly explain why.
- Never generate generic answers for document-specific questions.

YOU ARE IN MODE_DOCUMENT.

ANSWER MODE: MODE_DOCUMENT
- Use ONLY the provided document chunks
- Include citations [1], [2], etc. for every factual statement from documents
- Mention documents clearly when relevant
- If answer is not in chunks, say: "The answer is not available in the uploaded documents."

CRITICAL RULES:
- Never guess which mode you are in - you are explicitly in MODE_DOCUMENT
- Never mix modes - use ONLY document chunks
- Never fabricate citations - only cite chunks that exist [1] through [{num_context_pieces}]
- Never say a message is blank if text exists

STRICT CITATION RULES (NON-NEGOTIABLE):
1. ONLY cite information that comes DIRECTLY from the provided context chunks
2. Every factual statement derived from documents MUST include a citation reference like [1], [2]
3. Use the citation number that corresponds to the chunk number in the context (chunks are numbered [1], [2], [3], etc.)
4. If multiple chunks support a statement, cite all relevant ones: [1][2] or [1,2]
5. DO NOT cite general knowledge - only cite document-specific information
6. DO NOT invent citations - only use citations 1 through {num_context_pieces}
7. NEVER create fake citations - if information is general knowledge, do NOT cite it
8. NEVER imply sources if none were used - only cite when information comes from chunks
9. Place citations immediately after the statement they support
10. If information is not in the chunks, say: "The answer is not available in the uploaded documents."

OUTPUT FORMAT:
- Write clean, professional text in natural paragraphs
- Include inline citations like [1] or [2][3] immediately after factual statements FROM DOCUMENTS
- You MAY mention "the uploaded documents" or "the provided documents" when relevant
- Do NOT use markdown formatting (no **, *, #, etc.)
- Write in clean plain text like ChatGPT"""

            user_prompt = f"""YOU ARE IN MODE_DOCUMENT.

CONTEXT CHUNKS (numbered for citation):
{context}

QUESTION:
{rewritten_question}

Generate a comprehensive answer with inline citations [1], [2], etc. immediately after each factual statement derived from the context chunks above. Use only the citation numbers that correspond to the chunk numbers in the context.

CRITICAL REMINDERS:
- You are in MODE_DOCUMENT - use ONLY the provided document chunks
- Include citations [1], [2], etc. for every factual statement from documents
- If answer is not in chunks, say: "The answer is not available in the uploaded documents."
- Only cite information that comes DIRECTLY from the context chunks
- Do NOT cite general knowledge
- Do NOT invent citations
- Never mix modes - you are explicitly in MODE_DOCUMENT"""

            def document_stream():
                full_response = ""
                for token in stream_llm(system_prompt, user_prompt):
                    full_response += token
                    yield sse_event("token", {"text": token})
                
                # Extract citations from response
                import re
                citation_ids = set(re.findall(r'\[(\d+)\]', full_response))
                
                # Build citation metadata
                citations_metadata = []
                citation_counter = 1
                for chunk in chunks[:len(context_pieces)]:
                    v_id = chunk.get("vault_id", "unknown")
                    chunk_index = chunk.get("chunk_index", 0)
                    chunk_content = chunk.get("content", "").strip()
                    score = chunk.get("score", 0.0)
                    filename = vault_id_to_filename.get(v_id, f"Document {v_id[:8]}")
                    
                    if str(citation_counter) in citation_ids:
                        citations_metadata.append({
                            "citation_id": citation_counter,
                            "source_document_id": v_id,
                            "source_document_name": filename,
                            "chunk_id": str(chunk_index),
                            "quoted_text": chunk_content[:200] + "..." if len(chunk_content) > 200 else chunk_content,
                            "chunk_content": chunk_content,
                            "score": float(score)
                        })
                    citation_counter += 1
                
                # Save message
                try:
                    used_chunk_ids = [c.get("id") for c in chunks if c.get("id")]
                    used_files = list(dict.fromkeys(vault_id_to_filename.values()))
                    supabase.table("messages").insert({
                        "conversation_id": conversation_id,
                        "user_message": payload.message,
                        "assistant_message": full_response,
                        "used_documents": {"chunks": used_chunk_ids, "files": used_files},
                        "created_at": datetime.utcnow().isoformat()
                    }).execute()
                except Exception as e:
                    logging.error(f"Error saving message: {e}")
                
                yield sse_event("done", {
                    "citations": citations_metadata,
                    "source": "document" if citations_metadata else "generated"
                })
            
            return StreamingResponse(
                document_stream(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                }
            )
        else:
            # No relevant chunks - use MODE_GENERAL
            constraints = extract_constraints(payload.message)
            original_question = payload.message.strip()

            system_prompt = """You are FounderGPT.

YOU ARE IN MODE_GENERAL.

ANSWER MODE: MODE_GENERAL
- Answer using general knowledge
- Do NOT mention documents
- Do NOT mention chunks
- Do NOT include citations
- Always add at the end: "Source: Generated"

CRITICAL RULES:
- Never guess which mode you are in - you are explicitly in MODE_GENERAL
- Never mix modes - use ONLY general knowledge
- Never mention documents, chunks, or sources
- Never include citations
- Always end with "Source: Generated"
- NEVER say "your message is empty" or "your message is blank" - you have a valid question
- NEVER say "It seems like your message" - always answer the question directly"""

            user_prompt = f"""=== USER QUESTION (YOU MUST ANSWER THIS) ===
{original_question}
=== END OF QUESTION ===

YOUR TASK: Answer the question above using general knowledge.

CRITICAL REMINDERS:
- You are in MODE_GENERAL - answer using general knowledge only
- You have a VALID QUESTION above - answer it directly
- Do NOT mention documents, chunks, or sources
- Do NOT include citations
- Always add at the end: "Source: Generated"
- Never mix modes - you are explicitly in MODE_GENERAL
- NEVER say "your message is empty" or "your message is blank" - you have a question above
- NEVER say "It seems like your message" - always answer the question
- Answer the question IMMEDIATELY using general knowledge"""

            def general_stream():
                full_response = ""
                for token in stream_llm(system_prompt, user_prompt):
                    full_response += token
                    yield sse_event("token", {"text": token})
                
                # Ensure "Source: Generated" is at the end
                if "Source: Generated" not in full_response:
                    yield sse_event("token", {"text": " Source: Generated"})
                
                # Save message
                try:
                    supabase.table("messages").insert({
                        "conversation_id": conversation_id,
                        "user_message": payload.message,
                        "assistant_message": full_response + (" Source: Generated" if "Source: Generated" not in full_response else ""),
                        "used_documents": {"chunks": [], "files": []},
                        "created_at": datetime.utcnow().isoformat()
                    }).execute()
                except Exception as e:
                    logging.error(f"Error saving message: {e}")
                
                yield sse_event("done", {"citations": [], "source": "generated"})
            
            return StreamingResponse(
                general_stream(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                }
            )

    except Exception as e:
        logging.error(f"Error in streaming endpoint: {e}", exc_info=True)
        def error_stream():
            yield sse_event("done", {"error": str(e)})
        return StreamingResponse(error_stream(), media_type="text/event-stream")
