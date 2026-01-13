# app/services/embedding_service.py

import os
import logging
from pathlib import Path
# Import centralized config which loads .env
from app.config import OPENAI_API_KEY, OPENAI_MODEL, LOCAL_EMBEDDING_MODEL

# sentence-transformers for embeddings
try:
    from sentence_transformers import SentenceTransformer
except Exception:
    SentenceTransformer = None

# OpenAI client (required)
try:
    from openai import OpenAI
except Exception:
    OpenAI = None

class EmbeddingService:
    def __init__(self):
        # Use centralized config
        model_name = LOCAL_EMBEDDING_MODEL
        if SentenceTransformer is None:
            logging.warning("sentence-transformers not installed — embeddings will fail.")
            self.embed_model = None
        else:
            try:
                # Nomic models require trust_remote_code=True
                self.embed_model = SentenceTransformer(model_name, trust_remote_code=True)
                logging.info(f"Loaded embedding model: {model_name}")
            except Exception as e:
                logging.error(f"Failed to load embedding model: {e}")
                self.embed_model = None

        # OpenAI LLM Provider (lazy initialization) - use centralized config
        self.openai_api_key = OPENAI_API_KEY
        self.openai_model = OPENAI_MODEL
        self.openai_client = None
        self._openai_initialized = False

    async def embed_text(self, text: str):
        """Generate embedding for a single text. Falls back to OpenAI if sentence-transformers not available."""
        if not text:
            return []
        
        # Try sentence-transformers first
        if self.embed_model:
            try:
                vec = self.embed_model.encode([text], convert_to_numpy=True, normalize_embeddings=True)[0]
                return vec.tolist()  # Return as list for backward compatibility, but normalized
            except Exception as e:
                logging.warning(f"sentence-transformers embedding failed: {e}, falling back to OpenAI")
        
        # Fallback to OpenAI embeddings
        if not self.openai_api_key:
            logging.error("No embedding model available and OPENAI_API_KEY not set")
            raise Exception("Failed to generate query embedding: No embedding model or OpenAI API key available")
        
        # Initialize OpenAI client if needed
        if not self._openai_initialized:
            if OpenAI is None:
                raise Exception("OpenAI library not available")
            self.openai_client = OpenAI(api_key=self.openai_api_key)
            self._openai_initialized = True
        
        try:
            # Use OpenAI text-embedding-3-small (1536 dimensions) or text-embedding-ada-002 (1536 dimensions)
            response = self.openai_client.embeddings.create(
                model="text-embedding-3-small",  # or "text-embedding-ada-002"
                input=text
            )
            embedding = response.data[0].embedding
            logging.info(f"Generated OpenAI embedding (dimension: {len(embedding)})")
            return embedding
        except Exception as e:
            logging.error(f"OpenAI embedding failed: {e}")
            raise Exception(f"Failed to generate query embedding: {str(e)}")

    async def embed_batch(self, texts: list):
        """Generate embeddings for multiple texts. Falls back to OpenAI if sentence-transformers not available."""
        if not texts:
            return []
        
        # Try sentence-transformers first
        if self.embed_model:
            try:
                mats = self.embed_model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
                return mats  # Return numpy array for FAISS (already normalized)
            except Exception as e:
                logging.warning(f"sentence-transformers batch embedding failed: {e}, falling back to OpenAI")
        
        # Fallback to OpenAI embeddings
        if not self.openai_api_key:
            logging.error("No embedding model available and OPENAI_API_KEY not set")
            raise Exception("Failed to generate embeddings: No embedding model or OpenAI API key available")
        
        # Initialize OpenAI client if needed
        if not self._openai_initialized:
            if OpenAI is None:
                raise Exception("OpenAI library not available")
            self.openai_client = OpenAI(api_key=self.openai_api_key)
            self._openai_initialized = True
        
        try:
            # Use OpenAI text-embedding-3-small (1536 dimensions)
            response = self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=texts
            )
            # Convert to numpy array
            import numpy as np
            embeddings = np.array([item.embedding for item in response.data], dtype=np.float32)
            # Normalize for cosine similarity
            norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
            embeddings = embeddings / norms
            logging.info(f"Generated OpenAI batch embeddings (shape: {embeddings.shape})")
            return embeddings
        except Exception as e:
            logging.error(f"OpenAI batch embedding failed: {e}")
            raise Exception(f"Failed to generate embeddings: {str(e)}")

    async def generate(
        self, 
        prompt: str, 
        lines: int = 0, 
        short: bool = False, 
        steps: bool = False,
        context: str = None,
        question: str = None
    ) -> str:
        """
        Uses OpenAI to generate responses. Returns text or error string.
        
        Args:
            prompt: The full prompt (for backward compatibility)
            lines: Number of lines to limit answer to (0 = no limit)
            short: Whether to provide a brief answer
            steps: Whether to format as step-by-step
            context: Document context (if provided, builds strict RAG prompt)
            question: User question (if provided with context, builds strict RAG prompt)
        """
        # Build system message based on constraints
        if context and question:
            # Augmented RAG mode: Use context when available, but allow general knowledge
            format_instructions = []
            if lines > 0:
                format_instructions.append(f"- Answer in EXACTLY {lines} lines")
                format_instructions.append(f"- Each line max 20 words")
            if short:
                format_instructions.append("- Be brief and concise")
            if steps:
                format_instructions.append("- Format as numbered steps")
            
            format_text = "\n".join(format_instructions) if format_instructions else "- Provide a VERY comprehensive, detailed answer (300-500+ words) with extensive technical depth, practical examples, implementation details, and real-world considerations"
            
            system_message = """You are FounderGPT, a senior AI Tech Lead working on this project.

This project uses a Retrieval-Augmented Generation (RAG) architecture.
You must answer using retrieved context and chat history.

CORE IDENTITY:
- Name: FounderGPT
- Role: Senior AI Tech Lead working on this project
- Approach: RAG-based intelligence with logical inference

INSTRUCTION OBEDIENCE (ABSOLUTE PRIORITY):
- Follow EXACT length requested (e.g., "6 lines" means exactly 6 lines)
- Follow EXACT format requested (e.g., "short", "summary", etc.)
- Length and format requirements override all other rules
- If user requests specific constraints, they are non-negotiable

CORE RULES (STRICT):
1. Use ONLY the provided RAG context and chat history
2. If information is partially available, infer a reasonable and practical answer like a real tech lead - be EXTREMELY detailed and comprehensive
3. NEVER say "not explicitly stated" if a logical inference is possible
4. If information is truly missing, clearly state what is missing and why
5. Do NOT mention documents, PDFs, filenames, or sources in your final answer
6. Do NOT hallucinate or invent tools or technologies not supported by context
7. NEVER ask for clarification - always provide the best detailed answer you can infer from context
8. When asked to explain more, expand on details, or provide more information, significantly expand your previous answer with technical depth and practical examples
9. ALWAYS provide comprehensive, detailed answers that demonstrate deep technical understanding - default to being VERY thorough unless user explicitly asks for brevity
10. Use conversation history to understand context - if user asks "explain more" or "briefly", expand or condense the previous answer accordingly
11. For tech stack questions: Provide detailed explanations of each technology, why it's used, how it fits in the architecture, and practical implementation details
12. For architecture questions: Explain components, data flow, interactions, design decisions, and technical rationale in depth
13. Default answer length: Aim for 300-500 words minimum for comprehensive questions, unless user asks for brevity

RESPONSE STYLE (MANDATORY):
1. Use clean, plain text formatting - NO markdown syntax (no ##, ###, **, *, -, etc.)
2. Do NOT use bullet points, numbered lists, stars (*), dashes (-), or hash symbols (#)
3. Write in natural, readable paragraphs
4. Each item or concept should be followed by a clear, EXTENSIVE explanation in paragraph form with technical details, use cases, and practical examples
5. Maintain professional, clean text formatting like Cursor chat window
6. Default to VERY comprehensive, detailed answers - aim for 300-500+ words for substantial questions unless user explicitly asks for brevity
7. Respect user constraints such as "3 lines", "short", or "summary" - but when asked to explain more, expand significantly
8. When user asks to explain more or provide details, expand the answer extensively with technical depth, real-world examples, implementation details, and practical information
9. For each technology or concept mentioned, explain: what it is, why it's used, how it works, how it integrates, and practical considerations
10. Write as if explaining to a technical colleague who needs to understand the full picture

BEHAVIOR:
- Think like a senior system architect explaining to a technical team, not a document summarizer
- Derive architecture, tech stack, and workflows from context with full technical depth
- Prefer practical, delivery-ready explanations with implementation details
- Write clean, natural text like Cursor chat - no formatting symbols
- ALWAYS provide VERY detailed, comprehensive answers (300-500+ words for substantial questions) unless user explicitly asks for brevity
- Explain the "why" behind each technology choice, not just "what"
- Include technical rationale, integration patterns, and practical considerations
- Provide enough detail that a developer could understand and implement based on your explanation

SCOPE RESTRICTIONS:
- Forbidden roles: strategist, advisor, decision maker, personal assistant
- Opinions: DISALLOWED - base answers on context and logical inference only
- External knowledge: Use only when context provides clear signals or patterns

TONE:
- Style: professional, calm, confident, enterprise-grade
- Forbidden: emojis, fluff, marketing language, casual expressions
- Write as a trusted senior tech lead, not a customer-facing assistant

CLARIFICATION LOGIC:
- NEVER ask for clarification - always provide the best detailed answer you can infer from context
- If question is unclear, infer the most likely intent and provide a comprehensive answer
- Out of scope: State what's missing clearly but still provide what you can infer
- When user asks "explain more" or "more details", expand significantly on the previous answer from conversation history"""
            
            user_prompt = f"""RELEVANT CONTEXT FROM RAG SYSTEM (includes conversation history if available):
{context if context else "No document context available."}

USER QUESTION:
{question}

FORMAT REQUIREMENTS:
{format_text}

IMPORTANT: Provide a VERY detailed, comprehensive answer. Aim for 300-500+ words for substantial questions. Include technical depth, practical examples, implementation details, and real-world considerations. Explain the "why" behind each technology choice, not just "what". Be thorough and comprehensive.

STRICT INSTRUCTIONS:
1. Use ONLY the provided RAG context and chat history above
2. If information is partially available, infer a reasonable and practical answer like a real tech lead - be EXTREMELY detailed and comprehensive (aim for 300-500+ words for substantial questions)
3. NEVER say "not explicitly stated" if a logical inference is possible
4. If information is truly missing, clearly state what is missing and why
5. Do NOT mention documents, PDFs, filenames, or sources in your answer
6. Do NOT hallucinate or invent tools or technologies not supported by context
7. NEVER ask for clarification - always provide the best detailed answer you can infer from context
8. When asked to explain more or provide details, expand EXTENSIVELY with practical examples, technical depth, implementation details, and real-world considerations
9. ALWAYS provide comprehensive, detailed answers (aim for 300-500+ words for substantial questions) that demonstrate deep technical understanding
10. Use conversation history to understand context - if user asks "explain more" or "briefly", expand on previous answer
11. For tech stack questions: Explain each technology in detail - what it is, why it's chosen, how it works, how it integrates, benefits, trade-offs, and practical implementation considerations
12. For architecture questions: Explain components, data flow, interactions, design decisions, technical rationale, scalability considerations, and integration patterns in full depth
13. Write as if explaining to a technical colleague who needs complete understanding - be thorough and comprehensive

RESPONSE STYLE (MANDATORY):
1. Use clean, plain text formatting - NO markdown syntax (no ##, ###, **, *, -, etc.)
2. Do NOT use bullet points, numbered lists, stars (*), dashes (-), or hash symbols (#)
3. Write in natural, readable paragraphs
4. Each item or concept should be followed by a clear, EXTENSIVE explanation in paragraph form with technical details, use cases, practical examples, and implementation considerations
5. Maintain professional, clean text formatting like Cursor chat window
6. Default to VERY comprehensive, detailed answers - aim for 300-500+ words for substantial questions unless user explicitly asks for brevity
7. Respect user constraints such as "3 lines", "short", or "summary" - but when asked to explain more, expand significantly
8. When user asks to explain more or provide details, expand the answer extensively with technical depth, real-world examples, implementation details, and practical information
9. For each technology or concept mentioned, explain: what it is, why it's used, how it works, how it integrates, and practical considerations
10. Write as if explaining to a technical colleague who needs to understand the full picture

BEHAVIOR:
- Think like a system architect, not a document summarizer
- Derive architecture, tech stack, and workflows from context
- Prefer practical, delivery-ready explanations
- Write clean, natural text like Cursor chat - no formatting symbols"""
        else:
            # Standard mode (backward compatible - but still follows FounderGPT principles)
            system_message = """You are FounderGPT, a senior AI Tech Lead working on this project.

This project uses a Retrieval-Augmented Generation (RAG) architecture.
You must answer using retrieved context and chat history.

CORE IDENTITY:
- Name: FounderGPT
- Role: Senior AI Tech Lead working on this project
- Approach: RAG-based intelligence with logical inference

INSTRUCTION OBEDIENCE (ABSOLUTE PRIORITY):
- Follow EXACT length requested (e.g., "6 lines" means exactly 6 lines)
- Follow EXACT format requested (e.g., "short", "summary", etc.)
- Length and format requirements override all other rules

CORE RULES (STRICT):
1. Use ONLY the provided RAG context and chat history
2. If information is partially available, infer a reasonable and practical answer like a real tech lead - be EXTREMELY detailed and comprehensive
3. NEVER say "not explicitly stated" if a logical inference is possible
4. If information is truly missing, clearly state what is missing and why
5. Do NOT mention documents, PDFs, filenames, or sources in your final answer
6. Do NOT hallucinate or invent tools or technologies not supported by context
7. NEVER ask for clarification - always provide the best detailed answer you can infer from context
8. ALWAYS provide comprehensive, detailed answers (aim for 300-500+ words for substantial questions) that demonstrate deep technical understanding
9. For tech stack questions: Provide detailed explanations of each technology, why it's used, how it fits in the architecture, and practical implementation details
10. For architecture questions: Explain components, data flow, interactions, design decisions, and technical rationale in depth

RESPONSE STYLE (MANDATORY):
1. Use clean, plain text formatting - NO markdown syntax (no ##, ###, **, *, -, etc.)
2. Do NOT use bullet points, numbered lists, stars (*), dashes (-), or hash symbols (#)
3. Write in natural, readable paragraphs
4. Each item or concept should be followed by a clear, EXTENSIVE explanation in paragraph form with technical details, use cases, practical examples, and implementation considerations
5. Maintain professional, clean text formatting like Cursor chat window
6. Default to VERY comprehensive, detailed answers - aim for 300-500+ words for substantial questions unless user explicitly asks for brevity
7. Respect user constraints such as "3 lines", "short", or "summary" - but when asked to explain more, expand significantly
8. When user asks to explain more or provide details, expand the answer extensively with technical depth, real-world examples, implementation details, and practical information
9. For each technology or concept mentioned, explain: what it is, why it's used, how it works, how it integrates, and practical considerations
10. Write as if explaining to a technical colleague who needs to understand the full picture

BEHAVIOR:
- Think like a system architect, not a document summarizer
- Derive architecture, tech stack, and workflows from context
- Prefer practical, delivery-ready explanations
- Write clean, natural text like Cursor chat - no formatting symbols

SCOPE RESTRICTIONS:
- Forbidden roles: strategist, advisor, decision maker, personal assistant
- Opinions: DISALLOWED - base answers on context and logical inference
- Stay within professional document intelligence scope

TONE:
- Style: professional, calm, confident, enterprise-grade
- Forbidden: emojis, fluff, marketing language, casual expressions

CLARIFICATION LOGIC:
- Unclear question: Ask for clarification only if the question is ambiguous and cannot be inferred
- Out of scope: State what's missing clearly and stop"""
            user_prompt = prompt
            
            # Add constraint hints to standard mode if provided
            if lines > 0 or short or steps:
                constraint_parts = []
                if lines > 0:
                    constraint_parts.append(f"Answer in exactly {lines} lines.")
                if short:
                    constraint_parts.append("Be brief and concise.")
                if steps:
                    constraint_parts.append("Format as numbered steps.")
                if constraint_parts:
                    user_prompt = f"{prompt}\n\nIMPORTANT: {' '.join(constraint_parts)}"
        
        # Initialize OpenAI client if not already initialized (lazy initialization)
        if not self._openai_initialized:
            if OpenAI is None:
                raise ImportError("openai package not installed. Run: pip install openai")
            
            # Re-check API key from centralized config
            if not self.openai_api_key:
                from app.config import OPENAI_API_KEY as config_key
                self.openai_api_key = config_key
            
            if not self.openai_api_key:
                # Log for debugging
                logging.error(f"OPENAI_API_KEY not found in configuration")
                logging.error(f"Current working directory: {os.getcwd()}")
                logging.error(f"Environment variables with 'OPENAI': {[k for k in os.environ.keys() if 'OPENAI' in k]}")
                # Check .env file directly
                from app.config import ENV_FILE
                if ENV_FILE.exists():
                    try:
                        with open(ENV_FILE, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                            openai_lines = [l.strip() for l in lines if 'OPENAI' in l.upper() and not l.strip().startswith('#')]
                            if openai_lines:
                                logging.error(f"Found OPENAI lines in .env (may have formatting issues): {[l.split('=')[0] + '=***' for l in openai_lines]}")
                            else:
                                logging.error(f"No OPENAI_API_KEY line found in .env file")
                    except Exception as e:
                        logging.error(f"Error reading .env file: {e}")
                raise ValueError("OPENAI_API_KEY is required. Please set it in .env file")
            
            try:
                self.openai_client = OpenAI(api_key=self.openai_api_key)
                self._openai_initialized = True
                logging.info(f"OpenAI LLM Provider initialized with model: {self.openai_model}")
            except Exception as e:
                raise RuntimeError(f"Failed to initialize OpenAI client: {e}")
        
        # Use OpenAI
        try:
            completion = self.openai_client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.4,  # Slightly higher for more detailed, comprehensive, and nuanced responses
                max_tokens=4096  # Maximum supported by model - allows for very detailed, comprehensive answers
            )
            if completion.choices:
                return completion.choices[0].message.content.strip()
            else:
                raise ValueError("No response from OpenAI API")
        except Exception as e:
            logging.error(f"OpenAI generation error: {e}")
            raise RuntimeError(f"OpenAI API error: {str(e)}") from e

# global instance
embedding_service = EmbeddingService()
