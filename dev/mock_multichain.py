"""Minimal stateful mock of a MultiChain 2.3.3 JSON-RPC node, for exercising the web demo."""
import hashlib, json, sys, time
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 6724
_n = [0]

def txid():
    _n[0] += 1
    return hashlib.sha256(str(_n[0]).encode()).hexdigest()

B58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

def newaddr():  # deterministic, shaped like a MultiChain base58 address
    _n[0] += 1
    n = int.from_bytes(hashlib.sha256(b'a' + str(_n[0]).encode()).digest(), 'big')
    s = ''
    while len(s) < 33:
        n, r = divmod(n, 58)
        s += B58[r]
    return '1' + s

ALL_PERMS = ['connect', 'send', 'receive', 'issue', 'create', 'mine', 'activate', 'admin']
A0 = newaddr()
S = {
    'addresses': [A0],
    'perms': {A0: set(ALL_PERMS)},
    'assets': [],
    'balances': {},
    'streams': [{'name': 'root', 'createtxid': txid(), 'streamref': '0-0-0', 'items': []}],
    'txfilters': [], 'streamfilters': [],
}

def perm_rows(types, addrs):
    types = ALL_PERMS if types in ('*', 'all') else types.split(',')
    out = []
    for a, ps in S['perms'].items():
        if addrs not in (None, '*') and a not in addrs.split(','):
            continue
        for t in types:
            if t in ps:
                out.append({'address': a, 'for': None, 'type': t, 'startblock': 0, 'endblock': 4294967295,
                            'admins': [A0], 'pending': []})
    return out

def stream(ident):
    for s in S['streams']:
        if ident in (s['name'], s['createtxid'], s['streamref']):
            return s
    raise KeyError('Stream with this name, ref or txid not found: ' + str(ident))

def stream_info(s):
    pubs = {p for it in s['items'] for p in it['publishers']}
    keys = {k for it in s['items'] for k in it['keys']}
    return {'name': s['name'], 'createtxid': s['createtxid'], 'streamref': s['streamref'],
            'restrict': {'write': False, 'read': False, 'onchain': False, 'offchain': False},
            'details': {}, 'filters': [], 'subscribed': True, 'synchronized': True, 'items': len(s['items']),
            'confirmed': len(s['items']), 'keys': len(keys), 'publishers': len(pubs), 'creators': [A0]}

def asset_info(a, verbose):
    info = {k: a[k] for k in ('name', 'issuetxid', 'assetref', 'multiple', 'units', 'open', 'details', 'issueqty', 'issueraw')}
    info.update({'restrict': {'send': False, 'receive': False}, 'fungible': True, 'canopen': False, 'canclose': False,
                 'totallimit': None, 'issuelimit': None, 'subscribed': False})
    if verbose:
        info['issues'] = a['issues']
    return info

def balances(addr):
    return [{'name': n, 'assetref': next(x['assetref'] for x in S['assets'] if x['name'] == n), 'qty': q}
            for n, q in S['balances'].get(addr, {}).items() if q]

def add_balance(addr, name, qty):
    S['balances'].setdefault(addr, {})
    S['balances'][addr][name] = S['balances'][addr].get(name, 0) + qty

def add_item(s, publisher, keys, data):
    if isinstance(keys, str):
        keys = [keys] if keys != '' else []
    t = txid()
    s['items'].append({'publishers': [publisher], 'keys': keys, 'offchain': False, 'available': True,
                       'data': data, 'confirmations': 1, 'blocktime': int(time.time()), 'txid': t, 'vout': 0,
                       'valid': True, 'time': int(time.time()), 'timereceived': int(time.time())})
    return t

def handle(method, p):
    if method == 'getinfo':
        return {'version': '2.3.3', 'nodeversion': 20303901, 'edition': 'Community', 'protocolversion': 20013,
                'chainname': 'chain1', 'description': 'MultiChain chain1', 'protocol': 'multichain', 'port': 6725,
                'setupblocks': 60, 'nodeaddress': 'chain1@192.168.1.10:6725', 'burnaddress': '1XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
                'incomingpaused': False, 'miningpaused': False, 'offchainpaused': False, 'walletversion': 60000,
                'balance': 0.0, 'walletdbversion': 3, 'reindex': False, 'blocks': 42, 'chainrewards': 0.0,
                'streams': len(S['streams']), 'timeoffset': 0, 'connections': 0, 'proxy': '', 'difficulty': 6e-08,
                'testnet': False, 'keypoololdest': 1700000000, 'keypoolsize': 2, 'paytxfee': 0.0, 'relayfee': 0.0, 'errors': ''}
    if method == 'getpeerinfo':
        return []
    if method == 'getaddresses':
        if p and p[0]:
            return [{'address': a, 'ismine': True, 'iswatchonly': False, 'isscript': False, 'pubkey': '02' + '11' * 32,
                     'iscompressed': True, 'account': '', 'synchronized': True} for a in S['addresses']]
        return list(S['addresses'])
    if method == 'getnewaddress':
        a = newaddr(); S['addresses'].append(a); return a
    if method == 'listpermissions':
        return perm_rows(p[0] if p else '*', p[1] if len(p) > 1 else None)
    if method in ('grantfrom', 'revokefrom'):
        for to in p[1].split(','):
            ps = S['perms'].setdefault(to, set())
            for t in p[2].split(','):
                (ps.add if method == 'grantfrom' else ps.discard)(t)
        return txid()
    if method == 'getmultibalances':
        out = {a: balances(a) for a in S['addresses']}
        return out
    if method == 'gettotalbalances':
        tot = {}
        for a in S['addresses']:
            for b in balances(a):
                tot[b['name']] = tot.get(b['name'], 0) + b['qty']
        return [{'name': n, 'assetref': next(x['assetref'] for x in S['assets'] if x['name'] == n), 'qty': q} for n, q in tot.items()]
    if method == 'getaddressbalances':
        return balances(p[0])
    if method == 'listassets':
        verbose = len(p) > 1 and p[1]
        want = p[0] if p else '*'
        found = [asset_info(a, verbose) for a in S['assets'] if want in ('*', a['name'], a['issuetxid'], a['assetref'])]
        if want != '*' and not found:
            raise KeyError('Asset with this name, ref or txid not found: ' + want)
        return found
    if method in ('issue', 'issuefrom'):
        if method == 'issue':
            p = [S['addresses'][0]] + p
        frm, to, spec, qty, units = p[0], p[1], p[2], float(p[3]), float(p[4]) if len(p) > 4 else 1.0
        name = spec['name'] if isinstance(spec, dict) else spec
        if any(a['name'] == name for a in S['assets']):
            raise KeyError('Asset or stream with this name already exists')
        multiple = int(round(1 / units))
        return handle('createrawsendfrom', [frm, {to: {'issue': {'raw': int(qty * multiple)}}},
                      [{'create': 'asset', 'name': name, 'multiple': multiple, 'open': bool(isinstance(spec, dict) and spec.get('open')), 'details': {}}], 'send'])
    if method == 'issuemore':
        a = next(x for x in S['assets'] if x['name'] == p[1])
        return handle('createrawsendfrom', [S['addresses'][0], {p[0]: {'issue': {'asset': a['name'], 'raw': int(float(p[2]) * a['multiple'])}}}, [], 'send'])
    if method == 'sendasset':
        return handle('sendassetfrom', [S['addresses'][0]] + p)
    if method == 'grant':
        return handle('grantfrom', [S['addresses'][0]] + p)
    if method == 'create':
        return handle('createfrom', [S['addresses'][0], p[0], p[1], p[2] if len(p) > 2 else False, ''])
    if method == 'publish':
        return handle('publishfrom', [S['addresses'][0]] + p)
    if method == 'getblockcount':
        return 42
    if method == 'getblock':
        return {'hash': '00' * 32, 'miner': S['addresses'][0], 'confirmations': 1, 'height': p[0], 'tx': [txid()]}
    if method == 'getmempoolinfo':
        return {'size': 0, 'bytes': 0}
    if method == 'stop':
        return 'MultiChain server stopping'
    if method == 'createrawsendfrom':
        frm, addrs, datas = p[0], p[1], p[2]
        for to, amt in addrs.items():
            if 'issue' in amt:
                iss = amt['issue']
                if 'asset' in iss:
                    a = next(x for x in S['assets'] if iss['asset'] in (x['name'], x['issuetxid']))
                    det = datas[0].get('details', {}) if datas and isinstance(datas[0], dict) else {}
                    a['issues'].append({'txid': txid(), 'qty': iss['raw'] * a['units'], 'raw': iss['raw'], 'details': det, 'issuers': [frm]})
                    a['issueqty'] += iss['raw'] * a['units']
                    add_balance(to, a['name'], iss['raw'] * a['units'])
                else:
                    d = datas[0]
                    t = txid()
                    units = 1.0 / d['multiple']
                    a = {'name': d['name'], 'issuetxid': t, 'assetref': '%d-266-%d' % (len(S['assets']) + 40, 1000 + len(S['assets'])),
                         'multiple': d['multiple'], 'units': units, 'open': d['open'], 'details': d['details'] or {},
                         'issueqty': iss['raw'] * units, 'issueraw': iss['raw'],
                         'issues': [{'txid': t, 'qty': iss['raw'] * units, 'raw': iss['raw'], 'details': d['details'] or {}, 'issuers': [frm]}]}
                    S['assets'].append(a)
                    add_balance(to, a['name'], iss['raw'] * units)
                    return t
        return txid()
    if method == 'sendassetfrom':
        frm, to, asset, qty = p[0], p[1], p[2], float(p[3])
        add_balance(frm, asset, -qty); add_balance(to, asset, qty); return txid()
    if method == 'sendwithmetadatafrom':
        frm, to, amounts = p[0], p[1], p[2]
        for asset, qty in amounts.items():
            add_balance(frm, asset, -float(qty)); add_balance(to, asset, float(qty))
        return txid()
    if method == 'lockunspent':
        return True
    if method == 'liststreams':
        want = p[0] if p else '*'
        found = [stream_info(s) for s in S['streams'] if want in ('*', s['name'], s['createtxid'])]
        if want != '*' and not found:
            raise KeyError('Stream with this name, ref or txid not found: ' + want)
        return found
    if method == 'createfrom':
        kind = p[1]
        t = txid()
        if kind == 'stream':
            S['streams'].append({'name': p[2], 'createtxid': t, 'streamref': '%d-267-%d' % (40 + len(S['streams']), 100), 'items': []})
        elif kind == 'txfilter':
            S['txfilters'].append({'name': p[2], 'createtxid': t, 'filterref': '1-2-3', 'language': 'javascript',
                                   'codelength': len(p[4]), 'for': [], 'approved': False, 'pending': []})
        elif kind == 'streamfilter':
            S['streamfilters'].append({'name': p[2], 'createtxid': t, 'filterref': '1-2-4', 'language': 'javascript',
                                       'codelength': len(p[4]), 'approved': False})
        return t
    if method == 'subscribe':
        return None
    if method == 'publishfrom':
        return add_item(stream(p[1]), p[0], p[2], p[3])
    if method == 'liststreamitems':
        return stream(p[0])['items'][-(p[2] if len(p) > 2 else 10):]
    if method == 'liststreamkeyitems':
        return [it for it in stream(p[0])['items'] if p[1] in it['keys']]
    if method == 'liststreampublisheritems':
        return [it for it in stream(p[0])['items'] if p[1] in it['publishers']]
    if method == 'liststreamkeys':
        s = stream(p[0]); keys = {}
        for it in s['items']:
            for k in it['keys']:
                keys[k] = keys.get(k, 0) + 1
        return [{'key': k, 'items': n, 'confirmed': n} for k, n in keys.items() if (p[1] if len(p) > 1 else '*') in ('*', k)]
    if method == 'liststreampublishers':
        s = stream(p[0]); pubs = {}
        for it in s['items']:
            for pub in it['publishers']:
                pubs.setdefault(pub, []).append(it)
        return [{'publisher': pub, 'items': len(its), 'confirmed': len(its), 'first': its[0], 'last': its[-1]}
                for pub, its in pubs.items() if (p[1] if len(p) > 1 else '*') in ('*', pub)]
    if method == 'getblockchainparams':
        return {'chain-name': 'chain1', 'protocol-version': 20013, 'maximum-block-size': 8388608,
                'max-std-tx-size': 4194304, 'max-std-op-return-size': 2097152, 'default-network-port': 6725,
                'default-rpc-port': 6724, 'target-block-time': 15, 'mining-diversity': 0.3}
    if method == 'gettxoutdata':
        return '00'
    if method == 'listtxfilters':
        return S['txfilters']
    if method == 'liststreamfilters':
        return S['streamfilters']
    if method in ('testtxfilter', 'teststreamfilter'):
        return {'compiled': True, 'passed': True, 'callbacks': [], 'time': 0.001}
    if method == 'getfiltercode':
        return 'function filtertransaction() {}'
    if method == 'preparelockunspentfrom':
        return {'txid': txid(), 'vout': 0}
    if method == 'createrawexchange':
        return 'ab' * 40
    if method == 'decoderawexchange':
        return {'offer': {'amount': 0.0, 'assets': []}, 'ask': {'amount': 0.0, 'assets': []},
                'cancomplete': True, 'complete': False, 'exchanges': []}
    if method == 'appendrawexchange':
        return {'hex': 'cd' * 40, 'complete': True}
    if method == 'sendrawtransaction':
        return txid()
    if method in ('approvefrom',):
        return txid()
    if method == 'getfiltercode':
        return ''
    raise NotImplementedError('Method not found: ' + method)

class H(BaseHTTPRequestHandler):
    def do_POST(self):
        req = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        try:
            body = {'result': handle(req['method'], req.get('params', [])), 'error': None, 'id': req.get('id')}
        except (KeyError, NotImplementedError) as e:
            body = {'result': None, 'error': {'code': -708, 'message': str(e)}, 'id': req.get('id')}
        sys.stderr.write('RPC %s %s -> %s\n' % (req['method'], json.dumps(req.get('params'))[:120], 'ERR' if body['error'] else 'ok'))
        data = json.dumps(body).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *a):
        pass

HTTPServer(('127.0.0.1', PORT), H).serve_forever()
