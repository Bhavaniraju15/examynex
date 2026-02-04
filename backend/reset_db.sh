#!/bin/bash

echo ""
echo "==================================="
echo "Examynex - Database Reset Script"
echo "==================================="
echo ""

# Check if exam.db exists
if [ -f exam.db ]; then
    echo "Deleting existing database..."
    rm exam.db
    echo "Database deleted."
else
    echo "No existing database found."
fi

echo ""
echo "Reinitializing database with fresh schema..."
echo "Running: python -c \"from app.database import Base, engine; Base.metadata.create_all(bind=engine)\""
echo ""

python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"

if [ $? -eq 0 ]; then
    echo ""
    echo "==================================="
    echo "Database reset successful!"
    echo "==================================="
    echo "You can now start the server with:"
    echo "  uvicorn app.main:app --reload"
else
    echo ""
    echo "ERROR: Database reset failed!"
    echo "Make sure you are in the backend directory with venv activated."
fi

echo ""
