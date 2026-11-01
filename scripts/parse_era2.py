#!/usr/bin/env python3
"""Normalize era-2 (eskiler daily pages) results -> list of issue records."""
import json, re, sys, os, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rgdate import fold

MONTHS = {'ocak':1,'subat':2,'mart':3,'nisan':4,'mayis':5,'haziran':6,'temmuz':7,'agustos':8,'eylul':9,'ekim':10,'kasim':11,'aralik':12}
def fold2(s):
    s = (s or '').replace('�', '?')
    return fold(s)
def mast_date(m):
    t = fold2((m or '').replace('*', ''))
    t = re.sub(r'[^a-z0-9? ]', ' ', t)
    mm = re.search(r'(\d{1,2})\s+([a-z?]{3,8})\s+(\d{4})', t)
    if not mm: return None
    mon = None
    w = mm.group(2)
    for k, v in MONTHS.items():
        if len(k) == len(w) and all(a == b or b == '?' for a, b in zip(k, w)):
            mon = v; break
    if not mon: return None
    try: return datetime.date(int(mm.group(3)), mon, int(mm.group(1)))
    except ValueError: return None
def digits(s):
    s = re.sub(r'(?<!\d)(19|20)\d\d(?!\d)', ' ', (s or '').replace('*', ''))  # drop years
    m = re.search(r'(?<!\d)\d{5}(?!\d)', s)
    return int(m.group(0)) if m else None

def parse(res):
    out = []; anomalies = []
    for d, e in sorted(res.items()):
        date = datetime.date.fromisoformat(d)
        y, mo, da = d[:4], d[5:7], d[8:10]
        base = f'https://www.resmigazete.gov.tr/eskiler/{y}/{mo}/{y}{mo}{da}'
        if e.get('main_status') == 'ok':
            no_issue = (e.get('no_issue') or '').strip().lower().startswith('y')
            n = digits(e.get('sayi')) or digits(e.get('masthead'))
            md = mast_date(e.get('masthead'))
            if no_issue and not n:
                out.append({'date': d, 'kind': 'no_issue'}); continue
            if n is None:
                anomalies.append({'date': d, 'why': 'no sayi', 'e': e}); continue
            if md and md != date:
                anomalies.append({'date': d, 'why': f'masthead date {md} != page date', 'e': e})
            out.append({'date': d, 'n': n, 'muk': 0, 'url': base + '.htm', 'masthead': e.get('masthead'), 'mast_date_ok': (md == date) if md else None})
            for p in e.get('probes') or []:
                if p.get('status') != 'ok': continue
                if f'{y}{mo}{da}M' not in (p.get('url') or ''):
                    continue  # link to another date's mükerrer; that date has its own probe
                sm = re.search(r'M(\d+)', p.get('suffix') or '') or re.search(r'M(\d+)\.', p.get('url') or '')
                k = int(sm.group(1)) if sm else None
                pn = digits(p.get('sayi')) or digits(p.get('masthead')) or n
                if pn != n:
                    anomalies.append({'date': d, 'why': f'mukerrer sayi {pn} != main {n}', 'e': p})
                out.append({'date': d, 'n': n, 'muk': k, 'url': p.get('url'), 'masthead': p.get('masthead'), 'probe_sayi': pn})
        elif e.get('main_status') == '404':
            okp = [p for p in (e.get('probes') or []) if p.get('status') == 'ok']
            if okp:
                anomalies.append({'date': d, 'why': 'main 404 but mukerrer exists', 'e': e})
                for p in okp:
                    sm = re.search(r'M(\d+)', p.get('suffix') or '')
                    out.append({'date': d, 'n': digits(p.get('sayi')) or digits(p.get('masthead')), 'muk': int(sm.group(1)) if sm else None, 'url': p.get('url'), 'masthead': p.get('masthead')})
            out.append({'date': d, 'kind': 'page404'})
        else:
            anomalies.append({'date': d, 'why': 'main error', 'e': e})
    return out, anomalies

def apply_corrections(out, path):
    if not os.path.exists(path): return out
    cor = json.load(open(path))
    new = []
    for r in out:
        c = cor.get(r.get('date'))
        if c and 'n' in r:
            if c['n'] is None:
                if r['muk'] == 0: new.append({'date': r['date'], 'kind': 'no_issue', 'note': c['note']})
                continue
            r = dict(r); r['printed_n'] = r['n']; r['n'] = c['n']
            if r['muk'] == 0: r['note'] = c['note']
        new.append(r)
    return new

if __name__ == '__main__':
    res = json.load(open(sys.argv[1]))
    out, an = parse(res)
    out = apply_corrections(out, os.path.join(os.path.dirname(sys.argv[2]), 'corrections.json'))
    json.dump({'records': out, 'anomalies': an}, open(sys.argv[2], 'w'), ensure_ascii=False, indent=0)
    iss = [r for r in out if 'n' in r and r['muk'] == 0]
    print('main issues', len(iss), 'muk', sum(1 for r in out if r.get('muk')), 'no_issue', sum(1 for r in out if r.get('kind') == 'no_issue'), '404', sum(1 for r in out if r.get('kind') == 'page404'), 'anomalies', len(an))
    # continuity: flag dates whose number breaks the +1 sequence (only between adjacent covered dates)
    iss.sort(key=lambda r: r['date'])
    covered = {r['date'] for r in out}
    sus = set()
    for a, b in zip(iss, iss[1:]):
        da_, db_ = datetime.date.fromisoformat(a['date']), datetime.date.fromisoformat(b['date'])
        contiguous = all((da_ + datetime.timedelta(days=i)).isoformat() in covered for i in range(1, (db_ - da_).days))
        if not contiguous: continue
        if b['n'] != a['n'] + 1:
            sus.add(a['date']); sus.add(b['date'])
            print('  seq jump', a['date'], a['n'], '->', b['date'], b['n'])
    json.dump(sorted(sus), open(sys.argv[2].replace('.json', '_suspects.json'), 'w'))
    print('suspect dates', len(sus))
