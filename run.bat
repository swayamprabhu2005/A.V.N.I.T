@echo off
setlocal enabledelayedexpansion
title A.V.N.I.T. Master Launcher

cd /d "%~dp0"

echo ========================================================================
echo       A.V.N.I.T. - Automated Vehicle Identity & Tampering Detection
echo ========================================================================
echo.

echo [1/4] Checking Python environment...
if exist "venv\Scripts\activate.bat" (
    echo [INFO] Activating local virtual environment (venv)...
    call "venv\Scripts\activate.bat"
) else (
    echo [INFO] Using system Python runtime.
)

set "PYTHONPATH=%~dp0"

echo.
echo [2/4] Checking Frontend dependencies...
if not exist "frontend\node_modules" (
    echo [INFO] Installing frontend node packages...
    cd frontend
    call npm install
    cd ..
) else (
    echo [INFO] Frontend packages verified.
)

echo.
echo [3/4] Launching FastAPI Backend Server (Port 8000)...
start "AVNIT - Backend Server (Port 8000)" cmd /k "title AVNIT Backend (Port 8000) ^& cd /d "%~dp0" ^& set "PYTHONPATH=%~dp0" ^& python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload"

echo.
echo [4/4] Launching Vue 3 + Vite Frontend Dashboard (Port 5173)...
start "AVNIT - Frontend Dashboard (Port 5173)" cmd /k "title AVNIT Frontend (Port 5173) ^& cd /d "%~dp0\frontend" ^& npm run dev"

echo.
echo Waiting for services to initialize...
timeout /t 4 /nobreak >nul

echo.
echo Opening A.V.N.I.T. Dashboard in your default web browser...
start http://localhost:5173

echo.
echo ========================================================================
echo   All A.V.N.I.T. systems are active and running:
echo.
echo   - Frontend Dashboard:   http://localhost:5173
echo   - Backend API:          http://localhost:8000
echo   - Interactive API Docs: http://localhost:8000/docs
echo.
echo   To stop all services, close the respective Backend & Frontend windows.
echo ========================================================================
echo.
pause
