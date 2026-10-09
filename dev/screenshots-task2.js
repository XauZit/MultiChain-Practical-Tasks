// Captures the Task 2 walkthrough (create Goffycoin in the web demo and send it to another address)
// against dev/mock_multichain.py. Usage: node screenshots-task2.js <web-demo-url> <output-dir>
const { chromium } = require('playwright');
const [base, out] = process.argv.slice(2);

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1200, height: 800 } });
  // only the local demo is reachable; skip the CDN jQuery/Bootstrap JS (not needed for screenshots)
  await page.route('**/*', r => (r.request().url().startsWith(base) ? r.continue() : r.abort()));
  const mark = sel => page.locator(sel).evaluate(e => { e.style.outline = '3px solid #e8590c'; e.style.outlineOffset = '2px'; });
  const shot = name => page.screenshot({ path: `${out}/${name}.png`, fullPage: true });

  await page.goto(base);
  await mark('a:has-text("chain1")');
  await shot('task2-01-choose-chain');

  await page.click('a:has-text("chain1")');
  await mark('input[name=getnewaddress]');
  await shot('task2-02-node-page');

  await page.click('input[name=getnewaddress]');
  const newTable = page.locator('table.bg-success');
  const newAddress = (await newTable.locator('td.td-break-words').first().innerText()).trim();
  await newTable.evaluate(e => { e.style.outline = '3px solid #e8590c'; });
  await shot('task2-03-new-address');

  await newTable.locator('a:has-text("change")').click();
  for (const p of ['connect', 'send', 'receive']) { await page.check(`input[name=${p}]`); await mark(`input[name=${p}]`); }
  await mark('#to');
  await mark('input[name=grantrevoke]');
  await shot('task2-04-grant-permissions');
  await page.click('input[name=grantrevoke]');
  await mark('div.bg-success');
  await shot('task2-05-permissions-granted');

  await page.goto(`${base}?chain=default&page=issue`);
  await page.fill('#name', 'Goffycoin');
  await page.fill('#qty', '1000');
  await page.fill('#units', '0.01');
  await page.fill('#key0', 'description');
  await page.fill('#value0', 'Goffycoin - Lab Task 2');
  for (const s of ['#from', '#name', '#qty', '#units', '#to', '#key0', '#value0', 'input[name=issueasset]']) await mark(s);
  await shot('task2-06-issue-form');
  await page.click('input[name=issueasset]');
  await mark('div.bg-success');
  await mark('table.bg-success');
  await shot('task2-07-issued');

  await page.goto(`${base}?chain=default&page=send`);
  await page.selectOption('#asset', 'Goffycoin');
  await page.selectOption('#to', newAddress);
  await page.fill('#qty', '100');
  for (const s of ['#from', '#asset', '#to', '#qty', 'input[name=sendasset]']) await mark(s);
  await shot('task2-08-send-form');
  await page.click('input[name=sendasset]');
  await mark('div.bg-success');
  await shot('task2-09-sent');

  await page.goto(`${base}?chain=default`);
  for (const t of await page.locator('table').filter({ hasText: 'Goffycoin' }).all())
    await t.evaluate(e => { e.style.outline = '3px solid #e8590c'; });
  await shot('task2-10-balances');

  console.log('new address:', newAddress);
  await browser.close();
})();
