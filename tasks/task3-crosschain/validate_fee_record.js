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
