@echo off
setlocal
cd /d "%~dp0backend"
where python >nul 2>&1
if errorlevel 1 (
  echo Python 3.11+ is required. Install Python from python.org then retry.
  pause
  exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
  python -m venv .venv
  if errorlevel 1 exit /b 1
)
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
  echo Dependency installation failed.
  pause
  exit /b 1
)
set FRAMEFORGE_LOCAL_DEMO=1
echo.
echo VALCIER FRAMEFORGE LOCAL DEMO
 echo Open http://127.0.0.1:8000 in your browser
 echo Press Ctrl+C to stop the server.
 echo.
".venv\Scripts\python.exe" -m uvicorn frameforge.api:app --host 127.0.0.1 --port 8000
pause
