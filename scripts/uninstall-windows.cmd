@echo off

if exist C:\SIMULIA\Commands\abaci.cmd (

    echo Uninstalling abaci launcher from C:\SIMULIA\Commands
    del C:\SIMULIA\Commands\abaci.cmd

    if exist %LOCALAPPDATA%\BCI\abaci (

        echo Uninstalling abaci from %LOCALAPPDATA%\BCI\abaci
        rmdir /s %LOCALAPPDATA%\BCI\abaci

        echo Abaci removed successfully

    ) else (

        echo Unable to find folder "%LOCALAPPDATA%\BCI\abaci" to remove abaci launcher

    )

) else (

    echo Unable to find folder "C:\SIMULIA\Commands" to remove abaci launcher
    
)

pause