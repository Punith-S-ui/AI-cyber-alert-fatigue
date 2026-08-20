@echo off
echo ============================================================
echo  Starting AI Cybersecurity Alert Fatigue Reduction System
echo ============================================================

echo.
echo Starting FastAPI backend on http://localhost:8000 ...
start "SentryGrid Backend" cmd /k "cd backend && call venv\Scripts\activate.bat && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

timeout /t 3 /nobreak >nul

echo Starting React frontend on http://localhost:5173 ...
start "SentryGrid Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ============================================================
echo  Backend:  http://localhost:8000  (docs at /docs)
echo  Frontend: http://localhost:5173
echo  Two new terminal windows were opened - close them to stop
echo  the services, or run stop.bat.
echo ============================================================
