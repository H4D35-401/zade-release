@echo off
TITLE ZADE IGNITE | UNIVERSAL HUD LAUNCHER
echo [INFO] Initializing Zade Ignite Protocol for Windows...

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.9+ and add it to PATH.
    pause
    exit /b
)

:: Setup Virtual Environment
if not exist "venv_win" (
    echo [INFO] Creating Virtual Neural Environment...
    python -m venv venv_win
)

:: Install Dependencies
echo [INFO] Synchronizing Dependency Protocols...
venv_win\Scripts\pip install -r src/requirements.txt

:: Launch
echo [INFO] Igniting HUD...
start venv_win\Scripts\python src/config_gui.py
exit
