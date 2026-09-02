@echo off
echo =========================================
echo       PETER AI BUTLER - STARTUP
echo =========================================

IF NOT EXIST "venv\" (
    echo [INFO] Creating Python virtual environment...
    python -m venv venv
)

echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

echo [INFO] Installing requirements...
pip install -r requirements.txt -q

IF NOT EXIST ".env" (
    echo [INFO] Copying .env.example to .env...
    copy .env.example .env
)

echo [INFO] Starting Peter...
python main.py

pause
