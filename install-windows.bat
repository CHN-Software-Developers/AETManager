@echo off
setlocal

set "PYTHON_URL=https://www.python.org/ftp/python/3.14.3/python-3.14.3-amd64.exe"
set "PYTHON_INSTALLER=%TEMP%\python-3.14.3-amd64.exe"
set "PYTHON_SHA256=b68ad91421afbbd1a628105199c8c5f6179b21ba799067a8d8c0bbac3b7defb0"

@REM Installation path
set "INSTALL_DIR=%LOCALAPPDATA%\CHN Software Developers\AETManager"

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

@REM Check is pip is in the PATH
pip --version >nul 2>&1

@REM If pip is not found, use python -m pip to install dependencies
if errorlevel 1 (
    echo pip is not found in PATH. Using python -m pip instead.
    python -m pip install -r requirements.txt
) else (
    pip install -r requirements.txt
)

echo Python dependencies installed successfully.

@REM Copy the software files to the installation directory without installation and requirements files
echo Copying files to installation directory...
if not exist "%INSTALL_DIR%" (
    mkdir "%INSTALL_DIR%"
)
robocopy . "%INSTALL_DIR%" /E /XF install-windows.bat requirements.txt >nul
if errorlevel 8 (
    echo Failed to copy files to installation directory.
    exit /b 1
)

@REM Add the installation directory to the PATH environment variable
echo Adding installation directory to PATH environment variable...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$installDir='%INSTALL_DIR%'; $userPath=[Environment]::GetEnvironmentVariable('Path','User'); if ([string]::IsNullOrWhiteSpace($userPath)) { $userPath='' }; if (($userPath -split ';') -notcontains $installDir) { $newPath = if ([string]::IsNullOrEmpty($userPath)) { $installDir } else { $userPath.TrimEnd(';') + ';' + $installDir }; [Environment]::SetEnvironmentVariable('Path', $newPath, 'User') }"
if errorlevel 1 (
    echo Failed to update PATH environment variable.
    exit /b 1
)
set "PATH=%PATH%;%INSTALL_DIR%"

echo Installation complete.

echo Press any key to exit...
pause >nul