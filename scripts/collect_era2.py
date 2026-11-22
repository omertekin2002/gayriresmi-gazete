"""İlk derlemenin (15 Kasım 2026) günlük sayfa taramasının (era 2: resmigazete.gov.tr/eskiler/…htm) sonuçlarını, taramayı
yapan iş akışlarının günlüklerinden tek dosyada toplar.
kullanım: collect_era2.py <W> <çıktı.json>

<W>/*/journal.jsonl içindeki `type: result` satırlarının `results` listesinden her gün için bir kayıt alır (aynı gün birden
çok kez varsa main_status'u `ok` olan tercih edilir) ve {gün: kayıt} olarak yazar; çıktı scripts/parse_era2.py'nin girdisidir.
İş akışı günlükleri depoda yok; günlük sayfa sonuçları aynı biçimde (gün → kayıt) kanit/gunluk_sayfalar.json.gz'dedir."""
import json, glob, sys, os
W = sys.argv[1]; OUT = sys.argv[2]
res = {}
for j in glob.glob(os.path.join(W, '*', 'journal.jsonl')):
    for l in open(j, encoding='utf-8'):
        try: r = json.loads(l)
        except Exception: continue
        if r.get('type') != 'result': continue
        v = r.get('result')
        if isinstance(v, dict) and 'results' in v:
            for e in v['results']:
                d = e.get('date')
                if not d: continue
                old = res.get(d)
                if old is None or (old.get('main_status') != 'ok' and e.get('main_status') == 'ok'):
                    res[d] = e
json.dump(res, open(OUT, 'w'), ensure_ascii=False)
print('dates', len(res))
