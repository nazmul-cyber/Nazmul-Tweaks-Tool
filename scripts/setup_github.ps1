# Initialize git repo and prepare for GitHub push
param([string]$RepoUrl = "https://github.com/nazmul-cyber/Nazmul-Tweaks-Tool.git")

$root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
Set-Location $root

if (-not (Test-Path ".git")) {
    git init
    git branch -M main
}

git add .
git status

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Create repo on GitHub: nazmul-cyber/Nazmul-Tweaks-Tool"
Write-Host "  2. Run: git remote add origin $RepoUrl"
Write-Host "  3. Run: git commit -m `"Initial release - Nazmul Tweaks Tool`""
Write-Host "  4. Run: git push -u origin main"
Write-Host "  5. Build EXE: double-click BUILD_NOW.vbs"
Write-Host "  6. GitHub Releases -> upload release\Nazmul-Tweaks-Tool.exe"
Write-Host ""