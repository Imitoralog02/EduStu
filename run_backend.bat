@echo off
cd /d "%~dp0Backend"
call "%~dp0venv\Scripts\activate.bat"
python -m uvicorn main:app --host 0.0.0.0 --port 8000
