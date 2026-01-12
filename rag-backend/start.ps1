# FastAPI Server Startup Script
# Run this script from the rag-backend directory

Write-Host "🚀 Starting RAG Backend Server..." -ForegroundColor Green

# Determine venv path (check both .venv and venv)
$venvPath = if (Test-Path ".venv\Scripts\python.exe") { ".venv" } elseif (Test-Path "venv\Scripts\python.exe") { "venv" } else { $null }

if (-not $venvPath) {
    Write-Host "❌ Virtual environment not found! Please run: python -m venv venv" -ForegroundColor Red
    exit 1
}

$pythonExe = "$venvPath\Scripts\python.exe"
$pipExe = "$venvPath\Scripts\pip.exe"

# Check if requirements are installed
Write-Host "🔍 Checking dependencies..." -ForegroundColor Yellow
& $pythonExe -c "import fastapi" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Dependencies not installed. Installing..." -ForegroundColor Yellow
    & $pipExe install -r requirements.txt
}

# Start the server using venv's Python directly
Write-Host "🌐 Starting server on http://localhost:8000" -ForegroundColor Green
Write-Host "📚 API docs available at http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "🛑 Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Set environment variables to ensure subprocesses use venv Python
$venvPythonPath = (Resolve-Path "$venvPath\Scripts\python.exe").Path
$env:PYTHONPATH = "$PWD;$env:PYTHONPATH"
$env:PYTHONEXECUTABLE = $venvPythonPath

# Use venv's Python directly to ensure correct interpreter
& $pythonExe -m uvicorn app.main:app --reload

