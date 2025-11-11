@echo off
echo ============================================================
echo STARTING WEB-BASED VIRTUAL OS BACKEND
echo ============================================================
echo.

cd /d "%~dp0.."
python backend\start_backend.py

pause
