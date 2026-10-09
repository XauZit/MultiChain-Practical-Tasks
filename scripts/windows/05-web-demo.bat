@echo off
rem Step 5 - configure and open the MultiChain Web Demo (PHP built-in server on http://127.0.0.1:8080/).
rem The node must be running (02-start-node.bat). Press Ctrl+C to stop. Usage: 05-web-demo.bat [chain-name]
setlocal
call "%~dp0_load-settings.bat"
if not "%~1"=="" set "CHAIN=%~1"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0web-demo.ps1" -Chain %CHAIN%
call "%~dp0_pause-if-double-clicked.bat" "%~f0"
