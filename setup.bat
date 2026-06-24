@echo off
echo ============================================
echo  Sales Intelligence Platform - Setup
echo ============================================

echo.
echo [1/4] Setting up Python virtual environment...
cd backend
python -m venv venv
call venv\Scripts\activate.bat

echo.
echo [2/4] Installing Python dependencies...
pip install -r requirements.txt

echo.
echo [3/4] Generating sample dataset...
python generate_sample.py

echo.
echo [4/4] Setup complete!
echo.
echo To start the backend:
echo   cd backend
echo   venv\Scripts\activate
echo   uvicorn app.main:app --reload --port 8000
echo.
echo To start the frontend:
echo   cd frontend
echo   npm install
echo   npm run dev
echo.
echo Backend API: http://localhost:8000
echo Frontend:    http://localhost:5173
echo API Docs:    http://localhost:8000/docs
pause
