@echo off
cd %~dp0
rmdir /s /q venv
python -m venv venv
call venv/Scripts/activate.bat
pip install -r requirements.txt
echo "O6HoBJIeHue 3aBepLLIeHO. HaZMuTe ENTER."
pause