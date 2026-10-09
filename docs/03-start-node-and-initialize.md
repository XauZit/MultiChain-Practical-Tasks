# 3. Start the node and initialise the blockchain

Creating the chain (`multichain-util create chain1`) only writes `params.dat`. The blockchain
**exists** only after the node starts for the first time and mines the **genesis block**.

## Start the node

```bat
cd /d C:\Users\BK-PC\Downloads\Programs\multichain-windows-2.3.3
multichaind chain1 -daemon
```

> **Windows note:** `-daemon` is ignored on Windows (the MultiChain source skips daemon mode on
> Windows), so the node runs in the **foreground**. Leave this window open and run every
> `multichain-cli` command from a **second** Command Prompt. Closing the window or pressing `Ctrl+C`
> stops the node. `scripts\windows\02-start-node.bat` opens the node in its own window for you.

Expected first-run output (message text from the MultiChain 2.3.3 source; your IP address and ports
will differ):

```text
MultiChain 2.3.3 Daemon (Community Edition, latest protocol 20013)

Looking for genesis block...
Genesis block found

Other nodes can connect to this node using:
multichaind chain1@192.168.1.10:6725

Listening for API requests on port 6724 (local only - see rpcallowip setting)

Node ready.
```

What each line means:

| Line | Meaning |
|---|---|
| `Looking for genesis block... Genesis block found` | First run: the node mined block 0 using the parameters in `params.dat`. Its own first address becomes the **admin** with every permission |
| `multichaind chain1@<ip>:<network-port>` | The command **another computer** runs to join this chain (it then needs `connect` permission) |
| `Listening for API requests on port <rpc-port>` | `multichain-cli` and the Web Demo talk to this port. By default only this PC can use it |
| `Node ready.` | You can now send commands |

## Files after initialisation

```bat
dir %APPDATA%\MultiChain\chain1
```

New files and folders appear next to `params.dat` and `multichain.conf`:

| Item | Contents |
|---|---|
| `blocks\` | Raw block files |
| `chainstate\` | Current state (unspent outputs) database |
| `wallet\`, `wallet.dat` | This node's private keys and wallet transactions |
| `permissions.dat`, `permissions.db` | Who holds which permission |
| `entities.dat`, `entities.db` | Assets and streams |
| `peers.dat` | Known peer nodes |
| `debug.log` | Node log. Check it when something goes wrong |
| `params.dat` | Now says `This parameter set is VALID.` and has the `genesis-*` values filled in |

## Check the node (second Command Prompt)

```bat
cd /d C:\Users\BK-PC\Downloads\Programs\multichain-windows-2.3.3
multichain-cli chain1 getinfo
```

```json
{
    "version" : "2.3.3",
    "nodeversion" : 20303901,
    "edition" : "Community",
    "protocolversion" : 20013,
    "chainname" : "chain1",
    "description" : "MultiChain chain1",
    "protocol" : "multichain",
    "port" : 6725,
    "setupblocks" : 60,
    "nodeaddress" : "chain1@192.168.1.10:6725",
    "burnaddress" : "1XXXXXXXX...",
    "incomingpaused" : false,
    "miningpaused" : false,
    "offchainpaused" : false,
    "walletversion" : 60000,
    "balance" : 0.00000000,
    "walletdbversion" : 3,
    "reindex" : false,
    "blocks" : 3,
    "chainrewards" : 0.00000000,
    "streams" : 1,
    "timeoffset" : 0,
    "connections" : 0,
    "proxy" : "",
    "difficulty" : 0.00000006,
    "testnet" : false,
    "keypoololdest" : 1760000000,
    "keypoolsize" : 2,
    "paytxfee" : 0.00000000,
    "relayfee" : 0.00000000,
    "errors" : ""
}
```

(Example values. `blocks` goes up by about one every 15 seconds while the node runs.)

Before the JSON, `multichain-cli` also prints the request it sent, for example
`{"method":"getinfo","params":[],"id":"...","chain_name":"chain1"}`. That is normal.

More checks:

```bat
multichain-cli chain1 getblockchainparams
multichain-cli chain1 getaddresses
multichain-cli chain1 listpermissions
multichain-cli chain1 getblockcount
```

`listpermissions` shows that the single admin address holds `connect, send, receive, issue, create,
mine, activate, admin`.

## Stop / restart

```bat
multichain-cli chain1 stop
multichaind chain1
```

On later starts there is no "Genesis block found" line. The node loads the existing chain.

## Connecting a second node (if asked)

On the second PC (MultiChain installed the same way):

```bat
multichaind chain1@192.168.1.10:6725
```

It prints its own address and asks for permission. On **your** (admin) node:

```bat
multichain-cli chain1 grant <address-printed-by-node-2> connect
```

Then start the second node again: `multichaind chain1`. Both PCs must reach each other on the
network port, so allow it through the Windows firewall.
