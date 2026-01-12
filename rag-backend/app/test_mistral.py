import os
from dotenv import load_dotenv
from mistralai import Mistral

load_dotenv()

api_key = os.getenv("MISTRAL_API_KEY")
client = Mistral(api_key=api_key)

# Test embedding
response = client.embeddings.create(
    model="mistral-embed",
    inputs=["Test document chunk"]
)

print(f"✅ Embedding dimension: {len(response.data[0].embedding)}")
print("✅ Mistral is connected successfully!")
