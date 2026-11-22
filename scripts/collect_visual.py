#!/usr/bin/env python3
"""İlk derlemenin (15 Kasım 2026) görsel künye okumalarını, okumayı yapan iş akışlarının günlüklerinden toplar ve listede
kullanılabilecek tarihleri ayırır.
kullanım: collect_visual.py <W> <D>

<W>/*/journal.jsonl içindeki `masthead_found` alanlı okumalardan her anahtar için güveni en yüksek olanı
<D>/visual_results.json'a yazar. <D>/visual_dates.json'a (anahtar → YYYY-MM-DD) yalnızca künyesi bulunmuş, tarihi geçerli,
güveni `low` olmayan, basılı sayı numarası dosya adındakiyle ve basılı gün adı tarihle tutan okumaları koyar.
İş akışı günlükleri ve <D> depoda yok; okumalar aynı biçimde (anahtar → okuma) kanit/gorsel_okumalar.json.gz'dedir ve bu
kurallar oradaki 2.486 okumadan 2.428 tarih kabul eder. kanit/README.md'de sayılan 24 geçersiz okuma burada değil,
scripts/identity.py'de (stale_visual_keys.json) ayıklanır."""
import json, glob, os, sys, re, datetime
W = sys.argv[1]; D = sys.argv[2]
res = {}
for j in glob.glob(os.path.join(W, '*', 'journal.jsonl')):
    for l in open(j, encoding='utf-8'):
        try: r = json.loads(l)
        except Exception: continue
        if r.get('type') != 'result': continue
        v = r.get('result')
        if isinstance(v, dict) and isinstance(v.get('items'), list) and v['items'] and 'masthead_found' in v['items'][0]:
            for it in v['items']:
                k = str(it.get('key', '')).strip()
                k = re.sub(r'T$', '', k)
                old = res.get(k)
                rank = {'high': 3, 'medium': 2, 'low': 1}.get(it.get('confidence'), 0)
                if old is None or rank > {'high': 3, 'medium': 2, 'low': 1}.get(old.get('confidence'), 0):
                    res[k] = it
json.dump(res, open(os.path.join(D, 'visual_results.json'), 'w'), ensure_ascii=False, indent=0)
ovr = {}; rej = []
GUN = {'pazartesi': 0, 'sali': 1, 'carsamba': 2, 'persembe': 3, 'cuma': 4, 'cumartesi': 5, 'pazar': 6}
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rgdate import fold
for k, it in res.items():
    iso = it.get('iso_date')
    if not it.get('masthead_found') or not iso or it.get('confidence') == 'low':
        rej.append((k, 'no/low')); continue
    try: d = datetime.date.fromisoformat(iso)
    except Exception: rej.append((k, 'bad iso')); continue
    sp = re.sub(r'\D', '', it.get('sayi_printed') or '')
    base = k.split('_')[0]
    if sp and sp != base:
        rej.append((k, f'sayi {sp} != key')); continue
    wd = fold(it.get('weekday_printed') or '').strip().split()
    wdn = GUN.get(wd[0]) if wd else None
    if wdn is not None and d.weekday() != wdn:
        rej.append((k, f'weekday {wd} != {d.strftime("%a")}')); continue
    ovr[k] = iso
json.dump(ovr, open(os.path.join(D, 'visual_dates.json'), 'w'), indent=0)
print('visual results', len(res), 'accepted', len(ovr), 'rejected', len(rej))
from collections import Counter
print(Counter(r[1].split()[0] for r in rej))
