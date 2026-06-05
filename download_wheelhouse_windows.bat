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
echo %C_HEADER% MarkdownViewDesk - Download wheelhouse%C_RESET%
echo %C_HEADER%============================================================%C_RESET%
if not exist wheelhouse mkdir wheelhouse
where py >nul 2>nul
if errorlevel 1 (
  echo %C_ERR%[ERROR] Python launcher "py" not found.%C_RESET%
  pause
  exit /b 1
)
echo %C_STEP%[STEP] Downloading packages into wheelhouse for offline installs...%C_RESET%
py -3 -m pip download -r requirements.txt -d wheelhouse
if errorlevel 1 (
  echo %C_ERR%[ERROR] Download failed.%C_RESET%
  pause
  exit /b 1
)
echo %C_OK%[OK] Wheelhouse ready: %cd%\wheelhouse%C_RESET%
pause
