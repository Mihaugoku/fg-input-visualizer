@echo off
echo Installing dependencies...

timeout /t 1 > nul

pip install -r requirements.txt
pause
