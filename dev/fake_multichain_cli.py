#!/usr/bin/env python3
"""Stand-in for multichain-cli.exe when testing scripts/windows/*.ps1 on Linux: same argv shape,
same output streams (request echo on stderr, result on stdout, errors on stderr + non-zero exit).
Reads the RPC port and credentials from <MC_DATA>/<chain>/ like the real client."""
import base64, json, os, re, sys, urllib.request

chain, method, raw = sys.argv[1], sys.argv[2], sys.argv[3:]
data_dir = os.path.join(os.environ['FAKE_MC_DATA'], chain)
port = re.search(r'^default-rpc-port = (\d+)', open(os.path.join(data_dir, 'params.dat')).read(), re.M).group(1)
conf = dict(l.strip().split('=', 1) for l in open(os.path.join(data_dir, 'multichain.conf')) if '=' in l)

def conv(a):
    try:
        return json.loads(a)
    except ValueError:
        return a

req = {'method': method, 'params': [conv(a) for a in raw], 'id': '1', 'chain_name': chain}
sys.stderr.write(json.dumps(req) + '\n\n')
r = urllib.request.Request('http://127.0.0.1:%s/' % port, json.dumps(req).encode(),
                           {'Authorization': 'Basic ' + base64.b64encode(('%s:%s' % (conf['rpcuser'], conf['rpcpassword'])).encode()).decode()})
try:
    reply = json.load(urllib.request.urlopen(r, timeout=5))
except OSError as e:
    sys.stderr.write('error: Could not connect to the server 127.0.0.1:%s (%s)\n' % (port, e)); sys.exit(1)
if reply.get('error'):
    sys.stderr.write('error code: %d\nerror message:\n%s\n' % (reply['error']['code'], reply['error']['message']))
    sys.exit(abs(reply['error']['code']))
res = reply['result']
if res is not None:
    print(res if isinstance(res, str) else json.dumps(res, indent=4))
