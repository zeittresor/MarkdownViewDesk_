@echo off
setlocal
cd /d "%~dp0"
for /F "tokens=1 delims=#" %%a in ('"prompt #$E# & echo on & for %%b in (1) do rem"') do set "ESC=%%a"
set "C_HEADER=%ESC%[96m"
set "C_STEP=%ESC%[94m"
set "C_OK=%ESC%[92m"
set "C_ERR=%ESC%[91m"
set "C_RESET=%ESC%[0m"
echo %C_HEADER%============================================================%C_RESET%
echo %C_HEADER% MarkdownViewDesk - Offline wheelhouse install%C_RESET%
echo %C_HEADER%============================================================%C_RESET%
if not exist wheelhouse (
  echo %C_ERR%[ERROR] wheelhouse folder not found. Run download_wheelhouse_windows.bat on an online PC first.%C_RESET%
  pause
  exit /b 1
)
if not exist .venv (
  echo %C_STEP%[STEP] Creating virtual environment...%C_RESET%
  py -3 -m venv .venv
)
echo %C_STEP%[STEP] Installing dependencies from local wheelhouse...%C_RESET%
.venv\Scripts\python.exe -m pip install --no-index --find-links=wheelhouse -r requirements.txt
if errorlevel 1 (
  echo %C_ERR%[ERROR] Offline install failed.%C_RESET%
  pause
  exit /b 1
)
echo %C_OK%[OK] Offline install complete.%C_RESET%
pause
