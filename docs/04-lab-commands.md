# 4. MultiChain lab commands

All commands use the form:

```text
multichain-cli <chain-name> <command> [arguments...]
```

The node must be running (`multichaind chain1` in another window). Run the commands from the MultiChain
folder, or from the window opened by `scripts\windows\00-open-terminal.bat`.

`scripts\windows\04-lab-walkthrough.bat` runs the most important ones below in order, against your
node, and prints each command exactly as you would type it.

> **Windows quoting rule:** JSON arguments go inside double quotes, and every inner `"` becomes `\"`:
> ```bat
> multichain-cli chain1 publish stream1 key2 "{\"json\":{\"name\":\"Ali\",\"marks\":85}}"
> ```
> On Linux use single quotes instead: `'{"json":{"name":"Ali","marks":85}}'`.

In the examples, `ADMIN` means your first address (from `getaddresses`) and `ADDR2` means a second
address you create. Replace them with the real addresses (they start with `1...`).

---

## 1. Help and node information

| Command | Purpose |
|---|---|
| `multichain-cli chain1 help` | List every API command |
| `multichain-cli chain1 help issue` | Arguments and examples for one command |
| `multichain-cli chain1 getinfo` | Version, protocol, chain name, ports, block count, peers |
| `multichain-cli chain1 getblockchainparams` | All parameters from `params.dat` (consensus, permissions, ports) |
| `multichain-cli chain1 getruntimeparams` | Node runtime settings (mining, autosubscribe, etc.) |
| `multichain-cli chain1 getblockchaininfo` | Chain height, best block hash |

## 2. Addresses and wallet

```bat
multichain-cli chain1 getaddresses
multichain-cli chain1 getnewaddress
multichain-cli chain1 listaddresses
multichain-cli chain1 validateaddress ADDR2
multichain-cli chain1 getwalletinfo
```

- `getaddresses` returns `["1...admin..."]` on a new chain. That address mined the genesis block and holds
  every permission.
- `getnewaddress` creates a new key pair and returns its address. It has **no permissions** until granted.

## 3. Permissions

Global permissions: `connect, send, receive, issue, create, mine, activate, admin`.

```bat
multichain-cli chain1 listpermissions
multichain-cli chain1 listpermissions all ADMIN
multichain-cli chain1 grant ADDR2 connect,send,receive
multichain-cli chain1 grant ADDR2 issue,create
multichain-cli chain1 listpermissions connect,send,receive ADDR2
multichain-cli chain1 revoke ADDR2 issue
```

Per-stream and per-asset permissions use `name.permission`:

```bat
multichain-cli chain1 grant ADDR2 stream1.write
multichain-cli chain1 grant ADDR2 asset1.send,asset1.receive
```

`grant` and `revoke` return a **transaction id**, because permission changes are recorded on the
blockchain.

| Permission | Allows |
|---|---|
| connect | Connect to the network and read the chain |
| send / receive | Send / receive assets and transactions |
| issue | Issue assets |
| create | Create streams |
| mine | Create blocks (take part in consensus) |
| activate | Grant / revoke connect, send, receive |
| admin | Grant / revoke everything (changes need admin consensus) |

## 4. Assets

```bat
multichain-cli chain1 issue ADMIN asset1 1000 0.01
multichain-cli chain1 issue ADMIN "{\"name\":\"asset2\",\"open\":true}" 5000 1
multichain-cli chain1 listassets
multichain-cli chain1 listassets asset1
multichain-cli chain1 gettotalbalances
multichain-cli chain1 getaddressbalances ADMIN
multichain-cli chain1 sendasset ADDR2 asset1 100
multichain-cli chain1 getaddressbalances ADDR2
multichain-cli chain1 sendassetfrom ADDR2 ADMIN asset1 10
multichain-cli chain1 issuemore ADMIN asset2 500
multichain-cli chain1 subscribe asset1
multichain-cli chain1 listassettransactions asset1
```

- `issue ADMIN asset1 1000 0.01`: issue 1000 units of `asset1` to ADMIN. `0.01` is the smallest unit,
  so 1 unit = 100 raw units.
- An asset is **closed** by default, meaning no more can ever be issued. Use the JSON form with
  `"open":true` if you need `issuemore` later.
- `sendasset` needs ADDR2 to have the **receive** permission. `sendassetfrom ADDR2 ...` needs ADDR2 to
  have **send**.
- `listassettransactions` works only after `subscribe asset1`.

## 5. Streams (data storage)

```bat
multichain-cli chain1 create stream stream1 true
multichain-cli chain1 create stream stream2 "{\"restrict\":\"write\"}"
multichain-cli chain1 liststreams
multichain-cli chain1 subscribe stream1
multichain-cli chain1 publish stream1 key1 48656c6c6f20576f726c64
multichain-cli chain1 publish stream1 key2 "{\"json\":{\"name\":\"Ali\",\"marks\":85}}"
multichain-cli chain1 publish stream1 key3 "{\"text\":\"MultiChain lab\"}"
multichain-cli chain1 publish stream1 "[\"key4\",\"key5\"]" "{\"text\":\"two keys\"}"
multichain-cli chain1 publishfrom ADDR2 stream1 key6 "{\"text\":\"from ADDR2\"}"
multichain-cli chain1 liststreamitems stream1
multichain-cli chain1 liststreamkeyitems stream1 key2
multichain-cli chain1 liststreampublisheritems stream1 ADMIN
multichain-cli chain1 liststreamkeys stream1
multichain-cli chain1 liststreampublishers stream1
```

- `create stream stream1 true`: `true` means **open**, so anyone with `send` can publish. `false` (or
  `{"restrict":"write"}`) means only addresses granted `stream1.write` can publish.
- Data can be **hex** (`48656c6c6f20576f726c64` = "Hello World"), **JSON** (`{"json":{...}}`) or
  **text** (`{"text":"..."}`).
- `publishfrom ADDR2 ...` needs ADDR2 to have `send` (and `stream1.write` if the stream is not open).
- You must `subscribe` before you can read a stream with `liststream...` commands.
- Every chain has a built-in stream called **`root`**.

Text → hex in PowerShell (if you are asked to publish raw hex):

```powershell
-join ([Text.Encoding]::UTF8.GetBytes('Hello World') | ForEach-Object { $_.ToString('x2') })
```

## 6. Blocks and transactions

```bat
multichain-cli chain1 getblockcount
multichain-cli chain1 getbestblockhash
multichain-cli chain1 getblockhash 0
multichain-cli chain1 getblock 0
multichain-cli chain1 listblocks 0-5
multichain-cli chain1 listwallettransactions 5
multichain-cli chain1 getwallettransaction TXID
multichain-cli chain1 getrawtransaction TXID 1
multichain-cli chain1 getmempoolinfo
```

- Block **0** is the genesis block. `getblock 0` shows its `miner` (the admin address).
- `listblocks 0-5` lists blocks 0 to 5 with their miner and transaction count. With one node, every block
  is mined by your admin address, which shows the round-robin with a single miner.
- `TXID` is any transaction id returned by `grant`, `issue`, `sendasset`, `publish`, etc.

## 7. Network / peers

```bat
multichain-cli chain1 getpeerinfo
multichain-cli chain1 getnetworkinfo
multichain-cli chain1 addnode 192.168.1.20:6725 onetry
```

## 8. Node control

```bat
multichain-cli chain1 pause mining
multichain-cli chain1 resume mining
multichain-cli chain1 stop
```

## Interactive mode (no need to repeat `multichain-cli chain1`)

```bat
multichain-cli chain1
```

Then type commands directly (`getinfo`, `listassets`, ...) and type `exit` (or `quit` / `bye`) to leave.

---

## Typical errors

| Error | Cause / fix |
|---|---|
| `Could not connect to the server 127.0.0.1:<port>` | Node not running. Start `multichaind chain1` and wait for `Node ready.` |
| `error code: -704` e.g. `Destination address doesn't have receive permission` | Grant the missing permission first (`grant ADDR2 receive` / `send` / `issue` / `create` / `stream1.write`) |
| `error code: -705` `Entity with this name already exists` | Asset/stream name already used. Pick another name or reuse the existing one |
| `error code: -6` `Insufficient funds, ...` | The address does not hold enough of the asset. Check `getaddressbalances` |
| `error code: -703` `Not subscribed to this stream` / `asset` | Run `subscribe stream1` (or `subscribe asset1`) first |
| JSON errors on Windows | Check the quoting: the outer `"..."` and every inner `\"` |
