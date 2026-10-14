@echo off
rem Periyapuranam beta preview launcher.
rem Serves the repo root on http://localhost:8934 and opens the preview reader.
rem Run: double-click preview.bat  (or: preview.bat [port])
rem Stop: CTRL+C in this window.

cd /d %~dp0

set PORT=8934
if not "%~1"=="" set PORT=%~1

where python >nul 2>nul
if errorlevel 1 (
  echo Python was not found on PATH. Install Python 3 from https://www.python.org/downloads/
  pause
  exit /b 1
)

if not exist "site\preview.html" (
  echo site\preview.html not found. Rebuild it first with:
  echo   python scripts/build.py --preview ^&^& python scripts/make_preview.py
  pause
  exit /b 1
)

echo Serving Periyapuranam preview at http://localhost:%PORT%/site/preview.html
echo Product reader (TK):        http://localhost:%PORT%/site/periya_puranam_index.html
echo Press CTRL+C to stop the server.
start "" "http://localhost:%PORT%/site/preview.html"
python -m http.server %PORT%
