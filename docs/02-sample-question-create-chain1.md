# Sample Question: Creating a MultiChain Instance

> **Command:** `multichain-util create chain1`
>
> 1. Run the command to create a new blockchain named `chain1`.
> 2. Note the configuration files generated in the `.multichain` directory.
> 3. Identify key attributes such as protocol-version, chain name, and default parameters.
> 4. Write the output for: chain-name, protocol-version, network-port, rpc-port, consensus mechanism.

---

## Answer sheet (copy this into your exam answer)

| Attribute | Value | Where it comes from |
|---|---|---|
| **chain-name** | `chain1` | `chain-name = chain1` in `params.dat` (the name you passed to `multichain-util create`) |
| **protocol-version** | `20013` | `protocol-version = 20013` in `params.dat`; MultiChain 2.3.3 prints `latest protocol 20013` |
| **network-port** | the value of `default-network-port` in **your** `params.dat`, e.g. `6725` | Picked at random when the chain is created, so every PC gets a different number |
| **rpc-port** | the value of `default-rpc-port` in **your** `params.dat`, e.g. `6724` | Always **network-port − 1** |
| **consensus mechanism** | **Round-robin permissioned mining ("mining diversity")**, a Proof-of-Authority-style consensus. Default `mining-diversity = 0.3` | Only addresses with `mine` permission can create blocks, and they take turns |

> ⚠️ **Do not copy the port numbers from this page.** `multichain-util` picks them at random
> (`network-port` is always odd and `rpc-port = network-port − 1`). Read your own values with the
> `findstr` command in Step 3 below, or run `scripts\windows\03-show-answers.bat`.

### Explaining the consensus mechanism (for the viva)

- MultiChain is a **permissioned** blockchain. Only addresses that have the **`mine`** permission can
  create blocks. On a new chain, only the first (admin) address has it.
- Miners take turns (**round robin**). `mining-diversity = 0.3` means that after mining a block, a miner
  must wait until **30% of the active miners** have mined before it may mine again
  (rule: *"Miners must wait `<mining-diversity>` × `<active miners>` between blocks"*). One miner cannot
  take over the chain.
- With only one node (your PC), that node mines every block, about every **15 seconds**
  (`target-block-time = 15`).
- There is technically a proof-of-work step, but it is tiny (`pow-minimum-bits = 8`) and never gets
  harder (`target-adjust-freq = -1`). It is not what secures the chain. The permissions are.
- Admin changes need **admin consensus**: `admin-consensus-admin = 0.5` means 50% of the admins must
  agree before admin permissions change.
- The first `setup-first-blocks = 60` blocks are a setup phase where mining diversity is not enforced.

---

## Step-by-step (Windows, your PC)

Open **Command Prompt** (`Win + R` → `cmd` → Enter) and go to your MultiChain folder:

```bat
cd /d C:\Users\BK-PC\Downloads\Programs\multichain-windows-2.3.3
```

### Step 1: Create the chain

```bat
multichain-util create chain1
```

Expected output (message text taken from the MultiChain 2.3.3 source; the path is your own `%APPDATA%` folder):

```text
MultiChain 2.3.3 Utilities (latest protocol 20013)

Blockchain parameter set was successfully generated.
You can edit it in C:\Users\BK-PC\AppData\Roaming\MultiChain\chain1\params.dat before running multichaind for the first time.

To generate blockchain please run "multichaind chain1 -daemon".
```

If you see `Cannot create chain parameter set, file ... already exists`, then `chain1` already exists.
Use another name (`multichain-util create chain2`) or delete the folder with
`scripts\windows\99-reset-chain.bat`.

### Step 2: Look at the generated files

The question says "`.multichain` directory". That is the **Linux/macOS** location (`~/.multichain/`).
**On Windows, MultiChain uses `%APPDATA%\MultiChain`** instead
(`C:\Users\BK-PC\AppData\Roaming\MultiChain`).

```bat
cd /d %APPDATA%\MultiChain
dir /s /b
```

```text
C:\Users\BK-PC\AppData\Roaming\MultiChain\chain1
C:\Users\BK-PC\AppData\Roaming\MultiChain\multichain.conf
C:\Users\BK-PC\AppData\Roaming\MultiChain\chain1\multichain.conf
C:\Users\BK-PC\AppData\Roaming\MultiChain\chain1\params.dat
```

| File | What it is |
|---|---|
| `MultiChain\multichain.conf` | Global settings shared by all chains. Created empty. |
| `MultiChain\chain1\params.dat` | **The blockchain parameters**: chain name, protocol version, ports, permissions, consensus rules. Can be edited only *before* the first `multichaind chain1`. |
| `MultiChain\chain1\multichain.conf` | Settings for this node: `rpcuser=multichainrpc` and a random `rpcpassword=...` used by `multichain-cli` and the Web Demo |

```bat
type chain1\multichain.conf
```

```text
rpcuser=multichainrpc
rpcpassword=<random 32+ character password>
```

### Step 3: Read the answers out of params.dat

```bat
findstr /b "chain-name protocol-version default-network-port default-rpc-port mining-diversity target-block-time" chain1\params.dat
```

Example output (your two port numbers will differ):

```text
target-block-time = 15                  # Target time between blocks (transaction confirmation delay), seconds. (2 - 86400)
mining-diversity = 0.3                  # Miners must wait <mining-diversity>*<active miners> between blocks. (0 - 1)
default-network-port = 6725             # Default TCP/IP port for peer-to-peer connection with other nodes.
default-rpc-port = 6724                 # Default TCP/IP port for incoming JSON-RPC API requests.
chain-name = chain1                     # Chain name, used as first argument for multichaind and multichain-cli.
protocol-version = 20013                # Protocol version at the moment of blockchain genesis.
```

To see the whole file: `notepad chain1\params.dat` (or `type chain1\params.dat | more`).

PowerShell equivalent:

```powershell
Select-String -Path "$env:APPDATA\MultiChain\chain1\params.dat" -Pattern '^(chain-name|protocol-version|default-network-port|default-rpc-port|mining-diversity) '
```

### Step 4 (optional): Confirm from the running node

```bat
cd /d C:\Users\BK-PC\Downloads\Programs\multichain-windows-2.3.3
multichaind chain1
```

On Windows `-daemon` is ignored. The node keeps running in this window, so **open a second Command
Prompt** for the next commands. See [03-start-node-and-initialize.md](03-start-node-and-initialize.md).

```bat
multichain-cli chain1 getinfo
multichain-cli chain1 getblockchainparams
```

`getinfo` shows `"chainname": "chain1"`, `"protocolversion": 20013`, `"port": <network-port>`.
`getblockchainparams` shows the same values as `params.dat`.

---

## params.dat explained (default parameters)

Full sample file: [`reference/params.dat.sample`](../reference/params.dat.sample). It was generated by
re-running MultiChain 2.3.3's own parameter table and file writer
([`dev/emulate_params.py`](../dev/emulate_params.py)), so the layout and defaults match the real file.
Only the random values differ (ports, magic bytes, address version bytes).

The file is split into sections:

| Section | Key defaults | Meaning |
|---|---|---|
| **Basic chain parameters** | `chain-protocol = multichain`, `chain-description = MultiChain chain1`, `root-stream-name = root`, `root-stream-open = true`, `target-block-time = 15`, `maximum-block-size = 8388608` | Chain type, description, built-in `root` stream, 15-second blocks, 8 MB maximum block size |
| **Global permissions** | `anyone-can-connect = false`, `anyone-can-send = false`, `anyone-can-receive = false`, `anyone-can-create = false`, `anyone-can-issue = false`, `anyone-can-mine = false`, `anyone-can-activate = false`, `anyone-can-admin = false` | **Private, permissioned chain**: everything must be granted by an admin |
| **Consensus requirements** | `setup-first-blocks = 60`, `mining-diversity = 0.3`, `admin-consensus-upgrade/txfilter/admin/activate/mine = 0.5`, `admin-consensus-create/issue = 0.0` | Round-robin mining rules and how many admins must agree on changes |
| **Defaults for node runtime parameters** | `lock-admin-mine-rounds = 10`, `mining-requires-peers = true`, `mine-empty-rounds = 10`, `mining-turnover = 0.5` | How the node mines (it pauses after 10 empty rounds) |
| **Native blockchain currency** | `initial-block-reward = 0`, `minimum-relay-fee = 0`, `native-currency-multiple = 100000000` | No mining reward and **no transaction fees** by default |
| **Advanced mining parameters** | `skip-pow-check = false`, `pow-minimum-bits = 8`, `target-adjust-freq = -1` | Very small proof of work that never gets harder |
| **Standard transaction definitions** | `max-std-tx-size = 4194304`, `max-std-op-returns-count = 32`, `max-std-op-return-size = 2097152`, `max-std-element-size = 40000` | Size limits for transactions and metadata |
| **Generated by multichain-util** | `default-network-port`, `default-rpc-port`, `chain-name`, `protocol-version`, `network-message-start`, `address-pubkeyhash-version`, `address-scripthash-version`, `private-key-version`, `address-checksum-value` | Random or derived values unique to this chain (ports, network "magic" bytes, address format bytes) |
| **Generated by multichaind** | `genesis-pubkey`, `genesis-version`, `genesis-timestamp`, `genesis-nbits`, `genesis-nonce`, `genesis-pubkey-hash`, `genesis-hash`, `chain-params-hash` | Show `[null]` until the node is started for the first time and mines the genesis block |

The header of a freshly created file says:

```text
# ==== MultiChain configuration file ====

# Created by multichain-util
# Protocol version: 20013

# This parameter set is properly GENERATED.
# To generate network please run "multichaind chain1".
```

After the first `multichaind chain1`, it changes to `This parameter set is VALID.` and the
`genesis-*` values are filled in. From then on, the parameters can no longer be changed for this chain.

---

## Same task on Linux (if the lab PC runs Linux)

```bash
multichain-util create chain1
ls -la ~/.multichain/chain1/
cat ~/.multichain/chain1/multichain.conf
grep -E '^(chain-name|protocol-version|default-network-port|default-rpc-port|mining-diversity) ' ~/.multichain/chain1/params.dat
multichaind chain1 -daemon
multichain-cli chain1 getinfo
```

On Linux `-daemon` works: the node runs in the background and your prompt comes back.
