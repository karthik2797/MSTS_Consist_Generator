@echo off
setlocal
cd /d "%~dp0"
title Build MSTS Consist Generator
where py >nul 2>nul
if errorlevel 1 (
  echo Python 3 not found. Install it from https://www.python.org/downloads/windows/
  echo Enable "Add python.exe to PATH" during setup.
  pause
  exit /b 1
)
py -m pip install --upgrade pyinstaller
if errorlevel 1 goto failed
py -m PyInstaller --noconfirm --clean --onefile --windowed --name MSTS_Consist_Generator MSTS_Consist_Generator.py
if errorlevel 1 goto failed
echo.
echo Build complete: %~dp0dist\MSTS_Consist_Generator.exe
pause
exit /b 0
:failed
echo Build failed. Check the errors above.
pause
exit /b 1
