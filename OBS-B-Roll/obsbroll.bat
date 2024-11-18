@echo off
set programName=obs64.exe
set obsPath="C:\Program Files\obs-studio\bin\64bit"
set pythonScript="C:\Repos\Utility-Scripts\OBS-B-Roll\obs-b-roll.py"

:: Change to OBS directory
cd /d %obsPath%

:: Check if OBS is running
tasklist /FI "IMAGENAME eq %programName%" | find /I "%programName%" >nul
if %ERRORLEVEL% NEQ 0 (
    echo OBS is not running. Starting OBS...
    start "" %programName%
) else (
    echo OBS is already running.
)

:: Wait for a few seconds
timeout /t 3 /nobreak >nul

:: Run the Python script
echo Running Python script...
python %pythonScript%
