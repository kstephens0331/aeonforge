@echo off
echo Starting Aeonforge Phase 3 Backend...
echo =====================================
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.
echo Installing backend dependencies...
pip install fastapi uvicorn python-multipart
echo.
echo Starting API server...
echo Backend API will be available at: http://localhost:8000
echo API documentation at: http://localhost:8000/docs
echo.
cd backend
python main.py