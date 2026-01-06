# How to Run Examynex

The project has been updated with correct dependencies and a fix for the frontend token issue.

## Prerequisites

1.  **Install Python**: You need Python 3.10 or higher.
    - Download from [python.org](https://www.python.org/downloads/).
    - **IMPORTANT**: During installation, check the box **"Add Python to PATH"**.

## Setup Instructions

1.  **Open Command Prompt** or PowerShell in this folder (`c:\Users\shanm\Downloads\examynex-main\examynex-main`).

2.  **Install Dependencies**:
    Run the following command to install the required libraries:
    ```sh
    pip install -r backend/requirements.txt
    ```
    *Note: If `pip` is not recognized, try `python -m pip install -r backend/requirements.txt`.*

3.  **Run the Backend**:
    
    **Option A: Automatic (Recommended)**
    - Go to the `backend` folder.
    - Double-click `run.bat`.
    - If Python is not in your PATH, it will ask you to paste the path to `python.exe`.

    **Option B: Manual Command (Conda)**
    If you want to run it manually using your Conda installation:
    
    1.  **Install Dependencies:**
        ```powershell
        C:\Users\shanm\miniconda3\python.exe -m pip install -r backend/requirements.txt
        ```
    
    2.  **Run Server:**
        ```powershell
        C:\Users\shanm\miniconda3\python.exe -m uvicorn app.main:app --reload --app-dir backend
        ```


4.  **Run the React Frontend**:
    The new frontend must be compiled and run using Node.js/Vite.
    
    In a **NEW** terminal window (keep the backend running in the first one):

    ```powershell
    cd frontend
    conda activate examynex
    conda run -n examynex npm run dev
    ```

    - Open the link shown (usually `http://localhost:5173`).
    - Enter any token (e.g., `test-token`).
    - Click **Start Exam Session**.

    *Note: `conda run -n examynex` is a helper to use the npm inside your environment. If you restarted VS Code, `npm run dev` might work directly.*

## Changes Made
- **Fixed Dependencies**: Renamed properties file to `requirements.txt` and added missing packages (`face_recognition`, `numpy`, etc.).
- **Frontend Update**: `index.html` now asks for a token if one is not provided in the URL, making it easier to test.
