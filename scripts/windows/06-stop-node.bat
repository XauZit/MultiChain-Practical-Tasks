@echo off
rem Stops the node:   multichain-cli chain1 stop
rem Usage: 06-stop-node.bat [chain-name]
setlocal
call "%~dp0_load-settings.bat"
if not "%~1"=="" set "CHAIN=%~1"
echo C:\^> multichain-cli %CHAIN% stop
"%MC_DIR%\multichain-cli.exe" %CHAIN% stop
call "%~dp0_pause-if-double-clicked.bat" "%~f0"
