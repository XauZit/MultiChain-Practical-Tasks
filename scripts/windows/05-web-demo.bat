@echo off
rem Step 5 - configure and open the MultiChain Web Demo (PHP built-in server on http://127.0.0.1:8080/).
rem The node(s) must be running (02-start-node.bat). Press Ctrl+C to stop.
rem Usage: 05-web-demo.bat [chain-name ...]   e.g. 05-web-demo.bat PaymentChain ServiceChain
setlocal
call "%~dp0_load-settings.bat"
if not "%~1"=="" set "CHAIN=%*"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0web-demo.ps1" -Chain "%CHAIN%"
call "%~dp0_pause-if-double-clicked.bat" "%~f0"
