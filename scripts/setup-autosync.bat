@echo off
:: setup-autosync.bat
:: Run ONCE on any Windows machine — no Python, no admin rights needed.
:: Registers vault-sync.ps1 to start automatically on login,
:: then starts it immediately in the background.

setlocal
set "VAULT=%~dp0.."
set "SCRIPT=%~dp0vault-sync.ps1"
set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "VBS=%STARTUP%\VaultAutoSync.vbs"

echo.
echo === setup-autosync ===
echo Vault:   %VAULT%
echo Script:  %SCRIPT%
echo Startup: %VBS%
echo.

:: Create Startup folder if missing
if not exist "%STARTUP%" mkdir "%STARTUP%"

:: Write a VBScript launcher (runs PowerShell silently, no window)
(
echo Set WshShell = CreateObject^("WScript.Shell"^)
echo WshShell.Run "powershell.exe -NonInteractive -WindowStyle Hidden -ExecutionPolicy Bypass -File ""%SCRIPT%""", 0, False
) > "%VBS%"

echo Registered: %VBS%
echo vault-sync will start automatically on next login.
echo.

:: Start immediately (detached, no window)
echo Starting now...
start "" /B powershell.exe -NonInteractive -WindowStyle Hidden -ExecutionPolicy Bypass -File "%SCRIPT%"

echo vault-sync is running in background.
echo Log: %VAULT%\scripts\vault-sync.log
echo.
pause
