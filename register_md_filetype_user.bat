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
echo %C_HEADER% MarkdownViewDesk - Register document file types%C_RESET%
echo %C_HEADER%============================================================%C_RESET%
set "APP_EXE=%~dp0dist\MarkdownViewDesk\MarkdownViewDesk.exe"
if not exist "%APP_EXE%" (
  set "APP_EXE=%~dp0dist\MarkdownViewDesk.exe"
)
if not exist "%APP_EXE%" (
  echo %C_ERR%[ERROR] No built EXE found.%C_RESET%
  echo %C_WARN%Build first with build_windows_onedir.bat%C_RESET%
  pause
  exit /b 1
)
set "PROGID=MarkdownViewDesk.document.1"
echo %C_STEP%[STEP] Registering app ProgID for current Windows user...%C_RESET%
reg add "HKCU\Software\Classes\%PROGID%" /ve /d "MarkdownViewDesk Document" /f >nul
reg add "HKCU\Software\Classes\%PROGID%\DefaultIcon" /ve /d "\"%APP_EXE%\",0" /f >nul
reg add "HKCU\Software\Classes\%PROGID%\shell\open" /ve /d "Open with MarkdownViewDesk" /f >nul
reg add "HKCU\Software\Classes\%PROGID%\shell\open\command" /ve /d "\"%APP_EXE%\" \"%%1\"" /f >nul
reg add "HKCU\Software\Classes\Applications\MarkdownViewDesk.exe\shell\open\command" /ve /d "\"%APP_EXE%\" \"%%1\"" /f >nul

echo %C_STEP%[STEP] Registering supported extensions...%C_RESET%
for %%E in (.md .markdown .mdown .mkd .guide .diz) do (
  echo %C_WARN%  %%E -^> %PROGID%%C_RESET%
  reg add "HKCU\Software\Classes\%%E" /ve /d "%PROGID%" /f >nul
)
ie4uinit.exe -ClearIconCache >nul 2>nul
echo.
echo %C_OK%[OK] Registered .md, .markdown, .mdown, .mkd, .guide and .diz.%C_RESET%
echo %C_WARN%If Windows still asks, choose MarkdownViewDesk once under:%C_RESET%
echo %C_WARN%Settings ^> Apps ^> Default apps ^> Choose defaults by file type%C_RESET%
pause
