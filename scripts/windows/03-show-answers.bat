@echo off
rem Step 3 - print the answers to the sample question (chain-name, protocol-version, ports, consensus).
rem Usage: 03-show-answers.bat [chain-name]
setlocal
call "%~dp0_load-settings.bat"
if not "%~1"=="" set "CHAIN=%~1"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0show-answers.ps1" -Chain %CHAIN%
call "%~dp0_pause-if-double-clicked.bat" "%~f0"
