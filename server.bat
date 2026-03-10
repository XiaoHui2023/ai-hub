@echo off
cd /d %~dp0

if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
)

call .venv\Scripts\activate.bat
pip install -e .
python examples\server.py config.yaml
pause
