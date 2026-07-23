@echo off
echo Installing dependencies (only needed once)...
pip install -r requirements.txt

echo.
echo Starting CropDoc backend...
python app.py

pause
