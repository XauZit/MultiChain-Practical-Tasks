# Task 3: Interaction between two MultiChain networks using stream filters

> Using the MultiChain Web Demo interface, configure two independent chains named **PaymentChain** and
> **ServiceChain**. A customer publishes a payment request on PaymentChain. Deduct a 2% service fee, then
> manually relay the remaining payment information to ServiceChain.

Everything below was done **through the web demo pages only**. The screenshots come from this repo's
web demo connected to two simulated MultiChain 2.3.3 nodes, so **your addresses, transaction IDs, block
counts and times will be different**. The pages, fields and buttons are the same. The filter code was run
for real on every test (see [How this was checked](#how-this-was-checked)).

Copy-paste files are in [`tasks/task3-crosschain/`](../tasks/task3-crosschain):
- the filter: [`validate_fee_record.js`](../tasks/task3-crosschain/validate_fee_record.js)
- every JSON record you publish: the [`json/`](../tasks/task3-crosschain/json) folder

## The flow

```mermaid
flowchart LR
  subgraph PC[PaymentChain]
    C[Customer] -- "1 publish REQ001" --> PR[(payment_requests)]
    C -- "2a send 20 PayToken" --> F[Fee Collection]
    C -- "2b send 980 PayToken" --> RC[Relay Custody]
    OP[PaymentChain Admin] -- "3 fee + txids" --> FL[(fee_deduction_logs)]
    OP -- logs --> PA[(crosschain_audit_logs)]
  end
  subgraph SC[ServiceChain]
    SA[ServiceChain Admin] -- "4 receipt REQ001" --> RT[(received_transactions)]
    VF{{validate_fee_record}} -. checks every item .-> RT
    SA -- logs --> SAL[(crosschain_audit_logs)]
  end
  FL -. "manual relay (copy the record)" .-> SA
```

The relay is **manual**: you copy the payment information into a ServiceChain record. No tokens move
between the chains. The 980 tokens stay on PaymentChain in the Relay Custody address.

## Values used

| Item | Value |
|---|---|
| Asset on PaymentChain | `PayToken`, 5000 issued to Customer, units `1` (whole tokens only) |
| Payment request | `REQ001`, amount **1000**, fee_percent **2** |
| Fee (2%) | 1000 × 2 / 100 = **20** → Fee Collection address |
| Net amount | 1000 − 20 = **980** → Relay Custody address |
| Addresses (PaymentChain) | PaymentChain Admin (operator), Customer, Fee Collection, Relay Custody |
| Address (ServiceChain) | ServiceChain Admin |

## Order of work

The task lists step 5 (publish the receipt) before step 6 (the filter). **Create and approve the filter
first.** In MultiChain 2.3 a stream filter only checks items published **after** it was approved (the
node checks approval at the item's own block). A receipt published before approval is never validated.
So the order below is: steps 1 → 2 → 3 → 4 → **6 → 7 (tests)** → 5 → 7 (live check, duplicate check) →
logs.

---

## Part A: Two chains connected to the web demo

### A1. Create and start both chains

Command Prompt, in `C:\Users\BK-PC\Downloads\Programs\multichain-windows-2.3.3`:

```bat
multichain-util create PaymentChain
multichain-util create ServiceChain
```

Start each node in **its own window** and leave both open:

```bat
multichaind PaymentChain
```
```bat
multichaind ServiceChain
```

Each chain gets its own random ports, so both run on the same PC without clashing. Wait until both
windows print `Node ready.`

**Shortcut:** `scripts\windows\10-task3-two-chains.bat` creates both chains (if missing), starts both
nodes in their own windows, then sets up and opens the web demo for both (step A2).

### A2. Put both chains in the web demo's `config.txt`

```bat
scripts\windows\05-web-demo.bat PaymentChain ServiceChain
```

This writes `web-demo\config.txt` with one section per chain and opens http://127.0.0.1:8080/. To do it
by hand, copy each chain's `rpcuser`/`rpcpassword` from `%APPDATA%\MultiChain\<chain>\multichain.conf`
and its `default-rpc-port` from `%APPDATA%\MultiChain\<chain>\params.dat`:

```ini
PaymentChain.name=PaymentChain
PaymentChain.rpchost=127.0.0.1
PaymentChain.rpcsecure=0
PaymentChain.rpcport=<PaymentChain default-rpc-port>
PaymentChain.rpcuser=multichainrpc
PaymentChain.rpcpassword=<PaymentChain rpcpassword>

ServiceChain.name=ServiceChain
ServiceChain.rpchost=127.0.0.1
ServiceChain.rpcsecure=0
ServiceChain.rpcport=<ServiceChain default-rpc-port>
ServiceChain.rpcuser=multichainrpc
ServiceChain.rpcpassword=<ServiceChain rpcpassword>
```

The home page now lists both chains:

![Both chains in the web demo](images/task3/task3-01-both-chains-in-web-demo.png)

| PaymentChain | ServiceChain |
|---|---|
| ![PaymentChain node](images/task3/task3-02-paymentchain-node.png) | ![ServiceChain node](images/task3/task3-03-servicechain-node.png) |

*(Optional) On each chain's Node page, click **Set label** on the admin address and name it
`PaymentChain Admin` / `ServiceChain Admin`. Labels make every later screenshot easier to read.*

---

## Part B (Task step 1): Create and subscribe to the streams

| Chain | Stream |
|---|---|
| PaymentChain | `payment_requests`, `fee_deduction_logs`, `crosschain_audit_logs` |
| ServiceChain | `received_transactions`, `crosschain_audit_logs` |

**Create Stream** page: *From address* = admin, *Stream name* = the name, then **Create Stream**. Repeat
for each stream.

![Create stream form](images/task3/task3-04-paymentchain-create-stream-form.png)

![PaymentChain streams created](images/task3/task3-05-paymentchain-streams-created.png)

New streams say **not subscribed**: a node doesn't subscribe to its own new streams by default. Open
**View Streams** and click **Subscribe** on each one under *Other streams*:

![Subscribe buttons](images/task3/task3-06-paymentchain-streams-not-subscribed.png)

![PaymentChain subscribed](images/task3/task3-07-paymentchain-streams-subscribed.png)

Same on **ServiceChain** (`received_transactions`, `crosschain_audit_logs`):

![ServiceChain streams created](images/task3/task3-08-servicechain-streams-created.png)

![ServiceChain subscribed](images/task3/task3-09-servicechain-streams-subscribed.png)

---

## Part C: PaymentChain addresses and the payment token

Step 3 needs a **fee-collection address**, a **relay-custody address**, and tokens to pay with.

### C1. Three new addresses

On PaymentChain's **Node** page click **Get new address** three times: one each for Customer, Fee
Collection and Relay Custody.

### C2. Permissions

For each new address click **change** → tick **Connect, Send, Receive** → **Change Permissions**.
*Receive* lets it be paid. *Send* lets the customer pay and lets you set labels.

![Grant permissions](images/task3/task3-10-paymentchain-grant-customer.png)

### C3. Labels

Click **Set label** on each address: `Customer`, `Fee Collection`, `Relay Custody`.

![Set label](images/task3/task3-11-paymentchain-label-customer.png)

![Labelled addresses](images/task3/task3-12-paymentchain-addresses-labelled.png)

### C4. Issue PayToken to the Customer

**Issue Asset**: *Asset name* `PayToken`, *Quantity* `5000`, *Units* `1` (whole tokens), *To address*
**Customer** → **Issue Asset**.

![Issue PayToken](images/task3/task3-13-paymentchain-issue-paytoken.png)

![PayToken issued](images/task3/task3-14-paymentchain-paytoken-issued.png)

---

## Part D (Task step 2): Customer publishes the payment request

**Publish** (PaymentChain): *From address* **Customer**, *To stream* `payment_requests`, *Optional keys*
`REQ001`, *Or JSON*: the sample input
([`json/01-PaymentChain-payment_requests-REQ001.json`](../tasks/task3-crosschain/json/01-PaymentChain-payment_requests-REQ001.json)):

```json
{
  "request_id": "REQ001",
  "source_chain": "PaymentChain",
  "destination_chain": "ServiceChain",
  "amount": 1000,
  "fee_percent": 2
}
```

![Publish payment request](images/task3/task3-15-step2-publish-payment-request.png)

Note the transaction ID: it is the `payment_request_txid`.

![Payment request published](images/task3/task3-16-step2-payment-request-published.png)

**View Streams** → `payment_requests`:

![payment_requests stream](images/task3/task3-17-step2-payment-requests-stream.png)

---

## Part E (Task step 7): Check the request ID before processing

Before paying anything, make sure REQ001 has not been processed already. **View Streams** → click
`fee_deduction_logs`, then add **`&key=REQ001`** to the end of the address in the browser bar and press
Enter. (When the stream already has a REQ001 item you can just click its `REQ001` key link.)
**0 items with key REQ001** means it is safe to process:

![Not processed yet](images/task3/task3-18-dupcheck-paymentchain-not-processed-yet.png)

Log it in PaymentChain → `crosschain_audit_logs` with key `REQ001`
([`audit-P1`](../tasks/task3-crosschain/json/audit-P1-PaymentChain-payment-request-received.json),
status `PENDING`).

> Why by hand? Stream filters cannot read a stream's earlier items (MultiChain gives filters no
> `liststreamkeyitems` callback), so a filter can't detect duplicates. The duplicate check is a manual
> "look up the key first" step. Checking a key that doesn't exist is safe: MultiChain returns it with 0
> items.

---

## Part F (Task step 3): Deduct the fee and pay both addresses

| | Formula | REQ001 |
|---|---|---|
| Fee | amount × fee_percent ÷ 100 | 1000 × 2 ÷ 100 = **20** |
| Net | amount − fee | 1000 − 20 = **980** |

(Amounts divisible by 50 always give a whole-number 2% fee.)

**Send** (PaymentChain), done twice, from the **Customer**:

| Transfer | From | Asset | To | Quantity | Gives |
|---|---|---|---|---|---|
| Fee | Customer | PayToken | Fee Collection | **20** | `fee_payment_txid` |
| Net | Customer | PayToken | Relay Custody | **980** | `custody_payment_txid` |

![Send fee](images/task3/task3-19-step3-send-fee-form.png)

![Fee sent](images/task3/task3-20-step3-fee-sent.png)

![Send net](images/task3/task3-21-step3-send-net-form.png)

![Net sent](images/task3/task3-22-step3-net-sent.png)

**Node** page balances: Customer 5000 − 1000 = **4000**, Fee Collection **20**, Relay Custody **980**.

![Balances](images/task3/task3-23-step3-balances-after-transfers.png)

**Copy both transaction IDs** (the Node page and Send page don't keep them, so take them from the green
messages).

---

## Part G (Task step 4): Record the fee calculation in `fee_deduction_logs`

**Publish** (PaymentChain): *From* PaymentChain Admin, *stream* `fee_deduction_logs`, *key* `REQ001`, JSON
from [`json/02-…fee_deduction_logs-REQ001.json`](../tasks/task3-crosschain/json/02-PaymentChain-fee_deduction_logs-REQ001.json)
with your own transaction IDs and addresses:

```json
{
  "request_id": "REQ001",
  "source_chain": "PaymentChain",
  "destination_chain": "ServiceChain",
  "asset": "PayToken",
  "amount": 1000,
  "fee_percent": 2,
  "fee_amount": 20,
  "net_amount": 980,
  "payment_request_txid": "<PAYMENT_REQUEST_TXID>",
  "fee_collection_address": "<FEE_COLLECTION_ADDRESS>",
  "relay_custody_address": "<RELAY_CUSTODY_ADDRESS>",
  "fee_payment_txid": "<FEE_PAYMENT_TXID>",
  "custody_payment_txid": "<CUSTODY_PAYMENT_TXID>"
}
```

![Publish fee log](images/task3/task3-24-step4-publish-fee-log.png)

![fee_deduction_logs stream](images/task3/task3-25-step4-fee-deduction-logs-stream.png)

Then the PaymentChain audit log
[`audit-P2`](../tasks/task3-crosschain/json/audit-P2-PaymentChain-fee-deducted.json) (`FEE_DEDUCTED` /
`SUCCESS`):

![Audit log form](images/task3/task3-26-log-paymentchain-fee-deducted-form.png)

---

## Part H (Task steps 6 and 7): The `validate_fee_record` stream filter on ServiceChain

### H1. The code

From [`tasks/task3-crosschain/validate_fee_record.js`](../tasks/task3-crosschain/validate_fee_record.js).
A stream filter defines `filterstreamitem()`. Returning a **string** rejects the item with that reason.
Returning **nothing** accepts it.

```js
function filterstreamitem()
{
    // validate_fee_record - stream filter for ServiceChain -> received_transactions
    // Returning a string rejects the item with that reason; returning nothing accepts it.
    var item = getfilterstreamitem();
    var REQUIRED = ["request_id", "source_chain", "destination_chain", "amount", "fee_percent",
                    "fee_amount", "net_amount", "fee_payment_txid", "custody_payment_txid"];
    var TXID = /^[0-9a-f]{64}$/;

    if (!item.data || typeof item.data.json !== "object" || item.data.json === null)
        return "Record must be published as JSON";
    var r = item.data.json;

    // 1. Required fields and source transaction references
    for (var i = 0; i < REQUIRED.length; i++) {
        var v = r[REQUIRED[i]];
        if (v === undefined || v === null || v === "")
            return "Missing required field: " + REQUIRED[i];
    }
    if (!TXID.test(r.fee_payment_txid))
        return "fee_payment_txid must be a 64-character transaction ID";
    if (!TXID.test(r.custody_payment_txid))
        return "custody_payment_txid must be a 64-character transaction ID";
    if (r.fee_payment_txid === r.custody_payment_txid)
        return "fee_payment_txid and custody_payment_txid must be different transactions";
    if (item.keys.indexOf(r.request_id) < 0)
        return "Item key must be the request_id " + r.request_id;

    // 2. Positive original amount (whole tokens)
    if (typeof r.amount !== "number" || r.amount <= 0 || Math.floor(r.amount) !== r.amount)
        return "amount must be a positive whole number, got " + r.amount;

    // 3. Fee amount = 2% of the original amount
    if (r.fee_percent !== 2)
        return "fee_percent must be 2, got " + r.fee_percent;
    var expectedFee = r.amount * 2 / 100;
    if (r.fee_amount !== expectedFee)
        return "Incorrect fee: 2% of " + r.amount + " is " + expectedFee + ", got " + r.fee_amount;

    // 4. Net amount = original amount - fee
    var expectedNet = r.amount - r.fee_amount;
    if (r.net_amount !== expectedNet)
        return "Incorrect net amount: " + r.amount + " - " + r.fee_amount + " is " + expectedNet + ", got " + r.net_amount;

    // 5. Source and destination chain names
    if (r.source_chain !== "PaymentChain")
        return "source_chain must be PaymentChain, got " + r.source_chain;
    if (r.destination_chain !== "ServiceChain")
        return "destination_chain must be ServiceChain, got " + r.destination_chain;
}
```

| Requirement | Code |
|---|---|
| Required fields and source transaction references | loop over `REQUIRED`; both txids must be 64-hex and different; key must equal `request_id` |
| Positive original amount | `amount` is a number, > 0, whole |
| Fee = 2% of amount | `fee_percent === 2` and `fee_amount === amount * 2 / 100` |
| Net = amount − fee | `net_amount === amount - fee_amount` |
| Correct chain names | `source_chain === "PaymentChain"`, `destination_chain === "ServiceChain"` |

`getfilterstreamitem()` returns the item being published. A JSON item's content is in `item.data.json`,
and its keys are in `item.keys`.

### H2. Test the code (Filters → Stream)

On **ServiceChain** open **Filters: Stream**. Paste the code into *Filter code* and click **Test Compiling
Filter Code Only**:

![Compiles](images/task3/task3-27-step6-filter-code-compiles.png)

### H3. Step 7: the three test records

On the same page, fill in the test fields. Testing does **not** publish anything:
- *Test publish stream:* `received_transactions`
- *Test publish item keys:* `REQ001`
- *Test publish data:* **JSON**, then paste the record
- click **Test Publishing Item with This Filter**

| Test | File | Amount | Recorded fee | Recorded net | Expected | Result |
|---|---|---|---|---|---|---|
| Correct calculation | [`04`](../tasks/task3-crosschain/json/04-filter-test-1-correct.json) | 1000 | 20 | 980 | Valid | ✅ *Filter code allowed this stream item* |
| Incorrect fee | [`05`](../tasks/task3-crosschain/json/05-filter-test-2-incorrect-fee.json) | 1000 | 10 | 990 | Invalid | ✅ blocked: *Incorrect fee: 2% of 1000 is 20, got 10* |
| Incorrect net amount | [`06`](../tasks/task3-crosschain/json/06-filter-test-3-incorrect-net.json) | 1000 | 20 | 990 | Invalid | ✅ blocked: *Incorrect net amount: 1000 - 20 is 980, got 990* |

Use your real `fee_payment_txid` / `custody_payment_txid` in the test records. Placeholder text fails the
transaction-ID check.

![Test 1 correct](images/task3/task3-28-step7-test-1-correct-calculation.png)

![Test 2 incorrect fee](images/task3/task3-29-step7-test-2-incorrect-fee.png)

![Test 3 incorrect net](images/task3/task3-30-step7-test-3-incorrect-net-amount.png)

(Ticking **Display callback results** in test 1 shows the exact item the filter received from
`getfilterstreamitem()`.)

### H4. Create the filter on-chain

Same page, bottom: *Create filter name* `validate_fee_record` → **Create as a New On-Chain Stream
Filter**.

![Create filter](images/task3/task3-31-step6-create-filter-form.png)

![Filter created](images/task3/task3-32-step6-filter-created.png)

### H5. Approve it for `received_transactions`

In the filter's box on the left, click **change** (next to *Active on: no streams*). *For stream*:
`received_transactions`. *Stream admin address*: ServiceChain Admin. Click **Approve Filter for this
Stream**.

![Approve filter](images/task3/task3-33-step6-approve-filter-form.png)

*Active on* now shows **received_transactions**:

![Filter approved](images/task3/task3-34-step6-filter-approved.png)

![Filter active](images/task3/task3-35-step6-filter-active-on-stream.png)

The *N bytes of Javascript* link shows the code exactly as stored on ServiceChain (for the "filter code"
screenshot):

![Filter code on chain](images/task3/task3-36-step6-filter-code-on-chain.png)

---

## Part I (Task step 5): Relay the receipt to ServiceChain

### I1. Duplicate check

**View Streams** → `received_transactions` → add `&key=REQ001` to the address → **0 items**, so
relaying is safe. Command-line equivalent: `multichain-cli ServiceChain liststreamkeyitems
received_transactions REQ001` returns `[]`.

![Before relay](images/task3/task3-37-dupcheck-servicechain-before-relay.png)

### I2. Publish the receipt

**Publish** (ServiceChain): *From* ServiceChain Admin, *stream* `received_transactions`, *key* `REQ001`,
JSON = the teacher's sample valid output with **your** two transaction IDs
([`json/03`](../tasks/task3-crosschain/json/03-ServiceChain-received_transactions-REQ001.json)):

```json
{
  "request_id": "REQ001",
  "source_chain": "PaymentChain",
  "destination_chain": "ServiceChain",
  "amount": 1000,
  "fee_percent": 2,
  "fee_amount": 20,
  "net_amount": 980,
  "fee_payment_txid": "<FEE_PAYMENT_TXID>",
  "custody_payment_txid": "<CUSTODY_PAYMENT_TXID>"
}
```

![Publish receipt](images/task3/task3-38-step5-publish-receipt.png)

![Receipt published](images/task3/task3-39-step5-receipt-published.png)

The approved filter checked it, and the JSON is shown, so it is **valid**:

![Receipt valid](images/task3/task3-40-step5-receipt-valid-in-stream.png)

This record documents the interaction only. **No tokens moved to ServiceChain.** The 980 PayToken stay
in Relay Custody on PaymentChain.

---

## Part J (Task step 7): Live check and duplicate prevention

### J1. An incorrect-fee record is rejected by the approved filter

To show the filter working on-chain (not just in the test box), publish a deliberately wrong test record
with its own ID `REQ001-T2` (fee 10, net 990,
[`json/07`](../tasks/task3-crosschain/json/07-ServiceChain-received_transactions-REQ001-T2-live-incorrect-fee.json)):

![Publish incorrect record](images/task3/task3-41-step7-live-publish-incorrect-fee.png)

The web demo shows it as **Not available … rejected by a stream filter**, while REQ001 stays valid:

![Rejected by filter](images/task3/task3-42-step7-live-incorrect-fee-rejected.png)

MultiChain 2.3 still accepts the transaction, but it marks a failing item `"available": false` whenever
it is read. The reason is visible from the command line:

```bat
multichain-cli ServiceChain liststreamkeyitems received_transactions REQ001-T2
```
```text
"available" : false,
"error" : "Stream item did not pass filter validate_fee_record: Incorrect fee: 2% of 1000 is 20, got 10",
```

### J2. Second attempt to relay REQ001 → stop

Before any further relay, check the key again (click the `REQ001` key link in `received_transactions`):
**1 item with key REQ001** already exists, so REQ001 must
**not** be relayed or paid again. Record this as `DUPLICATE_CHECK` / `REJECTED_DUPLICATE` in the audit
log.

![Duplicate found](images/task3/task3-43-dupcheck-servicechain-duplicate-found.png)

---

## Part K: Audit logs on both chains (`crosschain_audit_logs`, key = request ID)

Every log has the same fields: timestamp, request ID, chain names, original amount, fee, net amount,
transaction IDs, status and error message. Use the current UTC time for `timestamp`. Transaction IDs that
don't exist yet are left as `""`.

| # | Chain | Key | When | event / status | Template |
|---|---|---|---|---|---|
| P1 | PaymentChain | REQ001 | after duplicate check (Part E) | PAYMENT_REQUEST_RECEIVED / PENDING | [`audit-P1`](../tasks/task3-crosschain/json/audit-P1-PaymentChain-payment-request-received.json) |
| P2 | PaymentChain | REQ001 | after fee log (Part G) | FEE_DEDUCTED / SUCCESS | [`audit-P2`](../tasks/task3-crosschain/json/audit-P2-PaymentChain-fee-deducted.json) |
| S1 | ServiceChain | REQ001 | filter test 1 | FILTER_TEST_CORRECT_CALCULATION / VALID | [`audit-S1`](../tasks/task3-crosschain/json/audit-S1-ServiceChain-filter-test-correct-calculation.json) |
| S2 | ServiceChain | REQ001 | filter test 2 | FILTER_TEST_INCORRECT_FEE / INVALID + error | [`audit-S2`](../tasks/task3-crosschain/json/audit-S2-ServiceChain-filter-test-incorrect-fee.json) |
| S3 | ServiceChain | REQ001 | filter test 3 | FILTER_TEST_INCORRECT_NET_AMOUNT / INVALID + error | [`audit-S3`](../tasks/task3-crosschain/json/audit-S3-ServiceChain-filter-test-incorrect-net-amount.json) |
| S4 | ServiceChain | REQ001 | receipt published (Part I) | RECEIPT_RECORDED / VALID | [`audit-S4`](../tasks/task3-crosschain/json/audit-S4-ServiceChain-receipt-recorded.json) |
| S5 | ServiceChain | REQ001 | second relay attempt (J2) | DUPLICATE_CHECK / REJECTED_DUPLICATE + error | [`audit-S5`](../tasks/task3-crosschain/json/audit-S5-ServiceChain-duplicate-check.json) |
| S6 | ServiceChain | REQ001-T2 | live wrong record (J1) | RECEIPT_RECORDED / REJECTED_BY_FILTER + error | [`audit-S6`](../tasks/task3-crosschain/json/audit-S6-ServiceChain-REQ001-T2-rejected-by-filter.json) |
| P3 | PaymentChain | REQ001 | after the relay | RELAYED_TO_SERVICECHAIN / COMPLETED | [`audit-P3`](../tasks/task3-crosschain/json/audit-P3-PaymentChain-relayed-to-servicechain.json) |

Example (S4):

```json
{
  "timestamp": "2026-10-10T09:15:00Z",
  "request_id": "REQ001",
  "logged_on": "ServiceChain",
  "source_chain": "PaymentChain",
  "destination_chain": "ServiceChain",
  "event": "RECEIPT_RECORDED",
  "status": "VALID",
  "amount": 1000,
  "fee_amount": 20,
  "net_amount": 980,
  "transaction_ids": {
    "payment_request_txid": "<PAYMENT_REQUEST_TXID>",
    "fee_payment_txid": "<FEE_PAYMENT_TXID>",
    "custody_payment_txid": "<CUSTODY_PAYMENT_TXID>",
    "fee_log_txid": "<FEE_LOG_TXID>",
    "servicechain_receipt_txid": "<RECEIPT_TXID>"
  },
  "error_message": ""
}
```

![Publish audit log](images/task3/task3-44-log-servicechain-receipt-form.png)

**ServiceChain → crosschain_audit_logs** (6 records):

![ServiceChain audit logs](images/task3/task3-45-logs-servicechain-crosschain-audit-logs.png)

**PaymentChain → crosschain_audit_logs** (3 records):

![PaymentChain audit logs](images/task3/task3-46-logs-paymentchain-crosschain-audit-logs.png)

---

## Submission checklist

| Teacher asks for | Screenshots |
|---|---|
| Both chains | 01, 02, 03 |
| Streams (created + subscribed) | 05, 07, 08, 09 |
| Payment request | 15, 16, 17 |
| Fee transfers | 19, 20, 21, 22, 23 |
| fee_deduction_logs | 24, 25 |
| Filter code and approval | 27, 31, 32, 33, 34, 35, 36 |
| Test results | 28, 29, 30 (tests), 40 (valid on-chain), 42 (rejected on-chain) |
| Duplicate check | 18, 37, 43 |
| Records in crosschain_audit_logs | 45, 46 |

## Verify from the command line (optional, good for the viva)

```bat
multichain-cli PaymentChain liststreamkeyitems payment_requests REQ001
multichain-cli PaymentChain getaddressbalances <RELAY_CUSTODY_ADDRESS>
multichain-cli PaymentChain getrawtransaction <FEE_PAYMENT_TXID> 1
multichain-cli PaymentChain liststreamkeyitems fee_deduction_logs REQ001
multichain-cli ServiceChain liststreamfilters
multichain-cli ServiceChain liststreams received_transactions
multichain-cli ServiceChain getfiltercode validate_fee_record
multichain-cli ServiceChain liststreamkeyitems received_transactions REQ001
multichain-cli ServiceChain liststreamkeyitems crosschain_audit_logs REQ001
```

`liststreams received_transactions` shows `"filters"` containing `validate_fee_record`.

## Viva: explain what you did

- **Two independent chains:** each has its own genesis block, `params.dat`, ports and addresses. They
  share nothing, so a PaymentChain address or token means nothing on ServiceChain.
- **Why "manual relay":** MultiChain has no built-in cross-chain transfer. The operator reads the
  result on PaymentChain and publishes a receipt on ServiceChain. Value stays on PaymentChain (980 in
  Relay Custody), and ServiceChain only gets a verifiable record pointing to the PaymentChain
  transaction IDs.
- **Streams:** append-only key-value logs on the chain. The key (`REQ001`) lets you fetch every
  record of a request across all streams. A node must **subscribe** to a stream to index and read it.
- **Stream filter:** JavaScript stored on the chain. Every node applies it to the items of the streams
  it is approved for. Return a string to reject, nothing to accept. It needs **approval** by a
  stream admin before it takes effect, and only applies to items published after approval.
- **Rejected items:** in MultiChain 2.3 the transaction is not refused. The item is marked
  `available: false` with the reason, so it never shows as valid data.
- **Duplicate payments:** filters can't search a stream's history, so the operator checks the request
  key in `fee_deduction_logs` / `received_transactions` before processing, and logs a
  `REJECTED_DUPLICATE` when it already exists.
- **2% fee with amounts divisible by 50:** 2% of a multiple of 50 is always a whole number (50 → 1), so
  fees and net amounts stay whole tokens (units = 1).

## How this was checked

- The filter was run on 16 cases (the 3 required tests plus missing fields, placeholder txids, same
  txids, zero/negative/string amount, wrong fee_percent, wrong chain names, wrong key, text instead of
  JSON, other amounts) with the expected result each time.
- The whole walkthrough above was clicked through automatically ([`dev/screenshots-task3.js`](../dev/screenshots-task3.js))
  against two simulated nodes ([`dev/mock_multichain.py`](../dev/mock_multichain.py)) that run the filter
  JavaScript for real and follow MultiChain 2.3's rules (filter approval per stream, items published
  after approval checked, failing items returned as `available: false`, no automatic subscription to new
  streams). These rules come from the MultiChain 2.3 source code.
- This found and fixed two more PHP 8 bugs in the original web demo (see
  [`web-demo/PHP8-CHANGES.md`](../web-demo/PHP8-CHANGES.md)). Testing an item on **Filters: Stream** or
  **Filters: Transaction** without ticking *Display callback results* printed a PHP warning.
- Not checked: a real MultiChain node on Windows. Run through it once on your PC before the exam.
