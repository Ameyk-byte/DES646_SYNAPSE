@echo off
echo ==========================================
echo      Starting Neuro AI Assistant...
echo ==========================================

IF EXIST venv (
    echo ✅ Virtual environment found.
) ELSE (
    echo 🔧 Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate
pip install -r requirements.txt >nul

echo ✅ Launching Neuro
python main.py

pause
