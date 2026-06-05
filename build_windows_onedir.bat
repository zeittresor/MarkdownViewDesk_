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
echo %C_HEADER% MarkdownViewDesk - Build recommended onedir EXE%C_RESET%
echo %C_HEADER%============================================================%C_RESET%
if not exist .venv\Scripts\python.exe call install_windows.bat
if errorlevel 1 exit /b 1
echo %C_STEP%[STEP] Installing/updating PyInstaller...%C_RESET%
.venv\Scripts\python.exe -m pip install pyinstaller
if errorlevel 1 exit /b 1
echo %C_STEP%[STEP] Building recommended onedir EXE...%C_RESET%
.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --windowed --name MarkdownViewDesk mdview.py
if errorlevel 1 (
  echo %C_ERR%[ERROR] Build failed.%C_RESET%
  pause
  exit /b 1
)
echo.
echo %C_OK%[OK] EXE folder: dist\MarkdownViewDesk\MarkdownViewDesk.exe%C_RESET%
echo %C_WARN%[NOTE] Recommended because Qt WebEngine is more reliable in onedir mode.%C_RESET%
pause
