// Runs a MultiChain stream filter (filterstreamitem) in a sandbox, the way a node would for one item.
// stdin: {"code": "...", "item": {...getfilterstreamitem() result...}, "txid": "...", "stream": {...}}
// stdout: {"compiled": bool, "passed": bool, "reason": string|null, "callbacks": [...]}
// Used by mock_multichain.py (teststreamfilter, and items published after a filter is approved).
const vm = require('vm');

let input = '';
process.stdin.on('data', d => (input += d));
process.stdin.on('end', () => {
  const { code, item, txid, stream } = JSON.parse(input);
  const callbacks = [];
  const cb = (method, fn) => (...params) => {
    const result = fn(...params);
    callbacks.push({ method, params, success: true, result });
    return JSON.parse(JSON.stringify(result === undefined ? null : result));
  };
  const sandbox = {
    getfilterstreamitem: cb('getfilterstreamitem', () => item),
    getfiltertxid: cb('getfiltertxid', () => txid),
    getfilterstream: cb('getfilterstream', () => stream),
    getlastblockinfo: cb('getlastblockinfo', () => ({ height: 100, time: Math.floor(Date.now() / 1000) })),
    setfilterparam: cb('setfilterparam', () => null),
  };
  const out = { compiled: true, passed: false, reason: null, callbacks };
  const ctx = vm.createContext(sandbox);
  try {
    vm.runInContext(code, ctx, { timeout: 1000 });
  } catch (e) {
    out.compiled = false;
    out.reason = String(e && e.message ? e.message : e);
    return console.log(JSON.stringify(out));
  }
  if (typeof ctx.filterstreamitem !== 'function') {
    out.compiled = false;
    out.reason = 'filterstreamitem() function not found';
    return console.log(JSON.stringify(out));
  }
  if (!item) return console.log(JSON.stringify(out));  // compile-only test
  try {
    const r = vm.runInContext('filterstreamitem()', ctx, { timeout: 1000 });
    if (typeof r === 'string' && r.length) out.reason = r;
    else out.passed = true;
  } catch (e) {
    out.reason = 'Filter error: ' + String(e && e.message ? e.message : e);
  }
  console.log(JSON.stringify(out));
});
