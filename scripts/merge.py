#!/usr/bin/env python3
"""Merge all sources into the final chronological list of Resmî Gazete issues.
Sources (priority for the date): official daily page (eskiler/fihrist) > masthead read visually > masthead OCR >
inference from neighbouring issues > Lexpera daily list."""
import json, sys, os, datetime, csv, collections
D = sys.argv[1]; OUTDIR = sys.argv[2]
os.makedirs(OUTDIR, exist_ok=True)
GUN = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']
def load(p, default=None):
    p = os.path.join(D, p)
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else default
e1 = load('era1_resolved.json', {'mains': [], 'muks': []})
e2 = load('era2/era2_parsed.json', {'records': []})
e3 = load('era3/era3_parsed.json', {'records': []})
vis = load('visual_dates.json', {})
visres = load('visual_results.json', {})
iso = datetime.date.fromisoformat

issues = collections.defaultdict(lambda: {'src': {}, 'urls': {}, 'notes': []})
def put(n, muk, src, date, url=None, note=None):
    it = issues[(n, muk)]
    if date: it['src'][src] = date
    if url: it['urls'].setdefault(src, url)
    if note: it['notes'].append(note)

# --- official daily pages (2000-06-27 → today)
official_dates = set()
for r in e2['records']:
    if r.get('kind') in ('no_issue', 'page404'):
        official_dates.add(r['date']); continue
    if r.get('n') is None or r.get('muk') is None: continue
    official_dates.add(r['date'])
    y, m, d = r['date'][:4], r['date'][5:7], r['date'][8:10]
    url = r.get('url') or f'https://www.resmigazete.gov.tr/eskiler/{y}/{m}/{y}{m}{d}.htm'
    put(r['n'], r['muk'], 'eskiler', r['date'], url, r.get('note'))
# --- archive PDFs (1921 → 2000), identity-reconciled
ident = load('era1_identity.json', [])
HOWTAG = {'visual': 'visual', 'ocr': 'arsiv_ocr', 'between-equal': 'arsiv_infer', 'inferred-weekday': 'arsiv_infer', 'inferred-weekday+day': 'arsiv_infer', 'main': 'arsiv_muk', 'unresolved': 'arsiv_unresolved'}
for r in ident:
    tag = HOWTAG.get(r.get('how'), 'arsiv_unresolved') if r.get('files') else 'arsiv_' + (r.get('why') or 'nofile')
    put(r['n'], r['muk'], tag, r.get('date') if r['muk'] == 0 else None, r.get('url'))
    for nt in r.get('notes', []): put(r['n'], r['muk'], tag, None, None, nt)
    if r['muk']:
        issues[(r['n'], r['muk'])]['era1_muk'] = True
        if r.get('date'): issues[(r['n'], r['muk'])]['muk_date'] = r['date']
# --- Lexpera (2014 → 2026-10-30)
for r in e3['records']:
    put(r['n'], r['muk'], 'lexpera', r['date'], None)

# --- choose a date per main issue
PRI = ['eskiler', 'visual', 'arsiv_ocr', 'arsiv_infer', 'lexpera']
mains = {}
for (n, muk), it in issues.items():
    if muk: continue
    src = it['src']
    ch = next(((src[p], p) for p in PRI if p in src), None)
    mains[n] = {'n': n, 'date': ch[0] if ch else None, 'how': ch[1] if ch else None, 'it': it}
nmax = max(mains)
# dates of otherwise-unreadable issues taken from Resmî Gazete citations (TBMM law/decision records, web sources)
citdec = load('citation_decisions.json', {})
fixed = dict((load('web_citations.json', {}) or {}).get('accepted') or {})
fixed.update(citdec.get('est_fixed') or {})   # TBMM records take precedence over web citations
for k, v in fixed.items():
    n = int(k)
    if n in mains and mains[n]['how'] not in ('eskiler', 'visual', 'arsiv_ocr', 'arsiv_infer'):
        mains[n]['date'] = v['date']; mains[n]['how'] = v.get('how', 'tbmm')
        mains[n]['it']['notes'].append(('tarih ' + v.get('label', 'TBMM kanun/karar kaydındaki Resmî Gazete bilgisinden') + ': ' + '; '.join(v['refs'][:2])) if v.get('refs') else 'tarih atıftan')
# main issue without a readable file but with a mükerrer whose masthead was read: same number, same day
for (n, muk), it in issues.items():
    if muk and it.get('muk_date') and n in mains and not mains[n]['date']:
        mains[n]['date'] = it['muk_date']; mains[n]['how'] = 'muk_kunye'
        mains[n]['it']['notes'].append('asıl sayının PDF’i okunamadı; tarih aynı sayının mükerrer nüshasının künyesinden alındı')
# unresolved / oversized PDFs: infer from neighbours
known = sorted(n for n, r in mains.items() if r['date'])
import bisect
for n, r in mains.items():
    if r['date']: continue
    j = bisect.bisect_left(known, n)
    p = known[j - 1] if j > 0 else None; q = known[j] if j < len(known) else None
    if p is None or q is None: continue
    dp, dq = iso(mains[p]['date']), iso(mains[q]['date'])
    span = (dq - dp).days
    est = dp + datetime.timedelta(days=round(span * (n - p) / (q - p)))
    r['date'] = est.isoformat(); r['how'] = 'tahmin'
    r['range'] = (dp.isoformat(), dq.isoformat())
    u = r['it']['urls']
    why = 'PDF 10 MB sınırını aştığı için indirilemedi' if 'arsiv_big' in u else ('arşivde bu sayının PDF’i bulunamadı' if ('arsiv_404' in u or 'arsiv_misfiled' in u) else 'künye okunamadı')
    r['it']['notes'].append(f'{why}; tarih komşu sayılardan tahmin edildi (en erken {dp.isoformat()}, en geç {dq.isoformat()})' if dp != dq else f'{why}; önceki ve sonraki sayı aynı gün ({dp.isoformat()}) yayımlandığı için tarih kesin')
    if dp == dq: r['how'] = 'arsiv_infer'

# --- rows
rows = []
dropped = []
for (n, muk), it in issues.items():
    if muk == 0:
        r = mains[n]
        rows.append({'n': n, 'muk': 0, 'date': r['date'], 'how': r['how'], 'it': it})
    else:
        main = mains.get(n)
        srcs = it['src']
        if 'eskiler' in srcs: date, how = srcs['eskiler'], 'eskiler'
        elif 'lexpera' in srcs:
            date, how = srcs['lexpera'], 'lexpera'
            if date in official_dates:   # official page for that day exists but lists no such mükerrer
                dropped.append({'n': n, 'muk': muk, 'date': date, 'why': 'yalnızca Lexpera’da var, resmî günlük sayfada yok'}); continue
        elif it.get('era1_muk'):
            date, how = it.get('muk_date') or (main or {}).get('date'), 'arsiv_muk'
            if it.get('muk_date') and main and main.get('date') and it['muk_date'] != main['date']:
                it['notes'].append(f"mükerrer nüshanın künyesindeki tarih ({it['muk_date']}) asıl sayınınkinden ({main['date']}) farklı")
                how = 'visual'
        else: continue
        rows.append({'n': n, 'muk': muk, 'date': date, 'how': how, 'it': it})

# --- validation
mrows = sorted([r for r in rows if r['muk'] == 0], key=lambda r: r['n'])
have = {r['n'] for r in mrows}
missing = [n for n in range(1, nmax + 1) if n not in have]
nonmono = [(a['n'], a['date'], b['n'], b['date']) for a, b in zip(mrows, mrows[1:]) if a['date'] and b['date'] and b['date'] < a['date']]
conflicts = []
for r in rows:
    s = {k: v for k, v in r['it']['src'].items() if v}
    if len(set(s.values())) > 1: conflicts.append({'n': r['n'], 'muk': r['muk'], 'src': s, 'chosen': r['date']})
mdate = {r['n']: r['date'] for r in mrows}
mukdiff = [(r['n'], r['muk'], r['date'], mdate.get(r['n'])) for r in rows if r['muk'] and r['date'] != mdate.get(r['n'])]

def yayin_adi(n):
    if n <= 21: return 'Ceride-i Resmiye'
    if n <= 762: return 'Resmî Ceride'
    return 'T.C. Resmî Gazete'
TAG = {'rg_atif': 'Resmî Gazete metinlerindeki tarih–sayı atfı', 'tbmm': 'TBMM kanun/karar kaydı (Resmî Gazete tarih ve sayısı)', 'web_atif': 'başka resmî metinlerde geçen tarih–sayı atfı', 'muk_kunye': 'aynı sayının mükerrer nüshasının künyesi', 'eskiler': 'resmî site günlük sayfası', 'arsiv_ocr': 'arşiv PDF künyesi (OCR + haftanın günü kontrolü)', 'visual': 'arşiv PDF künyesi (görsel okuma)',
       'arsiv_infer': 'komşu sayılardan kesin çıkarım', 'arsiv_muk': 'asıl sayının tarihi', 'lexpera': 'Lexpera günlük listesi', 'tahmin': 'komşu sayılardan tahmin (kesin değil)'}
def url_of(r):
    u = r['it']['urls']
    for k in ('eskiler', 'arsiv_muk', 'arsiv_ocr', 'visual', 'arsiv_infer', 'arsiv_unresolved', 'arsiv_big', 'arsiv_404', 'arsiv_misfiled', 'arsiv_nofile', 'arsiv_na'):
        if k in u: return u[k]
    if r['date'] and r['date'] >= '2000-06-27':
        return f"https://www.resmigazete.gov.tr/fihrist?tarih={r['date']}" + (f"&mukerrer={r['muk']}" if r['muk'] else '')
    return next(iter(u.values()), '')
final = [r for r in rows if r['date']]
final.sort(key=lambda r: (r['date'], r['n'], r['muk']))
with open(os.path.join(OUTDIR, 'resmi_gazete_sayilari.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['sira', 'tarih', 'gun', 'sayi', 'mukerrer', 'yayin_adi', 'url', 'tarih_kaynagi', 'not'])
    for i, r in enumerate(final, 1):
        d = iso(r['date'])
        w.writerow([i, r['date'], GUN[d.weekday()], r['n'], r['muk'], yayin_adi(r['n']), url_of(r), TAG.get(r['how'], r['how']), ' | '.join(dict.fromkeys(r['it']['notes']))])
json.dump([{'sira': i, 'tarih': r['date'], 'sayi': r['n'], 'mukerrer': r['muk'], 'yayin_adi': yayin_adi(r['n']), 'url': url_of(r), 'tarih_kaynagi': r['how'], 'not': ' | '.join(dict.fromkeys(r['it']['notes'])) or None} for i, r in enumerate(final, 1)],
          open(os.path.join(OUTDIR, 'resmi_gazete_sayilari.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
rep = {'total_rows': len(final), 'mains': sum(1 for r in final if r['muk'] == 0), 'mukerrer': sum(1 for r in final if r['muk']),
       'first': final[0]['date'] if final else None, 'last': final[-1]['date'] if final else None, 'max_number': nmax,
       'missing_numbers': missing, 'nonmonotonic': nonmono, 'mukerrer_date_differs_from_main': mukdiff, 'conflicts': conflicts,
       'dropped_lexpera_only': dropped, 'how_counts': dict(collections.Counter(r['how'] for r in final)),
       'tahmin': [(r['n'], r['date'], mains[r['n']].get('range')) for r in final if r['how'] == 'tahmin']}
json.dump(rep, open(os.path.join(D, 'merge_report.json'), 'w'), ensure_ascii=False, indent=0, default=str)
print({k: (v if not isinstance(v, list) else len(v)) for k, v in rep.items()})
