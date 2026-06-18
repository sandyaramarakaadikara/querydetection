@echo off
title SQL Query Compiler & Security Analyzer Launcher
echo ==========================================================
echo   SQL Query Compiler & Security Analyzer Launcher
echo ==========================================================
echo.
echo [1/2] Starting Backend API on http://localhost:8001...
start "SQL Analyzer - Backend API (Port 8001)" cmd /k "cd /d "%~dp0backend" && python -m uvicorn main:app --host 0.0.0.0 --port 8001"

echo [2/2] Starting Frontend App on http://localhost:3000...
start "SQL Analyzer - Frontend React (Port 3000)" cmd /k "cd /d "%~dp0frontend" && npm run dev"
echo.
echo ==========================================================
echo Both servers are starting in separate windows.
echo - Backend API: http://localhost:8001
echo - Frontend App: http://localhost:3000
echo.
echo You can check the logs in each window.
echo If any server fails to start, its window will stay open.
echo ==========================================================
echo.
pause
