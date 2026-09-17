# Social AI Studio: 1-Click Launch Script
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  SOCIAL AI STUDIO - 100% FREE AUTOMATION ENGINE" -ForegroundColor Cyan
Write-Host "  Profile: Muhammad Haroon" -ForegroundColor White
Write-Host "  FastAPI + Local Ollama + SQLite + Flutter" -ForegroundColor White
Write-Host "========================================================" -ForegroundColor Cyan

# 1. Check Ollama
Write-Host "`n[1/3] Checking Local Ollama AI Engine..." -ForegroundColor Yellow
try {
    $models = (Get-Command ollama -ErrorAction Stop)
    Write-Host "[OK] Ollama is installed and ready." -ForegroundColor Green
} catch {
    Write-Host "[WARNING] Please ensure Ollama is running from your system tray." -ForegroundColor DarkYellow
}

# 2. Launch FastAPI Backend
Write-Host "`n[2/3] Starting FastAPI Backend on http://localhost:8000..." -ForegroundColor Yellow
$backendPath = Join-Path $PSScriptRoot "backend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendPath'; .\.venv\Scripts\Activate.ps1; uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

Start-Sleep -Seconds 3

# 3. Launch Flutter App in Chrome
Write-Host "`n[3/3] Launching Flutter Application in Chrome / Browser..." -ForegroundColor Yellow
$mobilePath = Join-Path $PSScriptRoot "mobile_app"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$mobilePath'; flutter run -d chrome --web-port 3000"

Write-Host "`n========================================================" -ForegroundColor Green
Write-Host "  ALL SYSTEMS RUNNING!" -ForegroundColor Green
Write-Host "  - App UI: http://localhost:3000" -ForegroundColor White
Write-Host "  - Backend Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "  - Profile Linked: Muhammad Haroon" -ForegroundColor White
Write-Host "  - Master Auto-Posting: ACTIVE (24/7)" -ForegroundColor White
Write-Host "========================================================" -ForegroundColor Green
