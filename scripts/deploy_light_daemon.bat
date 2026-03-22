@echo off
REM Deploy light daemon to Raspberry Pi (Windows)

set RPI_HOST=192.168.100.197
set RPI_USER=beans
set SSH_KEY=%USERPROFILE%\.ssh\id_ed25519_rpi

echo ======================================
echo Deploying Light Daemon to Raspberry Pi
echo ======================================

echo Uploading light_daemon.py...
scp -i "%SSH_KEY%" light_daemon.py %RPI_USER%@%RPI_HOST%:~/

if %errorlevel% neq 0 (
    echo X Upload failed
    exit /b 1
)

echo √ Upload successful

echo Making executable...
ssh -i "%SSH_KEY%" %RPI_USER%@%RPI_HOST% "chmod +x ~/light_daemon.py"

echo.
echo ======================================
echo √ Deployment Complete
echo ======================================
echo.
echo To start the daemon on Raspberry Pi:
echo   ssh beans@%RPI_HOST%
echo   python3 light_daemon.py
echo.
echo Or run in background:
echo   nohup python3 light_daemon.py ^> light_daemon.log 2^>^&1 ^&
echo.
echo To test from laptop:
echo   echo 80 ^| nc %RPI_HOST% 9999
echo.
pause
