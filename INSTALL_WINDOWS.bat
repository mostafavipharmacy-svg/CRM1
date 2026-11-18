@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  echo Python launcher was not found. Install Python 3.10+ from python.org and enable PATH.
  pause
  exit /b 1
)
py -3 --version
if errorlevel 1 (
  echo Python 3.10 or newer is required.
  pause
  exit /b 1
)
if not exist ".venv\Scripts\python.exe" py -3 -m venv .venv
if errorlevel 1 goto :error
.venv\Scripts\python.exe -m pip install --upgrade pip
if errorlevel 1 goto :error
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto :error
echo Installation complete. Starting Pharmacy CRM...
.venv\Scripts\python.exe app.py
if errorlevel 1 goto :error
goto :eof
:error
echo Installation or application failed. Check the messages above.
pause
exit /b 1
