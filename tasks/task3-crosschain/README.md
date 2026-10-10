# Cross-chain lab: copy-paste files

Guide with screenshots: [docs/10-task-3-crosschain-stream-filter.md](../../docs/10-task-3-crosschain-stream-filter.md)

| File | Paste into (web demo) |
|---|---|
| [`validate_fee_record.js`](validate_fee_record.js) | ServiceChain → Filters: Stream → *Filter code* |
| [`json/01-PaymentChain-payment_requests-REQ001.json`](json/01-PaymentChain-payment_requests-REQ001.json) | PaymentChain → Publish → `payment_requests`, key `REQ001`, from **Customer** |
| [`json/02-PaymentChain-fee_deduction_logs-REQ001.json`](json/02-PaymentChain-fee_deduction_logs-REQ001.json) | PaymentChain → Publish → `fee_deduction_logs`, key `REQ001` |
| [`json/03-ServiceChain-received_transactions-REQ001.json`](json/03-ServiceChain-received_transactions-REQ001.json) | ServiceChain → Publish → `received_transactions`, key `REQ001` |
| [`json/04-filter-test-1-correct.json`](json/04-filter-test-1-correct.json) | ServiceChain → Filters: Stream → *Test publish data* (JSON), keys `REQ001` → expected **Valid** |
| [`json/05-filter-test-2-incorrect-fee.json`](json/05-filter-test-2-incorrect-fee.json) | same → expected **Invalid** (fee 10) |
| [`json/06-filter-test-3-incorrect-net.json`](json/06-filter-test-3-incorrect-net.json) | same → expected **Invalid** (net 990) |
| [`json/07-…-REQ001-T2-live-incorrect-fee.json`](json/07-ServiceChain-received_transactions-REQ001-T2-live-incorrect-fee.json) | ServiceChain → Publish → `received_transactions`, key `REQ001-T2` (after approval: shown as rejected) |
| `json/audit-P1…P3-PaymentChain-*.json` | PaymentChain → Publish → `crosschain_audit_logs`, key `REQ001` |
| `json/audit-S1…S6-ServiceChain-*.json` | ServiceChain → Publish → `crosschain_audit_logs`, key `REQ001` (S6: `REQ001-T2`) |

Replace every `<PLACEHOLDER>` with your own values before publishing:

| Placeholder | Where to get it |
|---|---|
| `<PAYMENT_REQUEST_TXID>` | green message after publishing the payment request |
| `<FEE_PAYMENT_TXID>` | green message after sending the 20 PayToken fee |
| `<CUSTODY_PAYMENT_TXID>` | green message after sending the 980 PayToken |
| `<FEE_LOG_TXID>` | green message after publishing to `fee_deduction_logs` |
| `<RECEIPT_TXID>` | green message after publishing the receipt on ServiceChain |
| `<REQ001_T2_RECEIPT_TXID>` | green message after publishing the REQ001-T2 test record |
| `<FEE_COLLECTION_ADDRESS>`, `<RELAY_CUSTODY_ADDRESS>` | Node page of PaymentChain |
| `<CURRENT UTC TIME, …>` | the time you publish, e.g. `2026-10-10T09:15:00Z` |

Keep numbers as numbers (`1000`, not `"1000"`). The filter rejects text amounts.
