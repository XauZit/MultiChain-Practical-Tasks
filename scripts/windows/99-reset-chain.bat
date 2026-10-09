@echo off
rem Stops the node and DELETES the chain folder (asks for confirmation) so you can practise from scratch.
rem Usage: 99-reset-chain.bat [chain-name]
setlocal
call "%~dp0_load-settings.bat"
if not "%~1"=="" set "CHAIN=%~1"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0reset-chain.ps1" -Chain %CHAIN%
call "%~dp0_pause-if-double-clicked.bat" "%~f0"
