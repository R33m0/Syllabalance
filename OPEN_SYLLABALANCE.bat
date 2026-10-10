@echo off
setlocal
cd /d "%~dp0"
title Syllabalance

where py >nul 2>&1
if errorlevel 1 (
    echo Python could not be found on this computer.
    echo Install Python, then double-click this file again.
    pause
    exit /b 1
)

py -c "import flask, numpy, scipy" >nul 2>&1
if errorlevel 1 (
    echo Setting up Syllabalance for the first time...
    py -m pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo Setup did not finish. Check your internet connection and try again.
        pause
        exit /b 1
    )
)

echo Starting Syllabalance...
start "" powershell -NoProfile -WindowStyle Hidden -Command "Start-Sleep -Seconds 2; Start-Process 'http://127.0.0.1:5050'"
py -c "from app import app; app.run(host='127.0.0.1', port=5050, debug=False)"

echo.
echo Syllabalance has stopped. You may close this window.
pause
