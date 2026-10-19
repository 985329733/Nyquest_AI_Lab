@echo off
cd /d "%~dp0"
if "%~1"=="" (
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Build.ps1" -SelectProject
) else (
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Build.ps1" -Project "%~1"
)
if errorlevel 1 (
    echo BUILD OR VERIFICATION INCOMPLETE. Read the error above.
    pause
    exit /b 1
)
echo Build and project software checks complete. Bench tests still required.
pause
