@echo off
setlocal

@REM Installation path
set "INSTALL_DIR=%LOCALAPPDATA%\CHN Software Developers\AETManager"

@REM Remove installation directory from PATH environment variable
echo Removing installation directory from PATH environment variable...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$installDir='%INSTALL_DIR%'.TrimEnd('\'); $userPath=[Environment]::GetEnvironmentVariable('Path','User'); if ([string]::IsNullOrWhiteSpace($userPath)) { exit 0 }; $newPath=(($userPath -split ';') | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | Where-Object { $_.TrimEnd('\') -ine $installDir }) -join ';'; [Environment]::SetEnvironmentVariable('Path', $newPath, 'User')"
if errorlevel 1 (
    echo Failed to update PATH environment variable.
    exit /b 1
)

@REM Remove installed files
echo Removing installed files...
if exist "%INSTALL_DIR%" (
    rmdir /s /q "%INSTALL_DIR%"
    if exist "%INSTALL_DIR%" (
        echo Failed to remove installation directory.
        exit /b 1
    )
) else (
    echo Installation directory not found. Nothing to remove.
)

echo Uninstallation complete.

echo Press any key to exit...
pause >nul
