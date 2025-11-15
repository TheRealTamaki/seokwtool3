@echo off
REM Google PAA Scraper - Web Server Startup Script (Windows)

setlocal enabledelayedexpansion

echo.
echo 4 Google PAA Scraper - Web Interface
echo ======================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Clean up old virtual environment to ensure fresh install
if exist "venv" (
    echo Removing old virtual environment...
    rmdir /s /q venv
)

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update dependencies
echo Installing dependencies...
pip install -q -r requirements.txt

REM Check for .env file
if not exist ".env" (
    echo.
    echo ^! No .env file found!
    echo Please create a .env file with your Firecrawl API key:
    echo.
    echo     echo FIRECRAWL_API_KEY=your_key_here ^> .env
    echo.
    echo You can get a free API key from: https://firecrawl.dev
    echo.
)

REM Start the Flask app
echo.
echo Starting web server...
echo Open your browser and go to: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py

endlocal
pause
