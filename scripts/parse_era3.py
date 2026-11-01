#!/usr/bin/env python3
"""Normalize Lexpera daily data -> issue records; report continuity."""
import json, sys, datetime
recs = {}
for l in open(sys.argv[1], encoding='utf-8'):
    r = json.loads(l)
    if r.get('http') == 200: recs[r['date']] = r
out = []; anomalies = []
for d in sorted(recs):
    r = recs[d]
    seen = set()
    for i in r['issues']:
        n = int(i['num'])
        if n > 40000:  # pseudo ids (YYYYMMDD-like) = non-Gazette sources
            continue
        key = (n, i['mukerrer'])
        if key in seen: continue
        seen.add(key)
        hd = i['hdr_date']; hd_iso = f'{hd[6:10]}-{hd[3:5]}-{hd[0:2]}'
        if hd_iso != d: anomalies.append({'date': d, 'why': 'hdr date mismatch', 'i': i})
        out.append({'date': d, 'n': n, 'muk': i['mukerrer'], 'lexpera_items': i['n_lines']})
json.dump({'records': out, 'anomalies': anomalies, 'days': len(recs)}, open(sys.argv[2], 'w'), ensure_ascii=False, indent=0)
mains = sorted([r for r in out if r['muk'] == 0], key=lambda r: (r['n']))
print('days', len(recs), 'mains', len(mains), 'muk', sum(1 for r in out if r['muk']), 'anomalies', len(anomalies))
nums = [r['n'] for r in mains]
print('range', nums[0], nums[-1])
s = set(nums)
missing = [n for n in range(nums[0], nums[-1] + 1) if n not in s]
print('missing main numbers', len(missing), missing[:40])
from collections import Counter
dup = [n for n, c in Counter(nums).items() if c > 1]
print('dup main numbers', dup[:20])
# monotonic
bad = [(a['date'], a['n'], b['date'], b['n']) for a, b in zip(mains, mains[1:]) if b['date'] < a['date']]
print('non-monotonic', bad[:10])
# mukerrer without main same date
mset = {(r['n'], r['date']) for r in mains}
orph = [r for r in out if r['muk'] and (r['n'], r['date']) not in mset]
print('orphan mukerrer', len(orph), orph[:10])
# days without a main issue
dm = {r['date'] for r in mains}
d0 = datetime.date.fromisoformat(min(recs)); d1 = datetime.date.fromisoformat(max(recs))
nod = []
x = d0
while x <= d1:
    if x.isoformat() not in dm: nod.append(x.isoformat())
    x += datetime.timedelta(days=1)
print('days without main issue', len(nod), nod[:60])
