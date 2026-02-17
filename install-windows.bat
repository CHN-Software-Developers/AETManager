@echo off
setlocal

set "PYTHON_URL=https://www.python.org/ftp/python/3.14.3/python-3.14.3-amd64.exe"
set "PYTHON_INSTALLER=python-installer.exe"
set "PYTHON_SHA256=b68ad91421afbbd1a628105199c8c5f6179b21ba799067a8d8c0bbac3b7defb0"

@REM Check for existing Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed. Attempting to install Python...
    @REM Download and validate Python installer
    if exist "%PYTHON_INSTALLER%" del /f /q "%PYTHON_INSTALLER%"
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_INSTALLER%'"
    if errorlevel 1 (
        echo Failed to download Python installer.
        exit /b 1
    )
    
    @REM Check hash checksum for the downloaded installer
    powershell -NoProfile -ExecutionPolicy Bypass -Command "$actual=(Get-FileHash '%PYTHON_INSTALLER%' -Algorithm SHA256).Hash.ToLower(); if ($actual -ne '%PYTHON_SHA256%') { Write-Error ('Hash mismatch! Expected: %PYTHON_SHA256% Actual: ' + $actual); exit 1 }"
    if errorlevel 1 (
        if exist "%PYTHON_INSTALLER%" del /f /q "%PYTHON_INSTALLER%"
        exit /b 1
    )

    @REM start /wait "%PYTHON_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1
    start /wait "" "%PYTHON_INSTALLER%"
    if errorlevel 1 (
        echo Python installer failed.
        del /f /q "%PYTHON_INSTALLER%"
        exit /b 1
    )

    del /f /q "%PYTHON_INSTALLER%"
)

@REM Install the python dependencies for the project
echo Installing python dependencies...
pip install -r requirements.txt
echo Python dependencies installed successfully.

