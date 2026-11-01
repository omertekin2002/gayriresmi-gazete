#!/usr/bin/env python3
"""Parse RG (date, number) citations and compare them with our list.
Writes data/citations.json: {"<n>": [{"date": iso, "src": "...", "ref": "..."}]}"""
import json, re, sys, os, datetime, collections, csv
D = sys.argv[1]; LIST = sys.argv[2]
cit = collections.defaultdict(list)
def norm_date(s):
    s = s.strip().replace('/', '.').replace('-', '.')
    m = re.match(r'(\d{1,2})\.(\d{1,2})\.(\d{4})$', s)
    if not m: return None
    d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
    if 1330 <= y <= 1345: y += 584
    try: return datetime.date(y, mo, d).isoformat()
    except ValueError: return None
bad = 0
for p, kind in ((os.path.join(D, 'tbmm', 'laws.jsonl'), 'Kanun'), (os.path.join(D, 'tbmm', 'decisions.jsonl'), 'TBMM Kararı')):
  if not os.path.exists(p): continue
  for l in open(p):
        r = json.loads(l)
        for x in r['recs']:
            raw = x.get('rg_raw') or ''
            m = re.match(r'\s*([0-9./-]+)\s*No\s*:\s*(\d+)\s*(.*)$', raw)
            if not m: bad += 1; continue
            iso = norm_date(m.group(1)); n = int(m.group(2))
            if not iso: bad += 1; continue
            muk = bool(re.search(r'm[üu]k', m.group(3), re.I))
            cit[n].append({'date': iso, 'src': 'tbmm', 'ref': f"{kind} {x['law']} (kabul {x['kabul']})", 'muk': muk})
extra = os.path.join(D, 'citations_extra.json')
if os.path.exists(extra):
    for n, lst in json.load(open(extra)).items(): cit[int(n)].extend(lst)
json.dump({str(k): v for k, v in cit.items()}, open(os.path.join(D, 'citations.json'), 'w'), ensure_ascii=False)
rows = list(csv.DictReader(open(LIST, encoding='utf-8')))
ours = {int(r['sayi']): r for r in rows if r['mukerrer'] == '0'}
agree = dis = 0; disl = []; bysrc = collections.Counter(); est_fix = []
for n, lst in cit.items():
    r = ours.get(n)
    if not r: continue
    dates = collections.Counter(c['date'] for c in lst)
    best = dates.most_common(1)[0][0]
    est = 'tahmin' in r['tarih_kaynagi']
    if est: est_fix.append((n, r['tarih'], best, dates))
    elif best == r['tarih']: agree += 1; bysrc[r['tarih_kaynagi']] += 1
    else: dis += 1; disl.append((n, r['tarih'], dict(dates), r['tarih_kaynagi']))
print('citations for', len(cit), 'issue numbers; unparsable', bad)
print('agree', agree, 'disagree', dis, 'by source', dict(bysrc))
for x in disl[:40]: print('  DIS', x)
print('estimated issues with a citation:', len(est_fix))
for x in est_fix[:20]: print('  EST', x[0], 'ours', x[1], '->', dict(x[3]))
