@echo off
cd /d "%~dp0Frontend"
call "%~dp0venv\Scripts\activate.bat"
python main.py
