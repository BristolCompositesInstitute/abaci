@echo off

if exist %~dp0..\src\abaci_main.py (

    REM Relative execution path
    abaqus python %~dp0..\src\abaci_main.py %*
    
) else (

    if exist %LOCALAPPDATA%\BCI\abaci\src\abaci_main.py (

        REM Local installation path
        abaqus python %LOCALAPPDATA%\BCI\abaci\src\abaci_main.py %*

    ) else (

        echo Unable to find the abaci installation in "%LOCALAPPDATA%\BCI\abaci"
        
    )

)