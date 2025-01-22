@echo off
setlocal EnableDelayedExpansion

REM Set paths for IPFS
set "IPFS_PATH=%USERPROFILE%\.ipfs"
set "KUBO_PATH=%USERPROFILE%\ipfs_setup\kubo"

REM Add Kubo directory to PATH
set "PATH=%PATH%;%KUBO_PATH%"

REM Verify IPFS is accessible
where ipfs >nul 2>nul
if errorlevel 1 (
    echo IPFS not found in PATH. Checking user profile...
    if exist "%KUBO_PATH%\ipfs.exe" (
        set "PATH=%PATH%;%KUBO_PATH%"
        echo Found IPFS in %KUBO_PATH%
    ) else (
        echo Error: Cannot find ipfs.exe in %KUBO_PATH%
        pause
        exit /b 1
    )
)

REM Modify IPFS configuration for private network
echo Configuring IPFS for private network...

REM Remove default bootstrap peers
call "%KUBO_PATH%\ipfs.exe" bootstrap rm --all

REM Set Routing Type to DHT
call "%KUBO_PATH%\ipfs.exe" config Routing.Type dht

REM Disable public gateways
call "%KUBO_PATH%\ipfs.exe" config --json Gateway.PublicGateways "null"

REM Configure Swarm Addresses (with escaped quotes)
call "%KUBO_PATH%\ipfs.exe" config --json Addresses.Swarm "[^"/ip4/0.0.0.0/tcp/4001^", ^"/ip6/::/tcp/4001^"]"

REM Disable MDNS discovery
call "%KUBO_PATH%\ipfs.exe" config --json Discovery.MDNS.Enabled true

REM Disable Public DHT
call "%KUBO_PATH%\ipfs.exe" config --json Discovery.PublicDHT false

REM Force private networking
setx LIBP2P_FORCE_PNET 1

REM Verify configuration
echo Verifying IPFS configuration...

REM Get and display Peer ID
echo Getting Peer ID...
call "%KUBO_PATH%\ipfs.exe" id

REM Start IPFS daemon
echo Starting IPFS daemon...
start /B cmd /c "%KUBO_PATH%\ipfs.exe" daemon

echo Private IPFS network setup complete.
pause