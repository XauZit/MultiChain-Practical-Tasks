@echo off
rem Step 1 - create the blockchain:   multichain-util create chain1
rem Usage: 01-create-chain.bat [chain-name]
setlocal
call "%~dp0_load-settings.bat"
if not "%~1"=="" set "CHAIN=%~1"

if exist "%MC_DATA%\%CHAIN%\params.dat" (
    echo Chain "%CHAIN%" already exists in "%MC_DATA%\%CHAIN%".
    echo Delete it with 99-reset-chain.bat %CHAIN%  or use another name:  01-create-chain.bat chain2
    goto :end
)

echo C:\^> multichain-util create %CHAIN%
"%MC_DIR%\multichain-util.exe" create %CHAIN%
if errorlevel 1 goto :end

echo.
echo Files generated in %MC_DATA%\%CHAIN%:
dir /b "%MC_DATA%\%CHAIN%"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0show-answers.ps1" -Chain %CHAIN%

:end
call "%~dp0_pause-if-double-clicked.bat" "%~f0"
