@echo off
rem Keeps the window open when the calling script was started by double-clicking it in Explorer.
echo %cmdcmdline% | find /i "%~1" >nul && pause
