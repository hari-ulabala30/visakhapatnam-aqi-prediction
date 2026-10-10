@echo off
setlocal

cd /d "C:\Users\ASUS\Desktop\dti" || exit /b 1

REM Confirm the API key is available to the scheduled task without printing it.
if not defined OPENWEATHER_API_KEY (
    echo [%date% %time%] ERROR: OPENWEATHER_API_KEY is not available.>> logs.txt
    exit /b 1
)

echo.>> logs.txt
echo ==================================================>> logs.txt
echo [%date% %time%] AQI automation started.>> logs.txt

"C:\Program Files\Python314\python.exe" ml.py >> automation_console.log 2>&1
set "PYTHON_EXIT_CODE=%ERRORLEVEL%"

if "%PYTHON_EXIT_CODE%"=="0" (
    echo [%date% %time%] AQI automation completed successfully.>> logs.txt
) else (
    echo [%date% %time%] ERROR: ml.py failed with exit code %PYTHON_EXIT_CODE%.>> logs.txt
)

exit /b %PYTHON_EXIT_CODE%
