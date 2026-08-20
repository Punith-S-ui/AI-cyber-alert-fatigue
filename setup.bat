@echo off
setlocal enabledelayedexpansion
echo ============================================================
echo  AI Cybersecurity Alert Fatigue Reduction System - SETUP
echo ============================================================

echo.
echo [1/8] Checking for Python...
where python >nul 2>nul
if errorlevel 1 (
    echo ERROR: Python was not found on PATH. Install Python 3.10+ from python.org and re-run this script.
    pause
    exit /b 1
)
python --version

echo.
echo [2/8] Checking for Node.js...
where node >nul 2>nul
if errorlevel 1 (
    echo ERROR: Node.js was not found on PATH. Install Node.js 18+ from nodejs.org and re-run this script.
    pause
    exit /b 1
)
node --version

echo.
echo [3/8] Creating Python virtual environment (backend\venv)...
cd backend
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate.bat

echo.
echo [4/8] Installing Python dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: pip install failed. See the output above.
    pause
    exit /b 1
)

echo.
echo [5/8] Installing frontend dependencies (this can take a few minutes)...
cd ..\frontend
call npm install
if errorlevel 1 (
    echo ERROR: npm install failed. See the output above.
    pause
    exit /b 1
)

echo.
echo [6/8] Initializing the database...
cd ..\backend
python -m app.database.init_db

echo.
echo [7/8] Seeding demo data (users, ~500+ demo alerts)...
python seed.py

echo.
echo [8/8] Training the Random Forest severity model...
python -c "from app.ml.severity_model import severity_model_service; from app.ml.training_data import generate_training_dataframe; print(severity_model_service.train(generate_training_dataframe()))"

cd ..
echo.
echo ============================================================
echo  SETUP COMPLETE
echo  Run start.bat to launch the application.
echo ============================================================
pause
