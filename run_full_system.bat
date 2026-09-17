@echo off
title Social AI Studio - Launching System
color 0b

echo ========================================================
echo   SOCIAL AI STUDIO - 100%% FREE AUTOMATION ENGINE
echo   Profile: Muhammad Haroon
echo   FastAPI + Local Ollama (llama3.2) + SQLite + Flutter
echo ========================================================
echo.

echo [1/3] Checking Ollama Local AI Engine...
ollama list >nul 2>&1
if %errorlevel% neq 0 (
    echo Starting Ollama service...
    start /b ollama serve
    timeout /t 3 >nul
)
echo [OK] Ollama is active.

echo.
echo [2/3] Checking and Starting FastAPI Backend Server...
cd /d "%~dp0backend"
start "Social AI Backend (FastAPI)" cmd /k ".\.venv\Scripts\activate.bat && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
timeout /t 3 >nul

echo.
echo [3/3] Launching App in Chrome / Web Browser...
cd /d "%~dp0mobile_app"
start "Social AI Mobile App" cmd /k "flutter run -d chrome --web-port 3000"

echo.
echo ========================================================
echo   SYSTEM IS LIVE!
echo   - App UI: http://localhost:3000
echo   - Backend API Docs: http://localhost:8000/docs
echo   - Connected Profile: Muhammad Haroon
echo   - Master Automatic Mode: ON (24/7)
echo ========================================================
pause
