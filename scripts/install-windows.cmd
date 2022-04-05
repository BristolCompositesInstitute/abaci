@echo off

if exist C:\SIMULIA\Commands\ (

    echo Installing abaci to %LOCALAPPDATA%\BCI\abaci
    xcopy "%~dp0.." "%LOCALAPPDATA%\BCI\abaci" /E /Y /I /Q

    echo Installing abaci launcher to C:\SIMULIA\Commands
    copy "%~dp0..\scripts\abaci.cmd" "C:\SIMULIA\Commands"

    echo Abaci installed successfully

) else (

    echo Unable to find folder "C:\SIMULIA\Commands" to install abaci launcher
    
)

pause
