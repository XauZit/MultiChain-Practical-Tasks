@echo off
rem Task 3 - create (if needed) and start PaymentChain and ServiceChain in their own windows,
rem then configure the web demo for both chains and open it.
setlocal
call "%~dp0_load-settings.bat"
for %%C in (PaymentChain ServiceChain) do (
    if not exist "%MC_DATA%\%%C\params.dat" (
        echo C:\^> multichain-util create %%C
        "%MC_DIR%\multichain-util.exe" create %%C
    )
    echo C:\^> multichaind %%C
    start "MultiChain node: %%C" /D "%MC_DIR%" cmd /k multichaind.exe %%C
)
echo.
echo Two node windows are starting. When BOTH show "Node ready." press a key here.
pause
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0web-demo.ps1" -Chain "PaymentChain ServiceChain"
call "%~dp0_pause-if-double-clicked.bat" "%~f0"
