@echo off
setlocal
cd /d "%~dp0"
for /F "tokens=1 delims=#" %%a in ('"prompt #$E# & echo on & for %%b in (1) do rem"') do set "ESC=%%a"
set "C_HEADER=%ESC%[96m"
set "C_STEP=%ESC%[94m"
set "C_OK=%ESC%[92m"
set "C_WARN=%ESC%[93m"
set "C_RESET=%ESC%[0m"
echo %C_HEADER%============================================================%C_RESET%
echo %C_HEADER% MarkdownViewDesk - Unregister document file types%C_RESET%
echo %C_HEADER%============================================================%C_RESET%
echo %C_STEP%[STEP] Removing MarkdownViewDesk user file association keys...%C_RESET%
for %%E in (.md .markdown .mdown .mkd .guide .diz) do (
  echo %C_WARN%  Removing %%E%C_RESET%
  reg delete "HKCU\Software\Classes\%%E" /ve /f >nul 2>nul
)
reg delete "HKCU\Software\Classes\MarkdownViewDesk.document.1" /f >nul 2>nul
reg delete "HKCU\Software\Classes\MarkdownViewDesk.md.1" /f >nul 2>nul
reg delete "HKCU\Software\Classes\Applications\MarkdownViewDesk.exe" /f >nul 2>nul
ie4uinit.exe -ClearIconCache >nul 2>nul
echo %C_OK%[OK] Removed MarkdownViewDesk registration keys for current user.%C_RESET%
pause
