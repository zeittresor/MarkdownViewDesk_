@echo off
setlocal
cd /d "%~dp0"
for /F "tokens=1 delims=#" %%a in ('"prompt #$E# & echo on & for %%b in (1) do rem"') do set "ESC=%%a"
set "C_HEADER=%ESC%[96m"
set "C_STEP=%ESC%[94m"
set "C_OK=%ESC%[92m"
set "C_WARN=%ESC%[93m"
set "C_ERR=%ESC%[91m"
set "C_RESET=%ESC%[0m"
echo %C_HEADER%============================================================%C_RESET%
echo %C_HEADER% MarkdownViewDesk - Windows venv installer%C_RESET%
echo %C_HEADER%============================================================%C_RESET%
where py >nul 2>nul
if errorlevel 1 (
  echo %C_ERR%[ERROR] Python launcher "py" not found. Install Python 3.10+ first.%C_RESET%
  pause
  exit /b 1
)
if not exist .venv (
  echo %C_STEP%[1/3] Creating virtual environment...%C_RESET%
  py -3 -m venv .venv
  if errorlevel 1 goto :error
) else (
  echo %C_WARN%[1/3] Virtual environment already exists.%C_RESET%
)
echo %C_STEP%[2/3] Upgrading pip...%C_RESET%
.venv\Scripts\python.exe -m pip install --upgrade pip
if errorlevel 1 goto :error
echo %C_STEP%[3/3] Installing dependencies...%C_RESET%
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto :error
echo.
echo %C_OK%[OK] Installation complete.%C_RESET%
echo %C_OK%Start with run_windows.bat%C_RESET%
pause
exit /b 0
:error
echo.
echo %C_ERR%[ERROR] Installation failed.%C_RESET%
pause
exit /b 1
