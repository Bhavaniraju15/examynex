@echo off
echo ========================================
echo ExamyNex Backend Quick Start
echo ========================================
echo.

:: Check if virtual environment exists
if not exist "#\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv #
)

:: Activate virtual environment
echo Activating virtual environment...
call #\Scripts\activate.bat

:: Install dependencies
echo Installing dependencies...
pip install -r requirments.txt

:: Start the server
echo.
echo ========================================
echo Starting FastAPI server...
echo Backend will be available at:
echo http://localhost:8000
echo ========================================
echo.
echo Press Ctrl+C to stop the server
echo.

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
