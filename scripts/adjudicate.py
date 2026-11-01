#!/usr/bin/env python3
"""Adjudicate TBMM citations vs our list. Output data/citation_decisions.json"""
import json, csv, sys, os, datetime, collections
D, LIST = sys.argv[1], sys.argv[2]
cit = {int(k): v for k, v in json.load(open(os.path.join(D, 'citations.json'))).items()}
rep = json.load(open(os.path.join(D, 'merge_report.json')))
win = {n: r for n, d, r in rep['tahmin']}
rows = list(csv.DictReader(open(LIST, encoding='utf-8')))
ours = {int(r['sayi']): r for r in rows if r['mukerrer'] == '0'}
by_date = collections.defaultdict(list)
for n, r in ours.items(): by_date[r['tarih']].append(n)
def one_edit(a, b):
    a, b = str(a), str(b)
    if len(a) != len(b): return False
    diff = [i for i in range(len(a)) if a[i] != b[i]]
    if len(diff) == 1: return True
    if len(diff) == 2 and diff[1] == diff[0] + 1 and a[diff[0]] == b[diff[1]] and a[diff[1]] == b[diff[0]]: return True
    return False
dec = {'est_fixed': {}, 'est_conflict': [], 'agree': 0, 'tbmm_number_typo': [], 'tbmm_date_typo': [], 'recheck': []}
for n, lst in sorted(cit.items()):
    r = ours.get(n)
    if not r: continue
    dates = collections.Counter(c['date'] for c in lst)
    ourd = r['tarih']
    if 'tahmin' in r['tarih_kaynagi']:
        lo, hi = win.get(n) or (None, None)
        ok = [d for d in dates if lo and lo <= d <= hi]
        if len(ok) == 1:
            dec['est_fixed'][str(n)] = {'date': ok[0], 'refs': [c['ref'] for c in lst if c['date'] == ok[0]][:3]}
        else:
            dec['est_conflict'].append({'n': n, 'ours': ourd, 'window': [lo, hi], 'cited': dict(dates)})
        continue
    if ourd in dates: dec['agree'] += 1; continue
    expl = None
    for d in dates:
        others = by_date.get(d, [])
        if any(one_edit(n, m) for m in others): expl = ('number', d, others)
    if expl: dec['tbmm_number_typo'].append({'n': n, 'ours': ourd, 'cited': dict(dates), 'issue_on_cited_date': expl[2]}); continue
    if all(one_edit(ourd.replace('-', ''), d.replace('-', '')) for d in dates):
        dec['tbmm_date_typo'].append({'n': n, 'ours': ourd, 'cited': dict(dates), 'src': r['tarih_kaynagi']}); continue
    dec['recheck'].append({'n': n, 'ours': ourd, 'cited': dict(dates), 'src': r['tarih_kaynagi'], 'refs': [c['ref'] for c in lst][:3]})
json.dump(dec, open(os.path.join(D, 'citation_decisions.json'), 'w'), ensure_ascii=False, indent=1)
print('agree', dec['agree'], 'est_fixed', len(dec['est_fixed']), 'est_conflict', len(dec['est_conflict']),
      'tbmm_number_typo', len(dec['tbmm_number_typo']), 'tbmm_date_typo', len(dec['tbmm_date_typo']), 'recheck', len(dec['recheck']))
for x in dec['est_conflict']: print('  EST-CONFLICT', x)
for x in dec['recheck']: print('  RECHECK', x['n'], x['ours'], x['cited'], x['src'])
