import asyncio
from app.services.embedding_service import embedding_service

async def test_service():
    print("🔹 Testing text embedding...")
    emb = await embedding_service.embed_text("This is a test sentence for embedding.")
    print(f"✅ Embedding vector length: {len(emb)}")

    print("\n🔹 Testing text generation...")
    response = await embedding_service.generate("Explain reinforcement learning briefly.")
    print(f"🤖 Response:\n{response}")

if __name__ == "__main__":
    asyncio.run(test_service())
