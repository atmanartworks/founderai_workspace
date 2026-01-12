# Pre-Deployment Verification Script
# Run this before pushing to GitHub and deploying to Vercel

Write-Host "Pre-Deployment Check" -ForegroundColor Cyan
Write-Host "========================`n" -ForegroundColor Cyan

$errors = @()
$warnings = @()

# 1. Check if build works
Write-Host "1. Testing build..." -ForegroundColor Yellow
try {
    npm run build 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   [OK] Build successful!" -ForegroundColor Green
    } else {
        $errors += "Build failed - fix errors before deploying"
        Write-Host "   [FAIL] Build failed!" -ForegroundColor Red
    }
} catch {
    $errors += "Could not run build command"
    Write-Host "   [FAIL] Build check failed!" -ForegroundColor Red
}

# 2. Check for .env files (should be ignored)
Write-Host "`n2. Checking for .env files..." -ForegroundColor Yellow
$envFiles = Get-ChildItem -Recurse -Filter ".env*" -File -ErrorAction SilentlyContinue | Where-Object { $_.FullName -notmatch "node_modules|\.venv|venv" }
if ($envFiles) {
    $warnings += "Found .env files - ensure they're in .gitignore"
        Write-Host "   WARNING: Found .env files (should be ignored by git):" -ForegroundColor Yellow
    $envFiles | ForEach-Object { Write-Host "      - $($_.FullName)" -ForegroundColor Gray }
} else {
    Write-Host "   [OK] No .env files found" -ForegroundColor Green
}

# 3. Check required files exist
Write-Host "`n3. Checking required files..." -ForegroundColor Yellow
$requiredFiles = @(
    "package.json",
    "vercel.json",
    "index.html",
    "vite.config.ts",
    ".gitignore"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "   [OK] $file" -ForegroundColor Green
    } else {
        $errors += "Missing required file: $file"
        Write-Host "   [FAIL] $file (MISSING)" -ForegroundColor Red
    }
}

# 4. Check git status
Write-Host "`n4. Checking git status..." -ForegroundColor Yellow
try {
    $gitStatus = git status --porcelain 2>&1
    if ($LASTEXITCODE -eq 0) {
        if ($gitStatus) {
            Write-Host "   WARNING: You have uncommitted changes:" -ForegroundColor Yellow
            $gitStatus | ForEach-Object { Write-Host "      $_" -ForegroundColor Gray }
        } else {
            Write-Host "   [OK] Working directory clean" -ForegroundColor Green
        }
    }
} catch {
    Write-Host "   WARNING: Could not check git status" -ForegroundColor Yellow
}

# 5. Check for large files
Write-Host "`n5. Checking for large files..." -ForegroundColor Yellow
$largeFiles = Get-ChildItem -Recurse -File -ErrorAction SilentlyContinue | Where-Object { 
    $_.Length -gt 50MB -and 
    $_.FullName -notmatch "node_modules|\.venv|venv|dist" 
}
if ($largeFiles) {
    $warnings += "Found large files - ensure they're in .gitignore"
    Write-Host "   WARNING: Large files found (>50MB):" -ForegroundColor Yellow
    $largeFiles | Select-Object -First 5 | ForEach-Object { 
        $sizeMB = [math]::Round($_.Length/1MB, 2)
        Write-Host "      - $($_.Name) ($sizeMB MB)" -ForegroundColor Gray 
    }
} else {
    Write-Host "   [OK] No large files found" -ForegroundColor Green
}

# 6. Check .gitignore
Write-Host "`n6. Verifying .gitignore..." -ForegroundColor Yellow
if (Test-Path ".gitignore") {
    $gitignoreContent = Get-Content ".gitignore" -Raw
    $requiredPatterns = @("node_modules", "dist", ".env", "venv", ".venv", "__pycache__")
    $missingPatterns = @()
    
    foreach ($pattern in $requiredPatterns) {
        if ($gitignoreContent -notmatch [regex]::Escape($pattern)) {
            $missingPatterns += $pattern
        }
    }
    
    if ($missingPatterns.Count -eq 0) {
        Write-Host "   [OK] .gitignore looks good" -ForegroundColor Green
    } else {
        $warnings += "Some recommended patterns missing from .gitignore"
        Write-Host "   WARNING: Missing patterns: $($missingPatterns -join ', ')" -ForegroundColor Yellow
    }
} else {
    $errors += ".gitignore file missing"
    Write-Host "   [FAIL] .gitignore not found" -ForegroundColor Red
}

# Summary
Write-Host "`n========================`n" -ForegroundColor Cyan
Write-Host "Summary" -ForegroundColor Cyan
Write-Host "========================`n" -ForegroundColor Cyan

if ($errors.Count -eq 0 -and $warnings.Count -eq 0) {
    Write-Host "[SUCCESS] All checks passed! Ready to deploy." -ForegroundColor Green
    Write-Host "`nNext steps:" -ForegroundColor Cyan
    Write-Host "1. git add ." -ForegroundColor White
    Write-Host "2. git commit -m 'Ready for deployment'" -ForegroundColor White
    Write-Host "3. git push origin main" -ForegroundColor White
    Write-Host "4. Deploy to Vercel (see DEPLOYMENT_GUIDE.md)" -ForegroundColor White
    exit 0
} else {
    if ($errors.Count -gt 0) {
        Write-Host "[ERROR] Errors found ($($errors.Count)):" -ForegroundColor Red
        $errors | ForEach-Object { Write-Host "   - $_" -ForegroundColor Red }
    }
    if ($warnings.Count -gt 0) {
        Write-Host "`nWARNINGS ($($warnings.Count)):" -ForegroundColor Yellow
        $warnings | ForEach-Object { Write-Host "   - $_" -ForegroundColor Yellow }
    }
    Write-Host "`nWARNING: Please fix errors before deploying!" -ForegroundColor Yellow
    exit 1
}
