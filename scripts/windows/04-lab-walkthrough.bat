@echo off
rem Step 4 - run the lab commands step by step (addresses, permissions, assets, streams, blocks).
rem The node must be running (02-start-node.bat). Usage: 04-lab-walkthrough.bat [chain-name]
setlocal
call "%~dp0_load-settings.bat"
if not "%~1"=="" set "CHAIN=%~1"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0lab-walkthrough.ps1" -Chain %CHAIN%
call "%~dp0_pause-if-double-clicked.bat" "%~f0"
