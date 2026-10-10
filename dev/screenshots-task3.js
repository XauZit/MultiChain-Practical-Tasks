// Performs Task 3 (PaymentChain -> ServiceChain relay with a stream filter) entirely through the web demo
// and saves numbered screenshots plus run-values.json (addresses, txids, published JSON).
// Usage: node screenshots-task3.js <web-demo-url> <output-dir> <filter-code-file>
// The web demo's config.txt must define chains "PaymentChain" and "ServiceChain".
const fs = require('fs');
const { chromium } = require('playwright');
const [base, out, filterFile] = process.argv.slice(2);
const FILTER_CODE = fs.readFileSync(filterFile, 'utf8').replace(/\r\n/g, '\n').trim();
const P = 'PaymentChain', S = 'ServiceChain';
const run = { published: {} };
let page, n = 0;

const url = (chain, pg, extra = '') => `${base}?chain=${chain}${pg ? '&page=' + pg : ''}${extra}`;
const ts = () => new Date().toISOString().replace(/\.\d+Z$/, 'Z');
const pretty = o => JSON.stringify(o, null, 2);

async function mark(sel) {
  await page.locator(sel).evaluateAll(els => els.forEach(e => { e.style.outline = '3px solid #e8590c'; e.style.outlineOffset = '2px'; }));
}
async function grow(sel) { // let long JSON textareas show everything in the screenshot
  await page.locator(sel).evaluate(e => { e.style.height = 'auto'; e.style.height = (e.scrollHeight + 6) + 'px'; });
}
async function shot(name) {
  const body = await page.locator('body').innerText();
  if (/Warning:|Deprecated:|Fatal error|Notice:/.test(body)) throw new Error('PHP error on ' + page.url() + '\n' + body.slice(0, 500));
  n++;
  const file = `${out}/task3-${String(n).padStart(2, '0')}-${name}.png`;
  await page.screenshot({ path: file, fullPage: true });
  console.log('saved', file);
}
async function successTxid() {
  const box = page.locator('div.bg-success').first();
  await mark('div.bg-success');
  const text = await box.innerText();
  const m = text.match(/[0-9a-f]{64}/);
  if (!m) throw new Error('no txid in: ' + text);
  return m[0];
}
async function newAddress(chain) {
  await page.goto(url(chain));
  await page.click('input[name=getnewaddress]');
  return (await page.locator('table.bg-success td.td-break-words').first().innerText()).trim().split(/\s/)[0];
}
async function grant(chain, addr, perms, screenshot) {
  await page.goto(url(chain, 'permissions', '&address=' + addr));
  for (const p of perms) { await page.check(`input[name=${p}]`); await mark(`input[name=${p}]`); }
  if (screenshot) { await mark('#to'); await mark('input[name=grantrevoke]'); await shot(screenshot); }
  await page.click('input[name=grantrevoke]');
  await successTxid();
}
async function setLabel(chain, addr, label, screenshot) {
  await page.goto(url(chain, 'label', '&address=' + addr));
  await page.fill('#label', label);
  if (screenshot) { await mark('#address'); await mark('#label'); await mark('input[name=setlabel]'); await shot(screenshot); }
  await page.click('input[name=setlabel]');
  await successTxid();
}
async function createStream(chain, name, screenshot) {
  await page.goto(url(chain, 'create'));
  await page.fill('#name', name);
  if (screenshot) { await mark('#from'); await mark('#name'); await mark('input[name=createstream]'); await shot(screenshot); }
  await page.click('input[name=createstream]');
  return successTxid();
}
async function subscribeAll(chain) {
  await page.goto(url(chain, 'view'));
  for (;;) {
    const btn = page.locator('input[type=submit][name^=subscribe_]');
    if (!(await btn.count())) break;
    await Promise.all([page.waitForNavigation(), btn.first().click()]);
  }
}
async function streamTxid(chain, name) {
  await page.goto(url(chain, 'view'));
  const href = await page.locator('a', { hasText: new RegExp('^' + name + '$') }).first().getAttribute('href');
  return new URL(href, base).searchParams.get('stream');
}
async function viewStream(chain, name, extra = '') {
  await page.goto(url(chain, 'view', '&stream=' + (await streamTxid(chain, name)) + extra));
}
async function publish(chain, from, stream, key, obj, formShot, resultShot) {
  await page.goto(url(chain, 'publish'));
  await page.selectOption('#from', from);
  await page.selectOption('#name', stream);
  await page.fill('#key', key);
  await page.fill('#json', pretty(obj));
  await grow('#json');
  if (formShot) { for (const s of ['#from', '#name', '#key', '#json', 'input[name=publish]']) await mark(s); await shot(formShot); }
  await page.click('input[name=publish]');
  const txid = await successTxid();
  if (resultShot) await shot(resultShot);
  run.published[`${chain}/${stream}/${key}/${n}`] = { txid, json: obj };
  return txid;
}
async function send(chain, from, asset, to, qty, formShot, resultShot) {
  await page.goto(url(chain, 'send'));
  await page.selectOption('#from', from);
  await page.selectOption('#asset', asset);
  await page.selectOption('#to', to);
  await page.fill('#qty', String(qty));
  if (formShot) { for (const s of ['#from', '#asset', '#to', '#qty', 'input[name=sendasset]']) await mark(s); await shot(formShot); }
  await page.click('input[name=sendasset]');
  const txid = await successTxid();
  if (resultShot) await shot(resultShot);
  return txid;
}
async function adminAddress(chain) {
  await page.goto(url(chain));
  return (await page.locator('td.td-break-words').first().innerText()).trim().split(/\s/)[0];
}

(async () => {
  const browser = await chromium.launch();
  page = await browser.newPage({ viewport: { width: 1200, height: 800 } });
  await page.route('**/*', r => (r.request().url().startsWith(base) ? r.continue() : r.abort()));

  // ---- A. Both chains connected to the web demo
  await page.goto(base);
  await mark('a[href*="chain="]');
  await shot('both-chains-in-web-demo');
  await page.goto(url(P)); await mark('table:has-text("Name")'); await shot('paymentchain-node');
  await page.goto(url(S)); await mark('table:has-text("Name")'); await shot('servicechain-node');

  run.adminP = await adminAddress(P);
  run.adminS = await adminAddress(S);
  await setLabel(P, run.adminP, 'PaymentChain Admin');
  await setLabel(S, run.adminS, 'ServiceChain Admin');

  // ---- B. Step 1: create and subscribe streams
  await createStream(P, 'payment_requests', 'paymentchain-create-stream-form');
  await createStream(P, 'fee_deduction_logs');
  await createStream(P, 'crosschain_audit_logs');
  await mark('table.bg-success'); await shot('paymentchain-streams-created');
  await page.goto(url(P, 'view')); await mark('input[name^=subscribe_]'); await shot('paymentchain-streams-not-subscribed');
  await subscribeAll(P);
  await page.goto(url(P, 'view')); await mark('h3:has-text("Subscribed streams")'); await shot('paymentchain-streams-subscribed');

  await createStream(S, 'received_transactions');
  await createStream(S, 'crosschain_audit_logs');
  await mark('table.bg-success'); await shot('servicechain-streams-created');
  await subscribeAll(S);
  await page.goto(url(S, 'view')); await shot('servicechain-streams-subscribed');

  // ---- C. PaymentChain addresses: customer, fee collection, relay custody
  run.customer = await newAddress(P);
  run.feeCollection = await newAddress(P);
  run.relayCustody = await newAddress(P);
  await grant(P, run.customer, ['connect', 'send', 'receive'], 'paymentchain-grant-customer');
  await grant(P, run.feeCollection, ['connect', 'send', 'receive']);
  await grant(P, run.relayCustody, ['connect', 'send', 'receive']);
  await setLabel(P, run.customer, 'Customer', 'paymentchain-label-customer');
  await setLabel(P, run.feeCollection, 'Fee Collection');
  await setLabel(P, run.relayCustody, 'Relay Custody');
  await page.goto(url(P)); await mark('table:has-text("Label")'); await shot('paymentchain-addresses-labelled');

  // ---- D. Payment token for the customer
  await page.goto(url(P, 'issue'));
  await page.selectOption('#to', run.customer);
  await page.fill('#name', 'PayToken');
  await page.fill('#qty', '5000');
  await page.fill('#units', '1');
  for (const s of ['#from', '#name', '#qty', '#units', '#to', 'input[name=issueasset]']) await mark(s);
  await shot('paymentchain-issue-paytoken');
  await page.click('input[name=issueasset]');
  run.issueTxid = await successTxid();
  await mark('table.bg-success'); await shot('paymentchain-paytoken-issued');

  // ---- E. Step 2: customer publishes the payment request
  const request = { request_id: 'REQ001', source_chain: P, destination_chain: S, amount: 1000, fee_percent: 2 };
  run.requestTxid = await publish(P, run.customer, 'payment_requests', 'REQ001', request,
    'step2-publish-payment-request', 'step2-payment-request-published');
  await viewStream(P, 'payment_requests'); await mark('table:has-text("REQ001")'); await shot('step2-payment-requests-stream');

  // ---- F. Duplicate check before processing (PaymentChain)
  await viewStream(P, 'fee_deduction_logs', '&key=REQ001'); await mark('h3:has-text("with key")'); await shot('dupcheck-paymentchain-not-processed-yet');
  run.logs = [];
  // every log has the same fields; transaction IDs that do not exist yet are left empty
  const audit = (chain, event, status, ids, err = '', o = {}) => ({
    timestamp: ts(), request_id: o.request_id || 'REQ001', logged_on: chain, source_chain: P, destination_chain: S,
    event, status, amount: 1000, fee_amount: o.fee_amount || 20, net_amount: o.net_amount || 980,
    transaction_ids: { payment_request_txid: '', fee_payment_txid: '', custody_payment_txid: '', fee_log_txid: '',
      servicechain_receipt_txid: '', ...ids },
    error_message: err });
  const a1 = audit(P, 'PAYMENT_REQUEST_RECEIVED', 'PENDING', { payment_request_txid: run.requestTxid });
  run.logs.push([P, a1, await publish(P, run.adminP, 'crosschain_audit_logs', 'REQ001', a1)]);

  // ---- G. Step 3: fee 2% = 20 to Fee Collection, 980 to Relay Custody
  run.feeTxid = await send(P, run.customer, 'PayToken', run.feeCollection, 20, 'step3-send-fee-form', 'step3-fee-sent');
  run.custodyTxid = await send(P, run.customer, 'PayToken', run.relayCustody, 980, 'step3-send-net-form', 'step3-net-sent');
  await page.goto(url(P)); await mark('table:has-text("PayToken")'); await shot('step3-balances-after-transfers');

  // ---- H. Step 4: fee_deduction_logs
  const feeLog = { request_id: 'REQ001', source_chain: P, destination_chain: S, asset: 'PayToken', amount: 1000,
    fee_percent: 2, fee_amount: 20, net_amount: 980, payment_request_txid: run.requestTxid,
    fee_collection_address: run.feeCollection, relay_custody_address: run.relayCustody,
    fee_payment_txid: run.feeTxid, custody_payment_txid: run.custodyTxid };
  run.feeLogTxid = await publish(P, run.adminP, 'fee_deduction_logs', 'REQ001', feeLog, 'step4-publish-fee-log', null);
  await viewStream(P, 'fee_deduction_logs'); await mark('table:has-text("REQ001")'); await shot('step4-fee-deduction-logs-stream');
  const paid = { payment_request_txid: run.requestTxid, fee_payment_txid: run.feeTxid, custody_payment_txid: run.custodyTxid };
  const a2 = audit(P, 'FEE_DEDUCTED', 'SUCCESS', { ...paid, fee_log_txid: run.feeLogTxid });
  run.logs.push([P, a2, await publish(P, run.adminP, 'crosschain_audit_logs', 'REQ001', a2, 'log-paymentchain-fee-deducted-form', null)]);

  // ---- I. Step 6: stream filter on ServiceChain (create, test, approve) - before relaying, so it validates the receipt
  const receipt = { request_id: 'REQ001', source_chain: P, destination_chain: S, amount: 1000, fee_percent: 2,
    fee_amount: 20, net_amount: 980, fee_payment_txid: run.feeTxid, custody_payment_txid: run.custodyTxid };
  await page.goto(url(S, 'streamfilter'));
  await page.fill('#code', FILTER_CODE); await grow('#code');
  await page.click('input[name=teststreamfiltercode]');
  await grow('#code'); await mark('div.bg-success'); await mark('#code'); await shot('step6-filter-code-compiles');

  const tests = [
    ['correct-calculation', receipt],
    ['incorrect-fee', { ...receipt, fee_amount: 10, net_amount: 990 }],
    ['incorrect-net-amount', { ...receipt, net_amount: 990 }],
  ];
  run.tests = [];
  for (const [i, [name, rec]] of tests.entries()) {
    await page.goto(url(S, 'streamfilter'));
    await page.fill('#code', FILTER_CODE);
    await page.selectOption('#stream', { label: 'received_transactions' });
    await page.fill('#keys', 'REQ001');
    await page.selectOption('#format', 'json');
    await page.fill('#data', pretty(rec));
    if (i === 0) await page.check('#callbacks');
    await page.click('input[name=teststreamfilterpublish]');
    await grow('#data');
    const ok = await page.locator('div.bg-success').count();
    const msg = (await page.locator(ok ? 'div.bg-success' : 'div.bg-danger').first().innerText()).trim();
    run.tests.push({ name, record: rec, result: ok ? 'Valid' : 'Invalid', message: msg });
    await mark(ok ? 'div.bg-success' : 'div.bg-danger'); await mark('#data');
    await shot(`step7-test-${i + 1}-${name}`);
  }

  await page.goto(url(S, 'streamfilter'));
  await page.fill('#code', FILTER_CODE);
  await page.fill('#name', 'validate_fee_record');
  await mark('#createfrom'); await mark('#name'); await mark('input[name=createstreamfilter]');
  await shot('step6-create-filter-form');
  await page.click('input[name=createstreamfilter]');
  run.filterTxid = await successTxid();
  await mark('table.bg-success'); await shot('step6-filter-created');

  const rtTxid = await streamTxid(S, 'received_transactions');
  await page.goto(url(S, 'approve', '&streamfilter=' + run.filterTxid));
  await page.selectOption('#stream', rtTxid);
  await mark('#stream'); await mark('#approvefrom'); await mark('input[name=approvestreamfilter]');
  await shot('step6-approve-filter-form');
  await page.click('input[name=approvestreamfilter]');
  run.approveTxid = await successTxid();
  await mark('p.form-control-static:has-text("received_transactions")');
  await shot('step6-filter-approved');
  await page.goto(url(S, 'streamfilter')); await mark('table:has-text("validate_fee_record")'); await shot('step6-filter-active-on-stream');
  await page.goto(`${base}filter-code.php?chain=${S}&txid=${run.filterTxid}`); await shot('step6-filter-code-on-chain');

  // ---- J. Step 5: duplicate check, then relay the receipt to ServiceChain
  await viewStream(S, 'received_transactions', '&key=REQ001'); await mark('h3:has-text("with key")'); await mark('p:has-text("No items")');
  await shot('dupcheck-servicechain-before-relay');
  run.receiptTxid = await publish(S, run.adminS, 'received_transactions', 'REQ001', receipt,
    'step5-publish-receipt', 'step5-receipt-published');
  await viewStream(S, 'received_transactions'); await mark('table:has-text("REQ001")'); await shot('step5-receipt-valid-in-stream');

  // ---- K. Step 7 live proof: an incorrect-fee record is rejected by the approved filter
  const bad = { ...receipt, request_id: 'REQ001-T2', fee_amount: 10, net_amount: 990 };
  run.badTxid = await publish(S, run.adminS, 'received_transactions', 'REQ001-T2', bad, 'step7-live-publish-incorrect-fee', null);
  await viewStream(S, 'received_transactions'); await mark('table:has-text("REQ001-T2")'); await shot('step7-live-incorrect-fee-rejected');

  // ---- L. Duplicate attempt: REQ001 already relayed -> do not process again
  await viewStream(S, 'received_transactions', '&key=REQ001'); await mark('h3:has-text("with key")');
  await shot('dupcheck-servicechain-duplicate-found');

  // ---- M. Audit logs on both chains
  const t = run.tests;
  const done = { ...paid, fee_log_txid: run.feeLogTxid };
  const sLogs = [
    audit(S, 'FILTER_TEST_CORRECT_CALCULATION', 'VALID', done),
    audit(S, 'FILTER_TEST_INCORRECT_FEE', 'INVALID', done, t[1].message.split('\n').pop(), { fee_amount: 10, net_amount: 990 }),
    audit(S, 'FILTER_TEST_INCORRECT_NET_AMOUNT', 'INVALID', done, t[2].message.split('\n').pop(), { net_amount: 990 }),
    audit(S, 'RECEIPT_RECORDED', 'VALID', { ...done, servicechain_receipt_txid: run.receiptTxid }),
    audit(S, 'DUPLICATE_CHECK', 'REJECTED_DUPLICATE', { ...done, servicechain_receipt_txid: run.receiptTxid },
      'REQ001 already exists in received_transactions (relayed earlier) - not relayed again'),
  ];
  for (const [i, l] of sLogs.entries())
    run.logs.push([S, l, await publish(S, run.adminS, 'crosschain_audit_logs', 'REQ001', l, i === 3 ? 'log-servicechain-receipt-form' : null, null)]);
  const badLog = audit(S, 'RECEIPT_RECORDED', 'REJECTED_BY_FILTER', { ...paid, servicechain_receipt_txid: run.badTxid },
    'Stream item did not pass filter validate_fee_record: Incorrect fee: 2% of 1000 is 20, got 10',
    { request_id: 'REQ001-T2', fee_amount: 10, net_amount: 990 });
  run.logs.push([S, badLog, await publish(S, run.adminS, 'crosschain_audit_logs', 'REQ001-T2', badLog)]);
  const a3 = audit(P, 'RELAYED_TO_SERVICECHAIN', 'COMPLETED', { ...done, servicechain_receipt_txid: run.receiptTxid });
  run.logs.push([P, a3, await publish(P, run.adminP, 'crosschain_audit_logs', 'REQ001', a3)]);

  await viewStream(S, 'crosschain_audit_logs'); await shot('logs-servicechain-crosschain-audit-logs');
  await viewStream(P, 'crosschain_audit_logs'); await shot('logs-paymentchain-crosschain-audit-logs');

  fs.writeFileSync(`${out}/run-values.json`, JSON.stringify(run, null, 2));
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
