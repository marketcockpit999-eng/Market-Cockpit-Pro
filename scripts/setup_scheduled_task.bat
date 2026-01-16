@echo off
chcp 65001 >nul
REM ============================================================================
REM Market Cockpit Pro - Setup Scheduled Task
REM ============================================================================
REM This script creates a Windows Task Scheduler task to automatically
REM update market data at regular intervals.
REM
REM Schedule:
REM   - Every 10 minutes during US market hours (9:00-17:00 ET = 23:00-07:00 JST)
REM   - Every 30 minutes outside market hours
REM
REM Run as Administrator to create the task.
REM ============================================================================

echo ============================================
echo Market Cockpit Pro - Scheduled Task Setup
echo ============================================
echo.

REM Check for admin rights
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: This script requires Administrator privileges.
    echo Please right-click and "Run as administrator"
    pause
    exit /b 1
)

set "PROJECT_DIR=C:\Users\81802\.gemini\antigravity\scratch\market_monitor"
set "PYTHON_PATH=python"
set "SCRIPT_PATH=%PROJECT_DIR%\scripts\update_data.py"
set "TASK_NAME=MarketCockpitDataUpdate"

echo Project Directory: %PROJECT_DIR%
echo Script Path: %SCRIPT_PATH%
echo.

REM Check if script exists
if not exist "%SCRIPT_PATH%" (
    echo ERROR: Script not found: %SCRIPT_PATH%
    pause
    exit /b 1
)

REM Delete existing task if it exists
echo [1/4] Removing existing task (if any)...
schtasks /delete /tn "%TASK_NAME%" /f >nul 2>&1
echo       Done.

REM Create logs directory
echo [2/4] Creating logs directory...
if not exist "%PROJECT_DIR%\logs" mkdir "%PROJECT_DIR%\logs"
echo       Done.

REM Create the main scheduled task (every 10 minutes)
echo [3/4] Creating scheduled task...

REM Create XML task definition for more control
set "XML_FILE=%TEMP%\market_cockpit_task.xml"

(
echo ^<?xml version="1.0" encoding="UTF-16"?^>
echo ^<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task"^>
echo   ^<RegistrationInfo^>
echo     ^<Description^>Market Cockpit Pro - Automatic data update every 10 minutes^</Description^>
echo     ^<Author^>Market Cockpit Pro^</Author^>
echo   ^</RegistrationInfo^>
echo   ^<Triggers^>
echo     ^<TimeTrigger^>
echo       ^<Repetition^>
echo         ^<Interval^>PT10M^</Interval^>
echo         ^<StopAtDurationEnd^>false^</StopAtDurationEnd^>
echo       ^</Repetition^>
echo       ^<StartBoundary^>2026-01-01T00:00:00^</StartBoundary^>
echo       ^<Enabled^>true^</Enabled^>
echo     ^</TimeTrigger^>
echo   ^</Triggers^>
echo   ^<Principals^>
echo     ^<Principal id="Author"^>
echo       ^<LogonType^>InteractiveToken^</LogonType^>
echo       ^<RunLevel^>LeastPrivilege^</RunLevel^>
echo     ^</Principal^>
echo   ^</Principals^>
echo   ^<Settings^>
echo     ^<MultipleInstancesPolicy^>IgnoreNew^</MultipleInstancesPolicy^>
echo     ^<DisallowStartIfOnBatteries^>false^</DisallowStartIfOnBatteries^>
echo     ^<StopIfGoingOnBatteries^>false^</StopIfGoingOnBatteries^>
echo     ^<AllowHardTerminate^>true^</AllowHardTerminate^>
echo     ^<StartWhenAvailable^>true^</StartWhenAvailable^>
echo     ^<RunOnlyIfNetworkAvailable^>true^</RunOnlyIfNetworkAvailable^>
echo     ^<IdleSettings^>
echo       ^<StopOnIdleEnd^>false^</StopOnIdleEnd^>
echo       ^<RestartOnIdle^>false^</RestartOnIdle^>
echo     ^</IdleSettings^>
echo     ^<AllowStartOnDemand^>true^</AllowStartOnDemand^>
echo     ^<Enabled^>true^</Enabled^>
echo     ^<Hidden^>false^</Hidden^>
echo     ^<RunOnlyIfIdle^>false^</RunOnlyIfIdle^>
echo     ^<DisallowStartOnRemoteAppSession^>false^</DisallowStartOnRemoteAppSession^>
echo     ^<UseUnifiedSchedulingEngine^>true^</UseUnifiedSchedulingEngine^>
echo     ^<WakeToRun^>false^</WakeToRun^>
echo     ^<ExecutionTimeLimit^>PT5M^</ExecutionTimeLimit^>
echo     ^<Priority^>7^</Priority^>
echo   ^</Settings^>
echo   ^<Actions Context="Author"^>
echo     ^<Exec^>
echo       ^<Command^>%PYTHON_PATH%^</Command^>
echo       ^<Arguments^>"%SCRIPT_PATH%" --log^</Arguments^>
echo       ^<WorkingDirectory^>%PROJECT_DIR%^</WorkingDirectory^>
echo     ^</Exec^>
echo   ^</Actions^>
echo ^</Task^>
) > "%XML_FILE%"

REM Import the task
schtasks /create /tn "%TASK_NAME%" /xml "%XML_FILE%" /f

if %errorlevel% neq 0 (
    echo ERROR: Failed to create scheduled task.
    del "%XML_FILE%" >nul 2>&1
    pause
    exit /b 1
)

del "%XML_FILE%" >nul 2>&1
echo       Done.

REM Verify the task
echo [4/4] Verifying task...
schtasks /query /tn "%TASK_NAME%" /v /fo list | findstr /i "TaskName Status"

echo.
echo ============================================
echo SUCCESS! Scheduled task created.
echo ============================================
echo.
echo Task Name: %TASK_NAME%
echo Schedule:  Every 10 minutes
echo Action:    %PYTHON_PATH% "%SCRIPT_PATH%" --log
echo Log File:  %PROJECT_DIR%\logs\data_update.log
echo.
echo To manage the task:
echo   - View:    schtasks /query /tn "%TASK_NAME%"
echo   - Run now: schtasks /run /tn "%TASK_NAME%"
echo   - Disable: schtasks /change /tn "%TASK_NAME%" /disable
echo   - Enable:  schtasks /change /tn "%TASK_NAME%" /enable
echo   - Delete:  schtasks /delete /tn "%TASK_NAME%" /f
echo.
echo Or use Task Scheduler GUI: taskschd.msc
echo.
pause
