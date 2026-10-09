# 5. MultiChain Web Demo (PHP 8.4)

The [MultiChain Web Demo](https://github.com/MultiChain/multichain-web-demo) is a PHP website that
controls your node through its JSON-RPC API: addresses, permissions, assets, streams and filters, all
from a browser.

## Why this repo has its own copy

The original demo was last updated in 2021 and was written for PHP 5/7. **On PHP 8.x it crashes**:

| Page | Crash on PHP 8 (original code) | Fixed here |
|---|---|---|
| Node (home) | Fatal `count(): Argument #1 must be of type Countable\|array, null given`, as soon as an address has no permissions (e.g. right after **Get new address**) | ✅ |
| Issue Asset | Same fatal error once any asset exists without a file attachment | ✅ |
| Update | Same fatal error | ✅ |
| Every page | `Deprecated: strlen()/htmlspecialchars(): Passing null...` and `Warning: Undefined array key` messages | ✅ |
| Labels | Garbled label or warnings if a JSON/text item is published to the `root` stream | ✅ |

[`web-demo/`](../web-demo) is the original code (commit `582476b`) plus small PHP 8 fixes, listed in
[`web-demo/PHP8-CHANGES.md`](../web-demo/PHP8-CHANGES.md). It was tested on **PHP 8.3.6 and PHP 8.4.25**:
every page and form (new address, grant, label, issue with file, update, send, create stream, publish
hex/JSON/text/file/multi-key, view by key/publisher, offers, filters) ran against a simulated
MultiChain 2.3.3 node with `error_reporting=E_ALL`, with **0 errors** (original code: 51 failures).
See [`dev/README.md`](../dev/README.md).

## Quick start (script)

1. Start the node: `scripts\windows\02-start-node.bat` (wait for `Node ready.`)
2. Run `scripts\windows\05-web-demo.bat`

The script:
- reads `rpcuser` and `rpcpassword` from `%APPDATA%\MultiChain\chain1\multichain.conf`
- reads `default-rpc-port` from `%APPDATA%\MultiChain\chain1\params.dat`
- writes `web-demo\config.txt`
- checks that PHP has the **curl** extension (and turns it on for this run if `php.ini` doesn't)
- starts `php -S 127.0.0.1:8080 -t web-demo` and opens http://127.0.0.1:8080/

Press `Ctrl+C` in that window to stop the web server.

## Manual setup (what to explain / do in the exam)

### 1. Node running

```bat
cd /d C:\Users\BK-PC\Downloads\Programs\multichain-windows-2.3.3
multichaind chain1
```

The web server runs on the same PC as the node, so no `rpcallowip` change is needed.

### 2. Get the RPC credentials and port

```bat
type %APPDATA%\MultiChain\chain1\multichain.conf
findstr /b "default-rpc-port" %APPDATA%\MultiChain\chain1\params.dat
```

### 3. Create `web-demo\config.txt`

```bat
cd /d <this-repo>\web-demo
copy config-example.txt config.txt
notepad config.txt
```

Fill it in with **your** values:

```ini
default.name=chain1 (local node)        # name shown in the web interface
default.rpchost=127.0.0.1               # IP address of the MultiChain node
default.rpcsecure=0                     # 1 = https
default.rpcport=6724                    # default-rpc-port from params.dat
default.rpcuser=multichainrpc           # rpcuser from multichain.conf
default.rpcpassword=PASTE_YOUR_PASSWORD # rpcpassword from multichain.conf
```

`config.txt` contains your API password. It is git-ignored in this repo. Never put it on a public server.

### 4. Make sure PHP has curl

```bat
C:\inetpub\php\php-8.4\php.exe -m | findstr /i curl
```

If nothing is printed, open `C:\inetpub\php\php-8.4\php.ini` and set (remove the leading `;`):

```ini
extension_dir = "C:\inetpub\php\php-8.4\ext"
extension=curl
```

(If there is no `php.ini`, copy `php.ini-development` to `php.ini` first.) Or skip the edit and add
`-d extension_dir=C:\inetpub\php\php-8.4\ext -d extension=curl` to the command in step 5.

### 5. Start the PHP built-in web server

```bat
C:\inetpub\php\php-8.4\php.exe -S 127.0.0.1:8080 -t "<this-repo>\web-demo"
```

Open **http://127.0.0.1:8080/** → click **chain1 (local node)**.

> Using IIS instead (you already have `C:\inetpub`): copy the `web-demo` folder to
> `C:\inetpub\wwwroot\multichain` and open http://localhost/multichain/. This only works if PHP is
> already set up as a FastCGI handler in IIS. The built-in server above needs no IIS setup.

## Tour of the pages (what to demonstrate)

| Page | What it does | Equivalent CLI command |
|---|---|---|
| **Node** | Chain name, version, protocol, node address, blocks, peers. Your addresses with their permissions and balances. **Get new address** | `getinfo`, `getpeerinfo`, `getaddresses`, `getnewaddress`, `getmultibalances` |
| **Permissions** | Grant or revoke connect/send/receive/issue/create/mine/activate/admin | `grantfrom`, `revokefrom`, `listpermissions` |
| **Issue Asset** | Issue an asset with quantity, units, custom fields and an optional file | `issue` / `createrawsendfrom` |
| **Update** | Issue more units of an open asset, update its fields | `issuemore` |
| **Send** | Send asset units between addresses (optionally with metadata) | `sendassetfrom`, `sendwithmetadatafrom` |
| **Create Offer / Accept** | Atomic exchange of assets between two parties | `createrawexchange`, `appendrawexchange` |
| **Create Stream** | Create a stream (open or restricted) | `create stream` |
| **Publish** | Publish text, JSON or a file to a stream under one or more keys | `publishfrom` |
| **View Streams** | Subscribe, list items, filter by key or publisher, download files | `subscribe`, `liststreamitems`, `liststreamkeyitems` |
| **Filters** | Write and test JavaScript transaction/stream filters (smart filters) | `create txfilter`, `testtxfilter` |

**Label** (Node page → *Set label*): publishes a name to the `root` stream so every node shows that
name for the address.

### Suggested 3-minute demo

1. **Node** page: point out `chain1`, protocol `20013`, block count increasing.
2. **Get new address** → new address appears with permissions *none*.
3. **Permissions**: grant `connect, send, receive` to the new address → transaction id shown.
4. **Issue Asset**: `asset1`, quantity 1000, units 0.01 → shows on the Node page under the admin's balances.
5. **Send**: 100 `asset1` to the new address.
6. **Create Stream** `stream1` → **Publish** JSON `{"name":"Ali","marks":85}` with key `student1`.
7. **View Streams** → `stream1` → the item, its key and its publisher.
8. Back in Command Prompt: `multichain-cli chain1 liststreamitems stream1` shows the same data. The web
   demo and the CLI use the same API.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `Error: HTTP 0 ... http://127.0.0.1:6724/` | Node not running, or wrong `rpcport` in `config.txt` |
| `Error: HTTP 401` | Wrong `rpcuser` / `rpcpassword`. Copy them again from `multichain.conf` |
| `This web demo requires the curl extension for PHP` | Enable curl (step 4) |
| Page shows no chains | `config.txt` missing or the `default.rpchost` line is missing |
| `Failed to listen on 127.0.0.1:8080` | Port in use. Use another, e.g. `-S 127.0.0.1:8090` (or change `WEB_PORT` in `scripts\windows\settings.txt`) |
