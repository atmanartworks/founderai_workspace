# app/services/citation_service.py

"""
Citation service for generating interactive citations from RAG chunks.
Tracks which chunks are used in answers and creates citation metadata.
"""

import re
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

@dataclass
class Citation:
    """Citation metadata for a specific chunk reference"""
    citation_id: int  # Sequential number [1], [2], etc.
    source_document_id: str  # vault_id
    source_document_name: str  # filename
    chunk_id: Optional[str]  # chunk_index or unique identifier
    quoted_text: str  # Exact text excerpt from chunk
    chunk_content: str  # Full chunk content for reference
    score: float  # Relevance score from FAISS

class CitationService:
    """Service for generating and managing citations"""
    
    @staticmethod
    def create_citations_from_chunks(chunks: List[Dict]) -> Dict[str, Citation]:
        """
        Create citation objects from retrieved chunks.
        
        Args:
            chunks: List of chunk dictionaries from FAISS search
            
        Returns:
            Dictionary mapping chunk identifiers to Citation objects
        """
        citations = {}
        vault_id_to_filename = {}
        
        for idx, chunk in enumerate(chunks):
            vault_id = chunk.get("vault_id", "unknown")
            chunk_index = chunk.get("chunk_index", idx)
            chunk_content = chunk.get("content", "").strip()
            score = chunk.get("score", 0.0)
            
            # Get or cache filename
            if vault_id not in vault_id_to_filename:
                # Will be populated by caller with actual filename
                vault_id_to_filename[vault_id] = f"Document {vault_id[:8]}"
            
            # Create unique chunk identifier
            chunk_id = f"{vault_id}_{chunk_index}"
            
            # Extract a representative quote (first 200 chars)
            quoted_text = chunk_content[:200] + "..." if len(chunk_content) > 200 else chunk_content
            
            citation = Citation(
                citation_id=0,  # Will be assigned when used
                source_document_id=vault_id,
                source_document_name=vault_id_to_filename[vault_id],
                chunk_id=str(chunk_index),
                quoted_text=quoted_text,
                chunk_content=chunk_content,
                score=score
            )
            
            citations[chunk_id] = citation
        
        return citations, vault_id_to_filename
    
    @staticmethod
    def extract_citations_from_answer(
        answer: str,
        chunks: List[Dict],
        vault_id_to_filename: Dict[str, str]
    ) -> Tuple[str, List[Dict]]:
        """
        Extract citations from answer text and create citation metadata.
        
        This is a simplified version - in production, you'd use LLM to identify
        which chunks were actually used for each statement.
        
        Args:
            answer: The generated answer text
            chunks: List of chunks used in context
            vault_id_to_filename: Mapping of vault_id to filename
            
        Returns:
            Tuple of (answer_with_citations, citation_metadata)
        """
        # For now, we'll attach citations to chunks that were used
        # In a more sophisticated system, you'd use LLM to identify which
        # statements correspond to which chunks
        
        citation_metadata = []
        citation_counter = 1
        
        # Map chunks by their content for citation matching
        chunk_map = {}
        for chunk in chunks:
            vault_id = chunk.get("vault_id", "unknown")
            chunk_index = chunk.get("chunk_index", 0)
            chunk_content = chunk.get("content", "").strip()
            score = chunk.get("score", 0.0)
            
            filename = vault_id_to_filename.get(vault_id, f"Document {vault_id[:8]}")
            chunk_id = f"{vault_id}_{chunk_index}"
            
            # Create citation metadata
            citation_meta = {
                "citation_id": citation_counter,
                "source_document_id": vault_id,
                "source_document_name": filename,
                "chunk_id": str(chunk_index),
                "quoted_text": chunk_content[:200] + "..." if len(chunk_content) > 200 else chunk_content,
                "chunk_content": chunk_content,
                "score": float(score)
            }
            
            citation_metadata.append(citation_meta)
            chunk_map[chunk_id] = citation_counter
            citation_counter += 1
        
        # For now, append citations at the end
        # In production, you'd use LLM to identify inline citations
        answer_with_citations = answer
        
        # If we have citations, add them as references
        if citation_metadata:
            # Add citation markers - simple approach: add [1], [2] at end
            # In production, use LLM to identify which statements need citations
            citation_refs = " ".join([f"[{c['citation_id']}]" for c in citation_metadata])
            answer_with_citations = f"{answer}\n\nCitations: {citation_refs}"
        
        return answer_with_citations, citation_metadata
    
    @staticmethod
    def generate_cited_answer_with_llm(
        question: str,
        chunks: List[Dict],
        vault_id_to_filename: Dict[str, str],
        openai_client,
        lines: int = 0,
        short: bool = False,
        steps: bool = False
    ) -> Tuple[str, List[Dict]]:
        """
        Use LLM to generate answer with inline citations.
        
        Args:
            question: User's question
            chunks: Retrieved chunks from FAISS
            vault_id_to_filename: Mapping of vault_id to filename
            openai_client: OpenAI client instance
            
        Returns:
            Tuple of (answer_with_citations, citation_metadata)
        """
        # Validate chunk relevance scores before proceeding
        chunk_scores = [c.get("score", 0.0) for c in chunks if c.get("score") is not None]
        if chunk_scores:
            avg_score = sum(chunk_scores) / len(chunk_scores)
            max_score = max(chunk_scores)
            # If all chunks have very low relevance, they're likely irrelevant
            if avg_score < 0.3 and max_score < 0.4:
                logging.warning(f"CitationService: Chunks have low relevance scores (avg: {avg_score:.3f}, max: {max_score:.3f}) - likely irrelevant to question '{question[:50]}...'")
                return "This question is outside the scope of the available documents.", []
        
        # Build context with chunk identifiers
        context_parts = []
        citation_metadata = []
        citation_counter = 1
        
        for chunk in chunks:
            vault_id = chunk.get("vault_id", "unknown")
            chunk_index = chunk.get("chunk_index", 0)
            chunk_content = chunk.get("content", "").strip()
            score = chunk.get("score", 0.0)
            
            # Skip empty chunks
            if not chunk_content or len(chunk_content) < 10:
                continue
            
            filename = vault_id_to_filename.get(vault_id, f"Document {vault_id[:8]}")
            
            # Create citation metadata
            citation_meta = {
                "citation_id": citation_counter,
                "source_document_id": vault_id,
                "source_document_name": filename,
                "chunk_id": str(chunk_index),
                "quoted_text": chunk_content[:200] + "..." if len(chunk_content) > 200 else chunk_content,
                "chunk_content": chunk_content,
                "score": float(score)
            }
            
            citation_metadata.append(citation_meta)
            
            # Add chunk to context with citation marker - format: [1] Document Name (chunk 0): content
            context_parts.append(f"[{citation_counter}] {filename} (chunk {chunk_index}):\n{chunk_content}")
            citation_counter += 1
        
        if not context_parts:
            # No relevant chunks found - return message indicating answer not in documents
            return "The answer is not available in the uploaded documents.", []
        
        context = "\n\n---\n\n".join(context_parts)
        
        # Build format instructions based on constraints
        format_instructions = []
        if lines > 0:
            format_instructions.append(f"- Answer in EXACTLY {lines} lines")
            format_instructions.append(f"- Each line max 20 words")
        if short:
            format_instructions.append("- Be brief and concise")
        if steps:
            format_instructions.append("- Format as numbered steps")
        
        format_text = "\n".join(format_instructions) if format_instructions else "- Provide a comprehensive, detailed answer"
        
        # Prompt LLM to generate answer with citations
        system_prompt = f"""You are FounderGPT powered by OpenAI.

CONVERSATION AWARENESS RULES (STRICT):

1. The user may ask vague or incomplete questions.
2. If a document was uploaded or selected earlier in the conversation:
   - Assume references like "this document", "this file", "it", or "this" refer to that document.
3. Do NOT ask the user to restate the question if intent is clear.
4. Behave like ChatGPT when interpreting user intent.

YOU ARE IN MODE_DOCUMENT.

ANSWER MODE: MODE_DOCUMENT
- Use ONLY the provided document chunks
- Include citations [1], [2], etc. for every factual statement from documents
- Mention documents clearly when relevant
- If answer is not in chunks, say: "The answer is not available in the uploaded documents."

CRITICAL RULES:
- Never guess which mode you are in - you are explicitly in MODE_DOCUMENT
- Never mix modes - use ONLY document chunks
- Never fabricate citations - only cite chunks that exist [1] through [{len(context_parts)}]
- Never say a message is blank if text exists

STRICT CITATION RULES (NON-NEGOTIABLE):
1. ONLY cite information that comes DIRECTLY from the provided context chunks
2. Every factual statement derived from documents MUST include a citation reference like [1], [2]
3. Use the citation number that corresponds to the chunk number in the context (chunks are numbered [1], [2], [3], etc.)
4. If multiple chunks support a statement, cite all relevant ones: [1][2] or [1,2]
5. DO NOT cite general knowledge - only cite document-specific information
6. DO NOT invent citations - only use citations 1 through {len(context_parts)}
7. NEVER create fake citations - if information is general knowledge, do NOT cite it
8. NEVER imply sources if none were used - only cite when information comes from chunks
9. Place citations immediately after the statement they support
10. If information is not in the chunks, say: "The answer is not available in the uploaded documents."

FORMAT REQUIREMENTS:
{format_text}

OUTPUT FORMAT:
- Write clean, professional text in natural paragraphs
- Include inline citations like [1] or [2][3] immediately after factual statements FROM DOCUMENTS
- You MAY mention "the uploaded documents" or "the provided documents" when relevant
- Do NOT use markdown formatting (no **, *, #, etc.)
- Write in clean plain text like ChatGPT
- Follow the format requirements above strictly

EXAMPLE:
"Based on the uploaded documents, the project uses React for the frontend [1] and FastAPI for the backend [2]. The deployment is handled on Vercel [1]. The application follows a clean architecture pattern [2]."

Remember: You are in MODE_DOCUMENT. Use ONLY document chunks. Include citations. Never invent citations."""

        user_prompt = f"""YOU ARE IN MODE_DOCUMENT.

CONTEXT CHUNKS (numbered for citation):
{context}

QUESTION:
{question}

Generate a comprehensive answer with inline citations [1], [2], etc. immediately after each factual statement derived from the context chunks above. Use only the citation numbers that correspond to the chunk numbers in the context.

CRITICAL REMINDERS:
- You are in MODE_DOCUMENT - use ONLY the provided document chunks
- Include citations [1], [2], etc. for every factual statement from documents
- If answer is not in chunks, say: "The answer is not available in the uploaded documents."
- Only cite information that comes DIRECTLY from the context chunks
- Do NOT cite general knowledge
- Do NOT invent citations
- Never mix modes - you are explicitly in MODE_DOCUMENT"""

        try:
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.4,
                max_tokens=2000
            )
            
            answer = response.choices[0].message.content.strip()
            
            # Extract citation numbers used in answer
            citation_numbers = re.findall(r'\[(\d+)\]', answer)
            used_citation_ids = set([int(n) for n in citation_numbers if n.isdigit()])
            
            # Filter to only include citations that were actually used in the answer
            # STRICT RULE: Only return citations that were explicitly referenced
            if used_citation_ids:
                used_citations = [
                    c for c in citation_metadata 
                    if c["citation_id"] in used_citation_ids
                ]
            else:
                # If LLM didn't use citations, return empty list
                # STRICT RULE: Never return citations that weren't explicitly used
                used_citations = []
                logging.warning("LLM generated answer but did not use any citations - returning empty citations list")
            
            logging.info(f"Generated answer with {len(used_citations)} citations from {len(citation_metadata)} available chunks")
            
            return answer, used_citations
            
        except Exception as e:
            logging.error(f"Error generating cited answer: {e}")
            # Fallback: return answer without citations
            return f"Error generating answer: {str(e)}", []
