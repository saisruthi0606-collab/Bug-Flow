@echo off
SET "ROOT=%~dp0"
SET "VENV=%ROOT%\.venv\Scripts\activate.bat"
IF NOT EXIST "%VENV%" (
  echo Virtual environment not found at %VENV%
  exit /b 1
)
call "%VENV%"
start "Backend" cmd /k "cd /d "%ROOT%\backend" && uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000"
start "Frontend" cmd /k "cd /d "%ROOT%\frontend" && npm run dev -- --host 0.0.0.0 --port 3000"
start "BugFlow" "http://localhost:3000"
pause