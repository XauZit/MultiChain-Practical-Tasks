# MultiChain Practical Tasks

Preparation for **Section 2: Hands-on MultiChain Lab Assessment (7.5 marks)**: installing and
configuring MultiChain, creating and initialising a blockchain, running the lab commands, and the
MultiChain Web Demo. Written for **Windows** with **MultiChain 2.3.3** and **PHP 8.4**, with Linux
equivalents where they differ.

| Your setup | |
|---|---|
| MultiChain | `C:\Users\BK-PC\Downloads\Programs\multichain-windows-2.3.3\` |
| PHP | `C:\inetpub\php\php-8.4\php.exe` |
| Chain data | `%APPDATA%\MultiChain\chain1\` (Windows uses this instead of `~/.multichain`) |

## Sample question answer

> `multichain-util create chain1`: write chain-name, protocol-version, network-port, rpc-port,
> consensus mechanism.

| | |
|---|---|
| **chain-name** | `chain1` |
| **protocol-version** | `20013` |
| **network-port** | `default-network-port` from **your** `params.dat` (random, e.g. `6725`) |
| **rpc-port** | `default-rpc-port` from **your** `params.dat` (= network-port − 1, e.g. `6724`) |
| **consensus mechanism** | Round-robin permissioned mining ("mining diversity", Proof-of-Authority style), `mining-diversity = 0.3` |

Read your own ports in the exam:

```bat
findstr /b "chain-name protocol-version default-network-port default-rpc-port mining-diversity" %APPDATA%\MultiChain\chain1\params.dat
```

Full worked answer with outputs and explanation: **[docs/02-sample-question-create-chain1.md](docs/02-sample-question-create-chain1.md)**

## Exam tasks

| Task | | Guide |
|---|---|---|
| 1 | Connect your chain with the MultiChain Web Demo | ✅ [docs/05-web-demo.md](docs/05-web-demo.md) |
| 2 | Create the **Goffycoin** asset in the web demo and send it to another address | **[docs/09-task-2-goffycoin-asset.md](docs/09-task-2-goffycoin-asset.md)** (step-by-step with screenshots) |
| 3, 4 | Assigned in class | [docs/08-tasks-3-and-4.md](docs/08-tasks-3-and-4.md) |

## Exam-day sequence (type these yourself)

```bat
:: window 1
cd /d C:\Users\BK-PC\Downloads\Programs\multichain-windows-2.3.3
multichain-util create chain1
dir %APPDATA%\MultiChain\chain1
findstr /b "chain-name protocol-version default-network-port default-rpc-port mining-diversity" %APPDATA%\MultiChain\chain1\params.dat
multichaind chain1 -daemon

:: window 2 (the node keeps window 1 busy on Windows)
cd /d C:\Users\BK-PC\Downloads\Programs\multichain-windows-2.3.3
multichain-cli chain1 getinfo
multichain-cli chain1 getblockchainparams
```

## Contents

| Guide | Covers |
|---|---|
| [01 Install and configure](docs/01-install-and-configure.md) | Unzipping, PATH, config files, firewall, helper scripts |
| [02 Sample question: create chain1](docs/02-sample-question-create-chain1.md) | **The answer sheet**, generated files, every `params.dat` section explained |
| [03 Start node and initialise](docs/03-start-node-and-initialize.md) | `multichaind`, genesis block, files after start, `getinfo`, second node |
| [04 Lab commands](docs/04-lab-commands.md) | Addresses, permissions, assets, streams, blocks, peers, with Windows quoting |
| [05 Web Demo (PHP 8.4)](docs/05-web-demo.md) | Setting up and demonstrating multichain-web-demo |
| [06 Viva questions](docs/06-viva-questions.md) | Short explanations for "explain the steps you performed" |
| [07 Troubleshooting](docs/07-troubleshooting.md) | Common errors and fixes |
| [08 Exam tasks](docs/08-tasks-3-and-4.md) | Task list and status (tasks 3 and 4 assigned in class) |
| [09 Task 2: Goffycoin asset](docs/09-task-2-goffycoin-asset.md) | Issue Goffycoin in the web demo and send it to another address, with screenshots and CLI checks |
| [reference/params.dat.sample](reference/params.dat.sample) | A full `params.dat` exactly as MultiChain 2.3.3 writes it |

## Helper scripts (Windows): `scripts/windows/`

Double-click them or run them from Command Prompt. Paths come from
[`scripts/windows/settings.txt`](scripts/windows/settings.txt), which is already set to your folders.

| Script | Does |
|---|---|
| `00-open-terminal.bat` | Command Prompt with `multichain-*` and `php` on PATH |
| `01-create-chain.bat` | `multichain-util create chain1` + lists files + prints the answers |
| `02-start-node.bat` | `multichaind chain1` in its own window |
| `03-show-answers.bat` | Answer sheet from your `params.dat` (+ live `getinfo` if the node runs) |
| `04-lab-walkthrough.bat` | Runs the lab commands step by step and shows each command |
| `05-web-demo.bat` | Configures and opens the Web Demo on http://127.0.0.1:8080/ |
| `06-stop-node.bat` | `multichain-cli chain1 stop` |
| `99-reset-chain.bat` | Deletes the chain (asks first) so you can practise again |

Each script takes an optional chain name, e.g. `01-create-chain.bat chain2`.

## Web Demo

[`web-demo/`](web-demo) is [MultiChain/multichain-web-demo](https://github.com/MultiChain/multichain-web-demo)
with fixes for PHP 8 (the original crashes on PHP 8.x). See
[web-demo/PHP8-CHANGES.md](web-demo/PHP8-CHANGES.md). Licensed AGPL-3.0 by Coin Sciences Ltd.

## How this was verified

No Windows PC or MultiChain binary was available while this was written, so:

- Facts and messages come from the MultiChain **2.3.x source code**, including the `params.dat`
  sample, which was produced by re-running MultiChain's own parameter writer.
- The web demo was tested page by page on **PHP 8.3 and PHP 8.4** against a simulated MultiChain node.
- The PowerShell helpers were tested with PowerShell 7 against the same simulated node.
- The `.bat` launchers have **not** been run (no Windows `cmd` available). They are short wrappers.

Details: [dev/README.md](dev/README.md).
