"""Re-implements mc_MultichainParams::Create + Write (MultiChain 2.3.x) to print
the params.dat that `multichain-util create <name>` writes, using paramlist.h."""
import random, re, sys

paramlist_path, chain, version, seed = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
src = open(paramlist_path).read()
body = src[src.index('MultichainParamArray[] =') :]
body = body[body.index('{') + 1 : body.rindex('};')]

FLAGS = dict(MC_PRM_BINARY=1, MC_PRM_STRING=2, MC_PRM_BOOLEAN=3, MC_PRM_INT32=4, MC_PRM_INT64=5,
             MC_PRM_DOUBLE=6, MC_PRM_UINT32=7, MC_PRM_COMMENT=0x10, MC_PRM_USER=0x20,
             MC_PRM_GENERATED=0x30, MC_PRM_CALCULATED=0x40, MC_PRM_CLONE=0x10000,
             MC_PRM_SPECIAL=0x20000, MC_PRM_NOHASH=0x40000, MC_PRM_MINIMAL=0x80000,
             MC_PRM_DECIMAL=0x100000, MC_PRM_HIDDEN=0x200000, MC_PRM_TIME=0x400000,
             MC_DEFAULT_NETWORK_PORT=8571, MC_DEFAULT_RPC_PORT=8570, MC_PRM_NETWORK_NAME_MAX_SIZE=32)

tok_re = re.compile(r'"((?:[^"\\]|\\.)*)"|([^,{}"\s][^,{}"]*)|([{},])', re.S)
body = re.sub(r'//[^\n]*', '', body)
entries, cur, depth = [], None, 0
for m in tok_re.finditer(body):
    s, bare, punct = m.groups()
    if punct == '{':
        cur = []; continue
    if punct == '}':
        entries.append(cur); cur = None; continue
    if punct == ',' or cur is None:
        continue
    if s is not None:
        val = bytes(s, 'utf-8').decode('unicode_escape')
        # adjacent string literals concatenate
        if cur and isinstance(cur[-1], tuple) and cur[-1][0] == 'str' and m.start() > 0 and body[prev_end:m.start()].strip() == '':
            cur[-1] = ('str', cur[-1][1] + val)
        else:
            cur.append(('str', val))
    else:
        cur.append(('raw', bare.strip()))
    prev_end = m.end()

def num(expr):
    expr = expr.strip()
    total = 0
    for part in expr.split('|'):
        part = part.strip().rstrip('ULul') if re.match(r'^-?[0-9]', part.strip()) else part.strip()
        if part in FLAGS: total |= FLAGS[part]
        else: total |= int(float(part)) if re.match(r'^-?[\d.]+$', part) else int(part, 0)
    return total

params = []
for e in entries:
    vals = [v for _, v in e]
    p = dict(name=vals[0], disp=vals[1], type=num(vals[2]), maxstr=num(vals[3]), dflt=num(vals[4]),
             mn=num(vals[5]), mx=num(vals[6]), dbl=float(vals[7]), proto=num(vals[8]), removed=num(vals[9]),
             arg=vals[10], next=vals[11], group=vals[12], desc=vals[13])
    params.append(p)
index = {p['name']: i for i, p in enumerate(params)}

rng = random.Random(seed)
R = lambda a, b: rng.randint(a, b)
FREE = [2644,2744,2870,4244,4324,4374,4754,5744,6264,6446,6716,6790,7172,7314,7404,7718,8338,9218,9538,9696]
values, network_port = {}, None
for src_set in (0x10, 0x20, 0x30):
    for p in params:
        if p['type'] & 0xF0 != src_set: continue
        t = p['type'] & 0xF
        v = None
        if src_set in (0x10, 0x20):
            if t == 2:
                v = ''
                if p['type'] & FLAGS['MC_PRM_SPECIAL']:
                    v = {'chaindescription': 'MultiChain ' + chain, 'rootstreamname': 'root', 'chainprotocol': 'multichain'}.get(p['name'], '')
            elif t == 1: v = None
            elif t == 3: v = bool(p['dflt'])
            elif t in (4, 5, 7): v = p['dflt']
            elif t == 6: v = p['dbl']
        else:
            n = p['name']
            if n == 'defaultnetworkport':
                network_port = FREE[R(0, len(FREE) - 1)] + 1 + 2 * R(0, 24); v = network_port
            elif n == 'defaultrpcport': v = network_port - 1
            elif n == 'protocolversion': v = version
            elif n == 'chainname': v = chain
            elif n == 'networkmessagestart': v = bytes([R(0xf0,0xff), R(0xc0,0xff), R(0xc0,0xff), R(0xe0,0xff)])
            elif n == 'addresspubkeyhashversion': v = bytes([0x00, R(0,255), R(0,255), R(0,255)])
            elif n == 'addressscripthashversion': v = bytes([0x05, R(0,255), R(0,255), R(0,255)])
            elif n == 'privatekeyversion': v = bytes([0x80, R(0,255), R(0,255), R(0,255)])
            elif n == 'addresschecksumvalue': v = bytes([R(0,255) for _ in range(4)])
        values[p['name']] = v

LINE = 39
out = []
w = out.append
w("# ==== MultiChain configuration file ====\n\n")
w("# Created by multichain-util \n")
w("# Protocol version: %d \n\n" % version)
w("# This parameter set is properly GENERATED. \n")
w('# To generate network please run "multichaind %s".\n' % chain)

def relevant(p):
    return not (p['proto'] > version or (p['removed'] > 0 and p['removed'] <= version))

for s in (0x10, 0x20, 0x30, 0x40):
    header = False
    i = 0
    while i >= 0:
        p = params[i]
        if p['type'] & 0xF0 == s and relevant(p):
            hidden = False
            if not header:
                w("\n"); header = True
                w({0x10: "# The following parameters don't influence multichain network configuration. \n# They may be edited at any moment. \n",
                   0x20: "# The following parameters can be edited before running multichaind for this chain. \n",
                   0x30: "# The following parameters were generated by multichain-util.\n# They SHOULD ONLY BE EDITED IF YOU KNOW WHAT YOU ARE DOING. \n",
                   0x40: "# The following parameters were generated by multichaind.\n# They SHOULD NOT BE EDITED. \n"}[s])
                w("\n")
            if p['group']:
                w("\n# %s\n\n" % p['group'])
            line = "%s = " % p['disp']
            v = values.get(p['name'])
            t = p['type'] & 0xF
            if t == 2 and v == '' and not (p['type'] & FLAGS['MC_PRM_SPECIAL'] and p['name'] == 'rootstreamname'):
                v = None
            chars_remaining = 0
            if v is None:
                line += "[null]"
            elif t == 1:
                hx = v.hex()
                if len(hx) + len(line) > LINE: w(line + hx); chars_remaining = 1
                else: line += hx
            elif t == 2:
                if len(v) + 1 + len(line) > LINE: w(line + v); chars_remaining = 1
                else: line += v
            elif t == 3: line += 'true' if v else 'false'
            elif t in (4, 7):
                if p['type'] & FLAGS['MC_PRM_DECIMAL']:
                    if v: line += "%0.6g" % (((v + 1e-6) if v >= 0 else -((-v) + 1e-6)) / 1e6)
                    else: line += "0.0"
                else:
                    line += "%d" % v
                    if t == 7 and p['type'] & FLAGS['MC_PRM_HIDDEN'] and v == p['dflt']: hidden = True
            elif t == 5: line += "%d" % v
            elif t == 6: line += "%f" % v
            if not hidden:
                if chars_remaining == 0:
                    w(line); chars_remaining = LINE - len(line) + 1
                w(" " * max(chars_remaining, 0))
                parts = p['desc'].split('\n')
                for k, part in enumerate(parts):
                    w("# %s" % part)
                    if k < len(parts) - 1: w("\n" + " " * LINE + " ")
                if t in (4, 5, 7) and s in (0x10, 0x20) and p['mn'] <= p['mx']:
                    if p['type'] & FLAGS['MC_PRM_DECIMAL']:
                        d1 = (p['mn'] + 1e-6) / 1e6 if p['mn'] else 0
                        d2 = (p['mx'] + 1e-6) / 1e6 if p['mx'] else 0
                        w(" (%0.6g - %0.6g)" % (d1, d2))
                    else:
                        w(" (%d - %d)" % (p['mn'], p['mx']))
                w("\n")
        i = index[p['next']] if p['next'] else -1
w("\n")
sys.stdout.write(''.join(out))
