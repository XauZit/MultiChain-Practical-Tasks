# dev/: how this repo was checked

You don't need this folder for the exam. It shows how the outputs and scripts were verified without a
Windows PC.

| File | Purpose |
|---|---|
| `emulate_params.py` | Re-implements MultiChain 2.3.x's `mc_MultichainParams::Create` + `Write` (from `src/chainparams/params.cpp`) using its parameter table `src/chainparams/paramlist.h`, to produce [`reference/params.dat.sample`](../reference/params.dat.sample) |
| `php8_patch.py` | Applies the PHP 8 fixes to an upstream checkout of multichain-web-demo (see [`web-demo/PHP8-CHANGES.md`](../web-demo/PHP8-CHANGES.md)) |
| `mock_multichain.py` | Small stateful stand-in for a MultiChain 2.3.3 JSON-RPC node (getinfo, permissions, assets, streams, filters, ...) |
| `crawl.sh` | Drives the web demo through every page and form against the mock and fails on any PHP notice, warning, deprecation or fatal error |
| `wasm_shim.py`, `runner.php` | Let `crawl.sh` run the pages on PHP 8.4 (`@php-wasm/cli`) when no native PHP 8.4 is installed |
| `screenshots-task2.js` | Playwright script that clicks through Task 2 (new address → grant → issue Goffycoin → send) and saves the screenshots in [`docs/images/task2/`](../docs/images/task2) |
| `fake_multichain_cli.py` | Stand-in for `multichain-cli.exe` (same argv and stdout/stderr behaviour) to test `scripts/windows/*.ps1` with PowerShell 7 on Linux |

## Reproduce

```bash
# params.dat sample (needs a checkout of github.com/MultiChain/multichain, branch 2.3.x-release)
python3 emulate_params.py <multichain>/src/chainparams/paramlist.h chain1 20013 7 > ../reference/params.dat.sample

# web demo on the local PHP (8.3 here)
./crawl.sh ../web-demo 18080 16724

# web demo on PHP 8.4 via WebAssembly
mkdir /tmp/phpwasm && (cd /tmp/phpwasm && npm init -y && npm i @php-wasm/cli)
PHPWASM=/tmp/phpwasm ./crawl.sh ../web-demo 18081 16725

# Task 2 screenshots (web demo served on :18100 with config.txt pointing at a mock on :16770)
python3 mock_multichain.py 16770 & php -S 127.0.0.1:18100 -t <copy-of-web-demo> &
NODE_PATH=$(npm root -g) node screenshots-task2.js http://127.0.0.1:18100/ ../docs/images/task2
```

Results at the time of writing:

| Code | PHP 8.3.6 | PHP 8.4.25 |
|---|---|---|
| upstream multichain-web-demo `582476b` | 51 failing steps, including fatal `TypeError`s on Node, Issue Asset, Update | same |
| `web-demo/` in this repo | **0** failing steps (50 steps + 13 content checks) | **0** |

The MultiChain source facts used in the docs (protocol `20013`, build `2.3.3`, random port rule
`rpc = network − 1`, `%APPDATA%\MultiChain` data folder, `-daemon` ignored on Windows, console
messages, RPC method names and error codes) were read from the `2.3.x-release` branch of
`MultiChain/multichain`.
