@echo off
rem Step 2 - start the node:   multichaind chain1
rem On Windows -daemon is ignored, so the node runs in its own window. Keep that window open.
rem Usage: 02-start-node.bat [chain-name]
setlocal
call "%~dp0_load-settings.bat"
if not "%~1"=="" set "CHAIN=%~1"

if not exist "%MC_DATA%\%CHAIN%\params.dat" (
    echo Chain "%CHAIN%" has not been created yet - run 01-create-chain.bat first.
    goto :end
)

echo C:\^> multichaind %CHAIN%
start "MultiChain node: %CHAIN%" /D "%MC_DIR%" cmd /k multichaind.exe %CHAIN%
echo.
echo The node is starting in a new window titled "MultiChain node: %CHAIN%".
echo Wait until that window prints "Node ready.", then run for example:
echo     03-show-answers.bat     or     multichain-cli %CHAIN% getinfo

:end
call "%~dp0_pause-if-double-clicked.bat" "%~f0"
