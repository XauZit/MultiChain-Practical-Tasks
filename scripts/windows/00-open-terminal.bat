@echo off
rem Opens a Command Prompt in the MultiChain folder where multichain-util, multichaind,
rem multichain-cli and php all work without typing their full paths.
setlocal
call "%~dp0_load-settings.bat"
for %%P in ("%PHP_EXE%") do set "PHP_DIR=%%~dpP"
set "PATH=%MC_DIR%;%PHP_DIR%;%PATH%"
start "MultiChain terminal" /D "%MC_DIR%" cmd /k echo Ready. Data folder: %MC_DATA%   Try: multichain-cli %CHAIN% getinfo
