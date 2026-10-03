@echo off
title SatQuery AI Launcher
echo ========================================================
echo            Starting SatQuery AI Platform
echo ========================================================
echo.

cd /d %~dp0

echo [1/2] Launching Backend FastAPI Server (Port 8000)...
start "SatQuery AI - Backend" cmd /k "cd /d "%~dp0" && .\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000"

timeout /t 3 /nobreak >nul

echo [2/2] Launching Frontend Web Workstation (Port 5173)...
start "SatQuery AI - Frontend" cmd /k "cd /d "%~dp0\frontend" && npm.cmd run dev"

timeout /t 3 /nobreak >nul

echo.
echo ========================================================
echo SatQuery AI is running:
echo   - Web UI:     http://localhost:5173
echo   - API Docs:   http://127.0.0.1:8000/docs
echo   - Health:     http://127.0.0.1:8000/api/health
echo ========================================================
echo.
start http://localhost:5173
