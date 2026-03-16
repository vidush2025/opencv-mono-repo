@echo off
setlocal

cd /d "%~dp0\vision"

set "PY_CMD=python"

if not exist .venv (
  %PY_CMD% -m venv .venv
)

call .venv\Scripts\activate.bat

python -m pip install --upgrade pip
pip install -r requirements.txt

echo Starting Python vision app...
python main.py

endlocal