@echo off
echo.
echo ===================================
echo Examynex - Database Reset Script
echo ===================================
echo.

REM Check if exam.db exists
if exist exam.db (
    echo Deleting existing database...
    del exam.db
    echo Database deleted.
) else (
    echo No existing database found.
)

echo.
echo Reinitializing database with fresh schema...
echo Running: python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"
echo.

python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"

if %errorlevel% equ 0 (
    echo.
    echo ===================================
    echo Database reset successful!
    echo ===================================
    echo You can now start the server with:
    echo   uvicorn app.main:app --reload
) else (
    echo.
    echo ERROR: Database reset failed!
    echo Make sure you are in the backend directory with venv activated.
)

echo.
pause
