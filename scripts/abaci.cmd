@echo off

setlocal

REM Prevent Intel run-time library from establishing signal handlers
REM  to allow handling CTRL+C SIGINT in abaci
set FOR_DISABLE_CONSOLE_CTRL_HANDLER=1

if exist %~dp0..\src\abaci_main.py (

    REM Relative execution path
    abaqus python %~dp0..\src\abaci_main.py %* < nul
    
) else (

    if exist %LOCALAPPDATA%\BCI\abaci\abaci_main.py (

        REM Local installation path
        abaqus python %LOCALAPPDATA%\BCI\abaci\abaci_main.py %* < nul

    ) else (

        echo Unable to find the abaci installation in "%LOCALAPPDATA%\BCI\abaci"
        
    )

)

endlocal