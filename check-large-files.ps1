# PowerShell script to check for large files before pushing to GitHub
# GitHub has a 100MB file size limit

Write-Host "Checking for large files (>50MB)..." -ForegroundColor Cyan

$largeFiles = Get-ChildItem -Recurse -File | Where-Object { $_.Length -gt 50MB } | Select-Object FullName, @{Name="Size(MB)";Expression={[math]::Round($_.Length/1MB,2)}}

if ($largeFiles) {
    Write-Host "`n⚠️  Large files found (>50MB):" -ForegroundColor Yellow
    $largeFiles | Format-Table -AutoSize
    
    Write-Host "`n⚠️  WARNING: Files over 100MB cannot be pushed to GitHub!" -ForegroundColor Red
    Write-Host "Make sure these files are in .gitignore" -ForegroundColor Yellow
    
    # Check if files are in .gitignore
    $gitignoreContent = Get-Content .gitignore -Raw -ErrorAction SilentlyContinue
    if ($gitignoreContent) {
        Write-Host "`nChecking .gitignore..." -ForegroundColor Cyan
        foreach ($file in $largeFiles) {
            $relativePath = $file.FullName.Replace((Get-Location).Path + "\", "").Replace("\", "/")
            if ($gitignoreContent -match [regex]::Escape($relativePath)) {
                Write-Host "✅ $relativePath is in .gitignore" -ForegroundColor Green
            } else {
                Write-Host "❌ $relativePath is NOT in .gitignore" -ForegroundColor Red
            }
        }
    }
} else {
    Write-Host "✅ No large files found!" -ForegroundColor Green
}

Write-Host "`nChecking git-tracked files..." -ForegroundColor Cyan
$trackedLarge = git ls-files | ForEach-Object { 
    $item = Get-Item $_ -ErrorAction SilentlyContinue
    if ($item -and $item.Length -gt 50MB) {
        [PSCustomObject]@{
            File = $_
            "Size(MB)" = [math]::Round($item.Length/1MB,2)
        }
    }
}

if ($trackedLarge) {
    Write-Host "`n⚠️  Large files tracked by git:" -ForegroundColor Yellow
    $trackedLarge | Format-Table -AutoSize
    Write-Host "`nTo remove from git: git rm --cached <file>" -ForegroundColor Yellow
} else {
    Write-Host "✅ No large files tracked by git!" -ForegroundColor Green
}

Write-Host "`nDone!" -ForegroundColor Cyan
