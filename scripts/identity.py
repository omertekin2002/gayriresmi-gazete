#!/usr/bin/env python3
"""Era-1 (archive PDFs): decide which issue each downloaded file really is, using the printed masthead
(OCR text + visual reading) instead of trusting the file name. This guards against files paired with the wrong
number during download (parallel batches did this; such files were later re-downloaded one by one, see verify/*.jsonl).
After re-verification no file in the official archive was found to be misfiled.

İlk derleme (15 Kasım 2026) hattının betiği; kullanım: identity.py <D>. Buradaki dosya adları (era1/*.jsonl, verify/*.jsonl,
era1_resolved.json, visual_results.json, visual_dates.json, stale_visual_keys.json) o derlemenin çalışma dizinindedir, depoda
yoktur. Hepsi kanit/'ten kurulabilir: era1/ ve verify/ kanit/arsiv_pdf_ilk_sayfa.jsonl.gz'den (`sirali_yeniden_indirme: true`
olan kayıtlar verify/'a), era1_resolved.json kanit/arsiv_tarih_cozumleme.json.gz, visual_results.json
kanit/gorsel_okumalar.json.gz, visual_dates.json bundan scripts/collect_visual.py kurallarıyla, stale_visual_keys.json
kanit/README.md'de sayılan 24 geçersiz görsel okuma. Böyle kurulan girdilerle çıktı (<D>/era1_identity.json)
kanit/arsiv_kimlik_eslestirme.json.gz ile birebir aynıdır."""
import json, os, sys, glob, re, datetime, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rgdate import candidates, norm_text
D = sys.argv[1]
recs = {}
for f in sorted(glob.glob(os.path.join(D, 'era1', '*.jsonl'))):
    for l in open(f, encoding='utf-8'):
        try: r = json.loads(l)
        except Exception: continue
        k = r['key']; old = recs.get(k)
        if old is None or (old.get('status') != 'ok' and r.get('status') == 'ok') or (old.get('status') == r.get('status') == 'ok'):
            recs[k] = r

# Sequential re-downloads (one URL per request) override earlier parallel-batch records for the same key,
# because parallel batches occasionally paired a downloaded file with the wrong key.
VERIFIED = set()
for _f in sorted(glob.glob(os.path.join(D, 'verify', '*.jsonl'))):
    for _l in open(_f, encoding='utf-8'):
        try: _r = json.loads(_l)
        except Exception: continue
        if _r.get('status') == 'error' and 'maxContent' not in (_r.get('error') or ''): continue
        if _r['key'] in VERIFIED and recs[_r['key']].get('status') == 'ok' and _r.get('status') != 'ok': continue
        recs[_r['key']] = _r; VERIFIED.add(_r['key'])

res = json.load(open(os.path.join(D, 'era1_resolved.json')))
vr = json.load(open(os.path.join(D, 'visual_results.json')))
vd = json.load(open(os.path.join(D, 'visual_dates.json')))
_stale = set(json.load(open(os.path.join(D, 'stale_visual_keys.json')))) if os.path.exists(os.path.join(D, 'stale_visual_keys.json')) else set()
vr = {k: v for k, v in vr.items() if k not in _stale}; vd = {k: v for k, v in vd.items() if k not in _stale}
main_date = {m['n']: (m.get('date'), m.get('how')) for m in res['mains']}

def kp(k):
    m = re.fullmatch(r'(\d+)(?:_(\d+))?(T?)', k)
    return (int(m.group(1)), int(m.group(2) or 0), bool(m.group(3))) if m else None
def digits(s):
    s = re.sub(r'\D', '', s or ''); return int(s) if s else None
def is_big(r): return r.get('status') == 'error' and re.search(r'maxContent|10 ?MB', r.get('error') or '')

files = []
for k, r in recs.items():
    p = kp(k)
    if not p or r.get('status') != 'ok': continue
    n, muk, t = p
    if t and f'{n}' in recs and recs[f'{n}'].get('status') == 'ok' and muk == 0: pass
    txt = (r.get('text1') or '') + '\n' + (r.get('text2') or '')
    c, w, s_ocr, m_ocr = candidates(txt)
    vkey = re.sub(r'T$', '', k)
    v = vr.get(vkey)
    s_vis = digits(v.get('sayi_printed')) if v else None
    m_vis = bool(v.get('mukerrer')) if v else None
    # identity number
    if s_vis and s_ocr and s_vis == s_ocr and 0 < abs(s_vis - n) <= 3: idn = s_vis; idsrc = 'ocr+visual'
    elif s_ocr == n or s_vis == n: idn = n; idsrc = 'filename+print'
    elif muk > 0 and s_vis and v and v.get('confidence') == 'high' and 0 < abs(s_vis - n) <= 3 and (s_ocr is None or abs(s_ocr - n) > 0): idn = s_vis; idsrc = 'visual'
    else: idn = n; idsrc = 'filename'
    # mükerrer or main?
    printed_muk = bool(m_vis) or m_ocr
    if muk > 0:
        kind = 'muk' if (printed_muk or idn == n) else 'main'
    else:
        kind = 'muk' if (m_vis and m_ocr and idn == n) else 'main'
    date = vd.get(vkey)
    if not date and v and v.get('masthead_found') and v.get('iso_date') and v.get('confidence') in ('high', 'medium'):
        try:
            dd = datetime.date.fromisoformat(v['iso_date'])
            wdn = {'pazartesi': 0, 'sali': 1, 'carsamba': 2, 'persembe': 3, 'cuma': 4, 'cumartesi': 5, 'pazar': 6}
            from rgdate import fold
            wv = (fold(v.get('weekday_printed') or '').split() or [''])[0]
            if wv not in wdn or wdn[wv] == dd.weekday(): date = v['iso_date']
        except Exception: pass
    how = 'visual' if date else None
    if not date and kind == 'main' and idn == n:
        date, how = main_date.get(n, (None, None))
    files.append({'key': k, 'n': n, 'kmuk': muk, 'T': t, 'idn': idn, 'idsrc': idsrc, 'kind': kind, 'date': date, 'how': how,
                  'bytes': (r.get('bytes'), hash((r.get('text1') or '')[:3000])), 'url': r.get('url'), 's_ocr': s_ocr, 's_vis': s_vis, 'printed_muk': printed_muk})

# group by identity
mains = collections.defaultdict(list); muks = collections.defaultdict(list)
for f in files:
    (mains if f['kind'] == 'main' else muks)[f['idn']].append(f)
nmax = max([f['n'] for f in files] + [0])
out = []
notes_all = []
for n in range(1, nmax + 1):
    fl = mains.get(n, [])
    # prefer the file whose name matches, then transcription (T), then any
    fl.sort(key=lambda f: (f['n'] != n, not f['T'], f['kmuk']))
    row = {'n': n, 'muk': 0, 'files': [f['key'] for f in fl], 'notes': []}
    if fl:
        f = fl[0]
        row['url'] = f['url']; row['date'] = f['date']; row['how'] = f['how'] or ('ocr' if f['date'] else None)
        if f['n'] != n or f['kmuk']:
            row['notes'].append(f"resmî arşivde bu sayının dosyası {f['url'].rsplit('/', 1)[-1]} adı altında (dosya adı ile künyedeki sayı farklı)")
        if not row['date']:
            row['how'] = None
    else:
        r = recs.get(str(n)) or recs.get(f'{n}T')
        row['url'] = f'https://www.resmigazete.gov.tr/arsiv/{n}.pdf'
        row['date'] = None
        if r and is_big(r): row['why'] = 'big'
        elif r and r.get('status') == 'ok': row['why'] = 'misfiled'; row['notes'].append(f"arsiv/{n}.pdf başka bir sayının künyesini taşıyor; bu sayının kendi dosyası arşivde bulunamadı")
        elif r and r.get('status') == '404': row['why'] = '404'; row['notes'].append(f'arsiv/{n}.pdf resmî arşivde yok (404)')
        else: row['why'] = 'unknown'
    out.append(row)
    ml = sorted(muks.get(n, []), key=lambda f: (f['n'] != n, f['kmuk']))
    seen_bytes = set(); seen_keys = set(); k = 0
    ml.sort(key=lambda f: (f['n'] != n, f['kmuk'], f['T']))   # original scan before its transcription
    mrows = []   # (sort key, row): numbered afterwards in file-suffix order (_1, _2, …), readable or oversized
    for f in ml:
        if f['bytes'] in seen_bytes or (f['n'], f['kmuk']) in seen_keys: continue
        seen_bytes.add(f['bytes']); seen_keys.add((f['n'], f['kmuk']))
        mr = {'n': n, 'files': [f['key']], 'url': f['url'], 'date': f['date'], 'how': f['how'] or 'main', 'notes': []}
        if f['n'] != n: mr['notes'].append(f"resmî arşivde {f['url'].rsplit('/', 1)[-1]} adı altında")
        mrows.append(((f['n'] != n, f['kmuk']), mr))
    # oversized mükerrer files (exist on server, not downloadable): count them as mükerrer of n
    for kk in range(1, 10):
        r = recs.get(f'{n}_{kk}')
        if r is None: break
        if is_big(r) and not any(f['key'] == f'{n}_{kk}' for f in ml):
            mrows.append(((False, kk), {'n': n, 'files': [f'{n}_{kk}'], 'url': f'https://www.resmigazete.gov.tr/arsiv/{n}_{kk}.pdf', 'date': None, 'how': 'main',
                                        'notes': ['PDF 10 MB sınırını aştığı için indirilemedi; tarihi asıl sayınınki kabul edildi']}))
    for k, (_, mr) in enumerate(sorted(mrows, key=lambda x: x[0]), 1):
        mr['muk'] = k; out.append(mr)
json.dump(out, open(os.path.join(D, 'era1_identity.json'), 'w'), ensure_ascii=False, indent=0)
c = collections.Counter('main' if r['muk'] == 0 else 'muk' for r in out)
print(c, 'mains without file:', collections.Counter(r.get('why') for r in out if r['muk'] == 0 and not r.get('files')))
print('misfiled (identity != filename):', sum(1 for f in files if f['idn'] != f['n'] or (f['kind'] == 'main' and f['kmuk'])))
for f in files:
    if f['idn'] != f['n'] or (f['kind'] == 'main' and f['kmuk']): print('  ', f['key'], '->', f['idn'], f['kind'], f['idsrc'], f['date'])
