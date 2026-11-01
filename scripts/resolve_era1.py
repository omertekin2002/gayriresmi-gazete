#!/usr/bin/env python3
"""Resolve dates for arsiv issues (era 1) from noisy OCR text via weighted non-decreasing selection."""
import sys, os, json, glob, re, datetime, bisect
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rgdate import candidates, norm_text, YEAR_RE, to_greg_year

DATA = sys.argv[1]  # data dir containing era1/*.jsonl
OUT = sys.argv[2]
OVR = sys.argv[3] if len(sys.argv) > 3 else None   # optional overrides json {key: "YYYY-MM-DD"}
FIRST = datetime.date(1921, 2, 7)
LAST = datetime.date(2001, 12, 31)

recs = {}
for f in sorted(glob.glob(os.path.join(DATA, 'era1', '*.jsonl'))):
    for line in open(f, encoding='utf-8'):
        try:
            r = json.loads(line)
        except Exception:
            continue
        k = r['key']
        old = recs.get(k)
        if old is None or (old.get('status') != 'ok' and r.get('status') == 'ok') or (old.get('status') == r.get('status')):
            recs[k] = r

def keyparse(k):
    m = re.fullmatch(r'(\d+)(?:_(\d+))?(T?)', k)
    if not m: return None
    return int(m.group(1)), int(m.group(2) or 0), bool(m.group(3))

# group
issues = {}  # (n, muk) -> {'T': rec, 'O': rec}
for k, r in recs.items():
    kp = keyparse(k)
    if not kp: continue
    n, muk, t = kp
    issues.setdefault((n, muk), {})['T' if t else 'O'] = r

def best_rec(d):
    for t in ('T', 'O'):
        r = d.get(t)
        if r and r.get('status') == 'ok': return r
    return None

mains = sorted(n for (n, muk) in issues if muk == 0)
info = {}
for (n, muk), d in issues.items():
    r = best_rec(d)
    status = 'ok' if r else ('404' if all(x.get('status') == '404' for x in d.values()) else 'error')
    ent = {'n': n, 'muk': muk, 'status': status, 'srcs': {t: x.get('url') for t, x in d.items() if x.get('status') == 'ok'}}
    if r:
        txt = (r.get('text1') or '') + '\n' + (r.get('text2') or '')
        c, w, s, mk = candidates(txt)
        head = norm_text(txt)[:900]
        yhints = sorted({to_greg_year(int(y)) for y in YEAR_RE.findall(head)} - {1920})
        ent.update({'cands': c, 'wd': w, 'sayi': s, 'muk_word': mk, 'yhints': yhints, 'pages': r.get('pages'), 'bytes': r.get('bytes'), 'p1': r.get('p1'), 'textlen': len(txt.strip())})
    info[(n, muk)] = ent

# byte-identical files: either server-side misfiled archive entries or worker pairing mistakes
import collections as _c
_by = _c.defaultdict(list)
for (n, muk), e in info.items():
    if e['status'] == 'ok' and e.get('bytes'):
        _by[(e['bytes'], e.get('pages'))].append((n, muk))
dupinfo = {}
for k, members in _by.items():
    if len(members) < 2: continue
    good = [m for m in members if info[m].get('sayi') == m[0]]
    for m in members:
        e = info[m]
        if m[1] > 0:
            e['status'] = 'dup'; dupinfo[m] = members        # mükerrer that is a copy of another file: not trusted
        elif good and m not in good:
            e['cands'] = []; e['dupfile'] = True; dupinfo[m] = members
overrides = json.load(open(OVR)) if OVR and os.path.exists(OVR) else {}

# ---- candidate generation for mains
def gen(n):
    e = info.get((n, 0))
    if not e or e['status'] != 'ok': return []
    if str(n) in overrides:
        return [(datetime.date.fromisoformat(overrides[str(n)]), 100.0, 'override')]
    out = {}
    # neighbor explicit years
    nyears = set(e['yhints'])
    for dn in range(-6, 7):
        e2 = info.get((n + dn, 0))
        if e2 and e2.get('cands'):
            for c in e2['cands']:
                if isinstance(c[0], datetime.date): nyears.add(c[0].year)
    for c in e['cands']:
        if isinstance(c[0], datetime.date):
            d = c[0]
            if not (FIRST <= d <= LAST): continue
            sc = 2.0 + (0.5 if c[2] == 'after0' else 0.0)
            if e['wd']:
                sc += 2.0 if d.weekday() in e['wd'] else -1.5
            out[d] = max(out.get(d, -9), sc)
        else:
            _, mon, day = c[0]
            for y in nyears:
                try: d = datetime.date(y, mon, day)
                except ValueError: continue
                if not (FIRST <= d <= LAST): continue
                sc = 1.0 + (0.3 if y in e['yhints'] else 0.0)
                if e['wd']:
                    sc += 2.0 if d.weekday() in e['wd'] else -1.5
                out[d] = max(out.get(d, -9), sc)
    return [(d, s, 'c') for d, s in out.items() if s > 0]

cand = {n: gen(n) for n in mains}

# ---- weighted longest non-decreasing selection (DP with Fenwick max over date ordinals)
allc = []
for n in mains:
    for (d, s, tag) in cand[n]:
        allc.append((n, d, s))
ords = sorted({d.toordinal() for _, d, _ in allc})
idx = {o: i + 1 for i, o in enumerate(ords)}
size = len(ords) + 2
tree = [(0.0, -1)] * (size + 1)
def upd(i, val):
    while i <= size:
        if val[0] > tree[i][0]: tree[i] = val
        i += i & -i
def qry(i):
    best = (0.0, -1)
    while i > 0:
        if tree[i][0] > best[0]: best = tree[i]
        i -= i & -i
    return best
nodes = []  # (n, d, score_total, prev_node)
for n in mains:
    batch = []
    for (d, s, tag) in cand[n]:
        b = qry(idx[d.toordinal()])  # best chain ending with date <= d (strictly earlier n)
        batch.append((n, d, b[0] + s, b[1]))
    for item in batch:
        nodes.append(item)
        upd(idx[item[1].toordinal()], (item[2], len(nodes) - 1))
best = max(range(len(nodes)), key=lambda i: nodes[i][2]) if nodes else -1
chosen = {}
i = best
while i >= 0:
    n, d, tot, p = nodes[i]
    chosen[n] = d
    i = p

# ---- fill / flag
res = {}
ch_sorted = sorted(chosen)
for n in mains:
    e = info[(n, 0)]
    out = {'n': n, 'status': e['status'], 'src': e.get('srcs'), 'sayi_ocr': e.get('sayi'), 'pages': e.get('pages'), 'p1': e.get('p1')}
    if e.get('dupfile'): out['dupfile'] = [list(x) for x in dupinfo.get((n, 0), [])]
    if n in chosen:
        d = chosen[n]
        out['date'] = d.isoformat(); out['how'] = 'ocr'
        out['wd_ok'] = (d.weekday() in e['wd']) if e.get('wd') else None
    else:
        j = bisect.bisect_left(ch_sorted, n)
        pn = ch_sorted[j - 1] if j > 0 else None
        nn = ch_sorted[j] if j < len(ch_sorted) else None
        inferred = None
        if pn and nn and chosen[pn] == chosen[nn]:
            inferred = (chosen[pn], 'between-equal')
        elif pn and nn and (chosen[nn] - chosen[pn]).days <= 10 and e.get('wd'):
            days_known = {c[0][2] for c in e.get('cands', []) if not isinstance(c[0], datetime.date)} | {c[0].day for c in e.get('cands', []) if isinstance(c[0], datetime.date)}
            opts = []
            x = chosen[pn]
            while x <= chosen[nn]:
                if x.weekday() in e['wd'] and (not days_known or x.day in days_known): opts.append(x)
                x += datetime.timedelta(days=1)
            if len(opts) == 1: inferred = (opts[0], 'inferred-weekday' + ('+day' if days_known else ''))
        if inferred:
            out['date'] = inferred[0].isoformat(); out['how'] = inferred[1]
        else:
            out['date'] = None; out['how'] = 'unresolved'
            out['range'] = [chosen[pn].isoformat() if pn else None, chosen[nn].isoformat() if nn else None]
    res[n] = out

# gap/jump flags
prevd = None; prevn = None
for n in mains:
    o = res[n]
    if o.get('date'):
        d = datetime.date.fromisoformat(o['date'])
        if prevd is not None:
            gap = (d - prevd).days
            o['gap_days'] = gap
            if gap > 10 and not (prevd < datetime.date(1923, 9, 11) and d >= datetime.date(1921, 7, 1)):
                o['flag_gap'] = True
        prevd, prevn = d, n
    if o.get('sayi_ocr') is not None and o['sayi_ocr'] != n:
        o['flag_sayi'] = True

# mükerrer
muks = []
for (n, muk), e in sorted(info.items()):
    if muk == 0: continue
    o = {'n': n, 'muk': muk, 'status': e['status'], 'src': e.get('srcs'), 'p1': e.get('p1')}
    md = res.get(n, {}).get('date')
    o['date'] = md
    dates = [c[0] for c in e.get('cands', []) if isinstance(c[0], datetime.date)]
    if md and dates:
        o['ocr_agrees'] = any(d.isoformat() == md for d in dates)
    muks.append(o)

json.dump({'mains': [res[n] for n in mains], 'muks': muks}, open(OUT, 'w'), ensure_ascii=False, indent=0)
# summary
from collections import Counter
print('mains', len(mains), Counter(r['status'] for r in res.values()))
print('how', Counter(r.get('how') for r in res.values() if r['status'] == 'ok'))
print('wd_ok', Counter(r.get('wd_ok') for r in res.values() if r.get('how') == 'ocr'))
print('flag_gap', sum(1 for r in res.values() if r.get('flag_gap')), 'flag_sayi', sum(1 for r in res.values() if r.get('flag_sayi')))
print('muks', len(muks), Counter(m['status'] for m in muks), 'existing muk', sum(1 for m in muks if m['status']=='ok'))
