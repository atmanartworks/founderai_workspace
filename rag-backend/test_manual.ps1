# Manual API Testing Script
# Run this while the server is running

$BASE_URL = "http://localhost:8000"
$USER_ID = "test-user-123"

Write-Host "🧪 Testing RAG Backend API" -ForegroundColor Green
Write-Host ""

# Test 1: Health Check
Write-Host "1️⃣  Testing Health Endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/health" -Method Get
    Write-Host "   ✅ Health: $($response.status)" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Health check failed: $_" -ForegroundColor Red
}

# Test 2: List Vaults
Write-Host "2️⃣  Testing Vault List..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/api/vault/list/$USER_ID" -Method Get
    Write-Host "   ✅ Vault List: $($response.vaults.Count) vaults found" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  Vault List: $_" -ForegroundColor Yellow
    Write-Host "      (This is normal if no vaults exist yet)" -ForegroundColor Gray
}

# Test 3: Search
Write-Host "3️⃣  Testing Search Endpoint..." -ForegroundColor Yellow
try {
    $body = @{
        query = "test query"
        user_id = $USER_ID
        top_k = 5
    }
    $response = Invoke-RestMethod -Uri "$BASE_URL/api/search/semantic" -Method Post -Body $body
    Write-Host "   ✅ Search: Working" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  Search: $_" -ForegroundColor Yellow
    Write-Host "      (This is normal if no documents are embedded yet)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "💡 For full interactive testing, visit:" -ForegroundColor Cyan
Write-Host "   http://localhost:8000/docs" -ForegroundColor White
Write-Host ""

