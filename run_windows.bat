@echo off
setlocal
cd /d "%~dp0"
for /F "tokens=1 delims=#" %%a in ('"prompt #$E# & echo on & for %%b in (1) do rem"') do set "ESC=%%a"
set "C_INFO=%ESC%[96m"
set "C_ERR=%ESC%[91m"
set "C_RESET=%ESC%[0m"
if not exist .venv\Scripts\python.exe (
  echo %C_INFO%[INFO] Virtual environment not found. Running installer first...%C_RESET%
  call install_windows.bat
  if errorlevel 1 (
    echo %C_ERR%[ERROR] Installer failed.%C_RESET%
    exit /b 1
  )
)
.venv\Scripts\python.exe mdview.py %*
