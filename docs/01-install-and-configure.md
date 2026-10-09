# 1. Install and configure MultiChain (Windows)

Your setup:

| Item | Path |
|---|---|
| MultiChain 2.3.3 (Windows) | `C:\Users\BK-PC\Downloads\Programs\multichain-windows-2.3.3\` |
| PHP 8.4 (for the Web Demo) | `C:\inetpub\php\php-8.4\php.exe` |
| MultiChain data folder | `%APPDATA%\MultiChain` = `C:\Users\BK-PC\AppData\Roaming\MultiChain` |

## What "installing" MultiChain means

MultiChain for Windows is a zip file. There is no installer. "Installing" means unzipping it and making
the three programs runnable:

| Program | Job |
|---|---|
| `multichain-util.exe` | Creates a new blockchain's parameter file (`multichain-util create chain1`) |
| `multichaind.exe` | The node (daemon). Creates the genesis block on first run, then mines, stores blocks and serves the API |
| `multichain-cli.exe` | Command-line client that sends API commands to a running node (`multichain-cli chain1 getinfo`) |

Check that all three are in your folder:

```bat
dir C:\Users\BK-PC\Downloads\Programs\multichain-windows-2.3.3\*.exe
```

## Option A: run the commands from the MultiChain folder (simplest)

```bat
cd /d C:\Users\BK-PC\Downloads\Programs\multichain-windows-2.3.3
multichain-util
```

`multichain-util` with no arguments prints its version banner and usage. That proves MultiChain works:

```text
MultiChain 2.3.3 Utilities (latest protocol 20013)

Usage:
  multichain-util create <blockchain-name>  ( <protocol-version> = 20013 ) [options]
  ...
```

## Option B: add MultiChain to PATH (run from any folder)

**This session only** (nothing changes permanently):

```bat
set PATH=C:\Users\BK-PC\Downloads\Programs\multichain-windows-2.3.3;%PATH%
```

**Shortcut:** double-click `scripts\windows\00-open-terminal.bat`. It opens a Command Prompt where
`multichain-util`, `multichaind`, `multichain-cli` and `php` all work.

**Permanently:** Start → type *environment variables* → *Edit environment variables for your account* →
select **Path** → **Edit** → **New** → paste
`C:\Users\BK-PC\Downloads\Programs\multichain-windows-2.3.3` → OK. Then open a **new** Command Prompt.
(Avoid `setx PATH ...`, which can cut long PATH values short.)

## Configuration files you should know

| File | Created by | Purpose |
|---|---|---|
| `%APPDATA%\MultiChain\<chain>\params.dat` | `multichain-util create` | Blockchain parameters (consensus, permissions, ports). Fixed after the first `multichaind` run |
| `%APPDATA%\MultiChain\<chain>\multichain.conf` | `multichain-util create` | Node settings: `rpcuser`, `rpcpassword`, and optional `rpcallowip`, `rpcport`, `port` |
| `%APPDATA%\MultiChain\multichain.conf` | `multichain-util create` | Settings shared by all chains (empty by default) |

Common `multichain.conf` additions (stop the node, edit the file, start again):

```ini
rpcallowip=192.168.1.0/24   # let other PCs on the LAN call the API (default: this PC only)
rpcport=6724                # override the RPC port from params.dat
port=6725                   # override the peer-to-peer port from params.dat
```

## Windows firewall

The first time `multichaind` runs, Windows may ask whether to allow it on the network. Click **Allow**
(Private networks). You need this only if a second computer will connect to your node.

## Optional: use the helper scripts

Everything is in [`scripts/windows/`](../scripts/windows). Edit `settings.txt` if your folders change:

```ini
MC_DIR=C:\Users\BK-PC\Downloads\Programs\multichain-windows-2.3.3
PHP_EXE=C:\inetpub\php\php-8.4\php.exe
CHAIN=chain1
WEB_PORT=8080
MC_DATA=
```

| Script | Does |
|---|---|
| `00-open-terminal.bat` | Opens a Command Prompt with MultiChain and PHP on PATH |
| `01-create-chain.bat [name]` | `multichain-util create chain1`, lists the files, prints the answers |
| `02-start-node.bat [name]` | Starts `multichaind chain1` in its own window |
| `03-show-answers.bat [name]` | Prints chain-name, protocol-version, ports and consensus from `params.dat` (and live `getinfo`) |
| `04-lab-walkthrough.bat [name]` | Runs the lab commands step by step (addresses, permissions, assets, streams, blocks) |
| `05-web-demo.bat [name]` | Writes `web-demo\config.txt` and opens the Web Demo at http://127.0.0.1:8080/ |
| `06-stop-node.bat [name]` | `multichain-cli chain1 stop` |
| `99-reset-chain.bat [name]` | Stops the node and **deletes** the chain folder (asks first), to practise again |

You can double-click the scripts or run them from Command Prompt. In the exam, **type the real commands
yourself** ([02](02-sample-question-create-chain1.md), [03](03-start-node-and-initialize.md),
[04](04-lab-commands.md)). The scripts are for practice and for checking your answers.
