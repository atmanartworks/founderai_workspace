import asyncio
from app.services.embedding_service import embedding_service

async def test():
    print("\n🔹 Testing generation with DeepSeek...\n")
    response = await embedding_service.generate("Explain RAG in one simple line.")
    print("Response:\n", response)

asyncio.run(test())
