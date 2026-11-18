@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Run INSTALL_WINDOWS.bat first to create the virtual environment.
  pause
  exit /b 1
)
.venv\Scripts\python.exe -m pip install pyinstaller
if errorlevel 1 goto :error
.venv\Scripts\python.exe -m PyInstaller --noconfirm pharmacy_crm.spec
if errorlevel 1 goto :error
echo Build complete: dist\PharmacyCRM\PharmacyCRM.exe
 echo Copy the entire dist\PharmacyCRM folder to the target Windows computer.
pause
goto :eof
:error
echo Build failed. Check the messages above.
pause
exit /b 1
