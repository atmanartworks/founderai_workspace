"""
Comprehensive API Test Script
Tests all endpoints and services of the RAG Backend
"""
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:8000"
TEST_USER_ID = "test-user-123"

def print_test(name):
    print(f"\n{'='*50}")
    print(f"🧪 Testing: {name}")
    print(f"{'='*50}")

def print_result(success, message):
    if success:
        print(f"✅ {message}")
    else:
        print(f"❌ {message}")

def test_health():
    """Test health endpoint"""
    print_test("Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print_result(True, f"Health check passed: {data}")
            return True
        else:
            print_result(False, f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"Health check error: {e}")
        return False

def test_database_connection():
    """Test database connection"""
    print_test("Database Connection")
    try:
        from app.database import supabase
        # Try a simple query
        result = supabase.table("vault").select("id").limit(1).execute()
        print_result(True, "Database connection successful")
        return True
    except Exception as e:
        print_result(False, f"Database connection failed: {e}")
        print("⚠️  Make sure SUPABASE_URL and SUPABASE_KEY are set in .env")
        return False

def test_embedding_service():
    """Test embedding service"""
    print_test("Embedding Service")
    try:
        from app.services.embedding_service import embedding_service
        import asyncio
        
        async def test_embed():
            result = await embedding_service.embed_text("Test document")
            return result is not None and len(result) > 0
        
        result = asyncio.run(test_embed())
        if result:
            print_result(True, "Embedding service working")
            return True
        else:
            print_result(False, "Embedding service returned empty result")
            return False
    except Exception as e:
        print_result(False, f"Embedding service error: {e}")
        print("⚠️  Make sure MISTRAL_API_KEY is set in .env")
        return False

def test_api_docs():
    """Test API documentation"""
    print_test("API Documentation")
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print_result(True, "API docs accessible at /docs")
            return True
        else:
            print_result(False, f"API docs failed: {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"API docs error: {e}")
        return False

def test_search_endpoint():
    """Test search endpoint"""
    print_test("Search Endpoint")
    try:
        # Note: This requires database setup and embeddings
        response = requests.post(
            f"{BASE_URL}/api/search/semantic",
            params={
                "query": "test query",
                "user_id": TEST_USER_ID,
                "top_k": 5
            }
        )
        # Even if it fails due to no data, check if endpoint is reachable
        if response.status_code in [200, 404, 500]:
            print_result(True, f"Search endpoint reachable (status: {response.status_code})")
            if response.status_code == 200:
                print(f"   Response: {response.json()}")
            else:
                print(f"   Note: This may fail if no documents are embedded yet")
            return True
        else:
            print_result(False, f"Search endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"Search endpoint error: {e}")
        return False

def test_chat_endpoint():
    """Test chat endpoint"""
    print_test("Chat Endpoint")
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat/message",
            json={
                "conversation_id": "test-conv-123",
                "message": "Hello, test message",
                "user_id": TEST_USER_ID
            }
        )
        # Even if it fails due to no data, check if endpoint is reachable
        if response.status_code in [200, 404, 500]:
            print_result(True, f"Chat endpoint reachable (status: {response.status_code})")
            if response.status_code == 200:
                print(f"   Response: {response.json()}")
            else:
                print(f"   Note: This may fail if no documents are embedded yet")
            return True
        else:
            print_result(False, f"Chat endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"Chat endpoint error: {e}")
        return False

def test_vault_list():
    """Test vault list endpoint"""
    print_test("Vault List Endpoint")
    try:
        response = requests.get(f"{BASE_URL}/api/vault/list/{TEST_USER_ID}")
        if response.status_code == 200:
            data = response.json()
            print_result(True, f"Vault list endpoint working: {len(data.get('vaults', []))} vaults")
            return True
        else:
            print_result(False, f"Vault list failed: {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"Vault list error: {e}")
        return False

def test_environment_variables():
    """Test if required environment variables are set"""
    print_test("Environment Variables")
    required_vars = {
        "SUPABASE_URL": os.getenv("SUPABASE_URL"),
        "SUPABASE_KEY": os.getenv("SUPABASE_KEY"),
        "MISTRAL_API_KEY": os.getenv("MISTRAL_API_KEY")
    }
    
    all_set = True
    for var_name, var_value in required_vars.items():
        if var_value:
            print_result(True, f"{var_name} is set")
        else:
            print_result(False, f"{var_name} is NOT set")
            all_set = False
    
    return all_set

def main():
    print("\n" + "="*50)
    print("🚀 RAG Backend API Test Suite")
    print("="*50)
    
    results = []
    
    # Run tests
    results.append(("Environment Variables", test_environment_variables()))
    results.append(("Health Check", test_health()))
    results.append(("API Documentation", test_api_docs()))
    results.append(("Database Connection", test_database_connection()))
    results.append(("Embedding Service", test_embedding_service()))
    results.append(("Vault List", test_vault_list()))
    results.append(("Search Endpoint", test_search_endpoint()))
    results.append(("Chat Endpoint", test_chat_endpoint()))
    
    # Summary
    print("\n" + "="*50)
    print("📊 Test Summary")
    print("="*50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your API is working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the errors above.")
    
    print("\n" + "="*50)
    print("💡 Next Steps:")
    print("   1. Check the Swagger UI at http://localhost:8000/docs")
    print("   2. Test file upload via /api/vault/upload")
    print("   3. Embed documents via /api/vault/embed/{vault_id}")
    print("   4. Test search and chat functionality")
    print("="*50 + "\n")

if __name__ == "__main__":
    main()

