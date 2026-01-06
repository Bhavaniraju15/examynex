@echo off

:: 1. Try standard python (check version to see if it's the real one or the Store shim)
python --version >nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    SET "PYTHON_CMD=python"
    GOTO :FOUND
)

:: 2. Try common Miniconda/Anaconda paths
IF EXIST "%USERPROFILE%\miniconda3\python.exe" (
    SET "PYTHON_CMD=%USERPROFILE%\miniconda3\python.exe"
    echo Autosetup: Found Miniconda in User Profile.
    GOTO :FOUND
)

IF EXIST "%USERPROFILE%\anaconda3\python.exe" (
    SET "PYTHON_CMD=%USERPROFILE%\anaconda3\python.exe"
    echo Autosetup: Found Anaconda in User Profile.
    GOTO :FOUND
)

:: 3. Fallback: Ask User
echo.
echo ========================================================
echo  Could not find a working Python installation automatically.
echo  (The system 'python' command seems to be the Store shim)
echo ========================================================
echo.
echo Please locate your 'python.exe' and copy its full path.
echo Example: C:\Users\shanm\miniconda3\python.exe
echo.
set /p USER_PYTHON=Paste Python Path: 

IF EXIST "%USER_PYTHON%" (
    SET "PYTHON_CMD=%USER_PYTHON%"
    GOTO :FOUND
) ELSE (
    echo.
    echo Error: The file "%USER_PYTHON%" was not found.
    pause
    exit /b
)

:FOUND
echo.
echo --------------------------------------------------------
echo  Using Python: "%PYTHON_CMD%"
echo --------------------------------------------------------
echo.

echo [1/2] Installing dependencies...
"%PYTHON_CMD%" -m pip install -r requirements.txt
IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo [WARNING] Dependency installation had errors.
    echo Continuing anyway...
)

echo.
echo [2/2] Starting Backend Server...
echo --------------------------------------------------------
"%PYTHON_CMD%" -m uvicorn app.main:app --reload

pause
