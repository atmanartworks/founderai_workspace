import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class GroqService:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set")
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.1-8b-instant"  # Fast and free model (replacement for decommissioned llama3-8b-8192)
    
    def generate_answer(self, context: str, question: str) -> str:
        if not context or not question:
            raise ValueError("Context and question cannot be empty")
        
        prompt = f"""You are a helpful assistant that answers questions based on the provided document context.

Context from documents:
{context}

User Question: {question}

Instructions:
- Answer the question using information from the context above
- Be thorough and helpful in your explanation
- If the context contains relevant information, provide a detailed answer
- If the context doesn't contain enough information to fully answer the question, say what you can based on the context, then mention that more information may be needed
- Only say "The document does not contain this information" if the context is completely unrelated to the question

Answer:"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0
            )
            
            if not response.choices or not response.choices[0].message.content:
                raise ValueError("Empty response from Groq API")
            
            return response.choices[0].message.content
        except Exception as e:
            error_msg = f"Groq API error: {str(e)}"
            print(f"GroqService error: {error_msg}")
            raise RuntimeError(error_msg) from e

# Singleton
groq_service = GroqService()
