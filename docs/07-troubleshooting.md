# 7. Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| `'multichain-util' is not recognized as an internal or external command` | Not in the MultiChain folder and it's not on PATH | `cd /d C:\Users\BK-PC\Downloads\Programs\multichain-windows-2.3.3` or use `scripts\windows\00-open-terminal.bat` |
| `Cannot create chain parameter set, file ...params.dat already exists` | The chain was created before | Use a new name (`chain2`) or delete the old one: `99-reset-chain.bat chain1` |
| `multichain-cli`: `Could not connect to the server 127.0.0.1:<port>` | Node not running or still starting | Start `multichaind chain1` and wait for `Node ready.` |
| `multichaind` exits immediately mentioning another instance / lock | The node is already running (maybe in another window) | Use the running one, or `multichain-cli chain1 stop` and start again |
| `ERROR: Couldn't read configuration file for blockchain chain1` | Wrong chain name, or the chain doesn't exist | `dir %APPDATA%\MultiChain` to see which chains exist |
| Command prompt "hangs" after `multichaind chain1 -daemon` | Normal on Windows: `-daemon` is ignored and the node runs in the foreground | Open a second Command Prompt for `multichain-cli` |
| Windows Firewall pop-up | `multichaind` opens the network port | Allow on Private networks (needed only for a second node) |
| Ports in the answer don't match a friend's | Ports are random per chain | Correct. Always read your own `params.dat` |
| `findstr` prints nothing | Wrong folder or path | `findstr /b "chain-name" "%APPDATA%\MultiChain\chain1\params.dat"` |
| PowerShell: *running scripts is disabled on this system* | Execution policy | Use the `.bat` launchers (they pass `-ExecutionPolicy Bypass`) |
| Web Demo: `HTTP 0`, `HTTP 401`, curl missing | See [05-web-demo.md](05-web-demo.md#troubleshooting) | |
| Node log | `debug.log` has details | `notepad %APPDATA%\MultiChain\chain1\debug.log` |

## Start completely fresh

```bat
multichain-cli chain1 stop
rmdir /s /q %APPDATA%\MultiChain\chain1
multichain-util create chain1
multichaind chain1
```

(`scripts\windows\99-reset-chain.bat` does the stop and delete for you, after asking.)
