@echo off
REM PrintPrep launcher for Windows. Double-click to start the app.
REM Drops back to the venv's `printprep app` (native window) or `printprep serve` (browser tab).

setlocal
cd /d "%~dp0"

set "VENV_PY=%~dp0venv\Scripts\python.exe"
set "VENV_PP=%~dp0venv\Scripts\printprep.exe"

if not exist "%VENV_PP%" (
    echo PrintPrep venv not found at %~dp0venv\Scripts\.
    echo Run: pip install -e ".[web,desktop]"
    pause
    exit /b 1
)

"%VENV_PY%" -c "import webview" >NUL 2>&1
if %ERRORLEVEL%==0 (
    "%VENV_PP%" app
    exit /b %ERRORLEVEL%
)

REM Fallback: serve + open default browser.
start "" http://127.0.0.1:8000
"%VENV_PP%" serve --host 127.0.0.1 --port 8000
