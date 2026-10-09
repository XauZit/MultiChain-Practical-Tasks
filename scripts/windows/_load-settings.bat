@echo off
rem Loads settings.txt into MC_DIR, PHP_EXE, CHAIN, WEB_PORT and MC_DATA (call this, do not run it).
for /f "usebackq eol=# tokens=1,* delims==" %%A in ("%~dp0settings.txt") do set "%%A=%%B"
if not defined MC_DATA set "MC_DATA=%APPDATA%\MultiChain"
