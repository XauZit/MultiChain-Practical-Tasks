# 6. Viva / explanation questions

Short answers to the "explain the steps you performed" part of the assessment.

### What is MultiChain?
An open-source platform for building **private, permissioned blockchains**, based on Bitcoin Core.
Compared with Bitcoin it adds permissions (who may connect, send, mine, ...), native assets, streams
(key-value data storage) and a round-robin consensus with no expensive mining.

### What do the three programs do?
- `multichain-util`: creates the chain's parameter file (`create`) or copies one (`clone`).
- `multichaind`: the node. It creates the genesis block on first run, then validates, mines and stores
  blocks and serves the JSON-RPC API.
- `multichain-cli`: a client that sends API commands to the node (`getinfo`, `grant`, `issue`, ...).

### What happens when you run `multichain-util create chain1`?
It creates the folder `chain1` in the MultiChain data directory (`%APPDATA%\MultiChain` on Windows,
`~/.multichain` on Linux) with:
- `params.dat`: all blockchain parameters with default values, plus random ones (network/RPC port,
  network magic bytes, address version bytes)
- `multichain.conf`: the RPC username and a random password.

**No block exists yet.** The genesis block is created the first time `multichaind chain1` runs.

### Why can params.dat only be edited before the first start?
The genesis block contains a hash of the parameters (`chain-params-hash`). Every node checks its
parameters against it, so changing them later would create a different, incompatible chain. Some values
can be changed later through an admin-approved **upgrade** (`create upgrade ...`).

### What is the protocol version?
The version of the MultiChain network protocol the chain was created with: **20013** for MultiChain
2.3.x. It decides which features exist (for example, smart filters need 20004 or later). The software
version (2.3.3) is not the same thing as the protocol version (20013).

### Network port vs RPC port?
- **network-port** (`default-network-port`): peer-to-peer port that other **nodes** use to connect and
  sync blocks (`multichaind chain1@<ip>:<network-port>`).
- **rpc-port** (`default-rpc-port` = network-port − 1): JSON-RPC **API** port used by `multichain-cli`
  and apps such as the Web Demo. By default only the same computer may use it (`rpcallowip` widens this).

Both are chosen at random when the chain is created, so different chains don't clash.

### What consensus does MultiChain use?
**Round-robin mining among permitted miners ("mining diversity")**, a Proof-of-Authority-style
mechanism:
- Only addresses with the `mine` permission can create blocks.
- `mining-diversity = 0.3`: a miner must wait until 30% of active miners have mined before it may mine
  again. This stops one miner from taking control.
- Proof of work is minimal (`pow-minimum-bits = 8`) and never gets harder. Security comes from the
  permissions, not from computing power.
- Admin changes need **admin consensus** (e.g. `admin-consensus-admin = 0.5`: 50% of admins must agree).
- Blocks every ~15 s (`target-block-time = 15`). Transactions are final quickly, with no
  energy-intensive mining.

### What is the genesis block?
Block 0. On the first run of `multichaind chain1`, the node creates block 0 and the node's first address
becomes the **admin** with every permission. Its details (`genesis-hash`, `genesis-pubkey`, ...) are
then written into `params.dat`.

### Why is a newly created address unable to do anything?
`anyone-can-* = false` by default. MultiChain is **permissioned**, so an admin must `grant` permissions
(e.g. `grant <addr> connect,send,receive`).

### What are assets and streams?
- **Asset**: a token issued on the chain (`issue`). It can be transferred (`sendasset`) and, if open,
  issued again (`issuemore`). Every transfer is a blockchain transaction.
- **Stream**: an append-only key-value database on the chain (`create stream`, `publish`,
  `liststreamitems`). Items can be hex, JSON or text, and can be stored off-chain.
- The **root** stream is created automatically with every chain.

### Why does `-daemon` behave differently on Windows?
On Linux, `-daemon` runs the node in the background. On Windows the option is ignored and the node runs
in the foreground of its Command Prompt window, so you open a second window for `multichain-cli`.

### How does the Web Demo talk to MultiChain?
PHP sends **JSON-RPC over HTTP** (with the curl extension) to `127.0.0.1:<rpc-port>`, authenticated with
`rpcuser`/`rpcpassword` from `multichain.conf`. It uses the same API as `multichain-cli`.

### How would a second node join?
`multichaind chain1@<first-node-ip>:<network-port>` on the second PC. It downloads `params.dat`, prints
its address and waits. The admin runs `grant <that-address> connect` (plus `send,receive` if needed).
Then the second node is started again with `multichaind chain1`.

### MultiChain vs public blockchains (Bitcoin/Ethereum)
| | MultiChain | Bitcoin / Ethereum |
|---|---|---|
| Access | Permissioned (private) | Public (anyone) |
| Consensus | Round-robin among permitted miners | Proof of Work / Proof of Stake |
| Fees / mining reward | None by default | Required |
| Assets / data | Native assets and streams | Smart contracts / tokens |
| Speed | ~15 s blocks, configurable | Slower, not configurable |
