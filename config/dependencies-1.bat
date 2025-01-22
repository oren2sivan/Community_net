@echo off
setlocal enabledelayedexpansion
REM Set working directory
set "WORK_DIR=%USERPROFILE%\ipfs_setup"

REM Clean up previous setup if exists
if exist "%WORK_DIR%" (
    echo Removing existing setup directory...
    rmdir /s /q "%WORK_DIR%"
)

REM Create a fresh working directory
echo Creating working directory...
mkdir "%WORK_DIR%"
cd "%WORK_DIR%"

REM Define URLs for Kubo
set "KUBO_URL=https://dist.ipfs.tech/kubo/v0.32.1/kubo_v0.32.1_windows-amd64.zip"

REM Download Kubo
echo Downloading Kubo...
curl -L "%KUBO_URL%" -o "kubo.zip"
if not exist "kubo.zip" (
    echo Failed to download Kubo. Exiting.
    exit /b
)

REM Remove existing IPFS configuration directory
echo Cleaning up existing IPFS configuration...
if exist "%USERPROFILE%\.ipfs" (
    rmdir /s /q "%USERPROFILE%\.ipfs"
)

REM Extract Kubo using tar
echo Extracting Kubo...
tar -xvf "kubo.zip" -C "%WORK_DIR%"
if errorlevel 1 (
    echo Extraction failed. Ensure tar is installed and available in PATH. Exiting.
    exit /b
)

REM Locate the Kubo directory (assuming it's named "kubo" in the zip)
set "KUBO_DIR=%WORK_DIR%\kubo"

REM Verify the existence of IPFS binary
if not exist "%KUBO_DIR%\ipfs.exe" (
    echo IPFS binary not found in %KUBO_DIR%. Exiting.
    exit /b
)

REM Add Kubo directory to PATH
set PATH=%KUBO_DIR%;%PATH%
echo Added Kubo to PATH.

REM Verify IPFS installation
echo Verifying IPFS installation...
ipfs --version
if errorlevel 1 (
    echo IPFS command not recognized. Exiting.
    exit /b
)

REM Initialize IPFS
echo Initializing IPFS...
ipfs init
if errorlevel 1 (
    echo IPFS initialization failed. Exiting.
    exit /b
)