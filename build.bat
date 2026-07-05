@echo off
echo ==============================================
echo Starting AI Secure Review Build & Packaging
echo ==============================================

REM Check if virtual environment exists and activate it
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

REM Run python package builder script
python build_package.py

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Build failed!
    exit /b %ERRORLEVEL%
)

echo ==============================================
echo Build Completed Successfully!
echo ==============================================
