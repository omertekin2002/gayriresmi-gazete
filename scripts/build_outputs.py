#!/usr/bin/env python3
"""Copy final data into the repository and write the yearly summary + validation summary."""
import csv, json, os, sys, collections, shutil, datetime
D, OUT, REPO = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(os.path.join(REPO, 'data'), exist_ok=True)
for f in ('resmi_gazete_sayilari.csv', 'resmi_gazete_sayilari.json'):
    shutil.copy(os.path.join(OUT, f), os.path.join(REPO, 'data', f))
rows = list(csv.DictReader(open(os.path.join(OUT, 'resmi_gazete_sayilari.csv'), encoding='utf-8')))
y = collections.OrderedDict()
for r in rows:
    yr = r['tarih'][:4]
    e = y.setdefault(yr, {'yil': yr, 'asil_sayi': 0, 'mukerrer': 0, 'toplam': 0, 'ilk_sayi': None, 'son_sayi': None, 'tahmini_tarih': 0})
    e['toplam'] += 1
    if r['mukerrer'] == '0':
        e['asil_sayi'] += 1
        n = int(r['sayi']); e['ilk_sayi'] = n if e['ilk_sayi'] is None else min(e['ilk_sayi'], n); e['son_sayi'] = n if e['son_sayi'] is None else max(e['son_sayi'], n)
    else:
        e['mukerrer'] += 1
    if 'tahmin' in r['tarih_kaynagi']: e['tahmini_tarih'] += 1
with open(os.path.join(REPO, 'data', 'yillik_ozet.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['yil', 'asil_sayi', 'mukerrer', 'toplam', 'ilk_sayi', 'son_sayi', 'tahmini_tarih'])
    w.writeheader(); [w.writerow(e) for e in y.values()]
rep = json.load(open(os.path.join(D, 'merge_report.json')))
src = collections.Counter(r['tarih_kaynagi'] for r in rows)
summary = {
    'olusturma_tarihi': datetime.date.today().isoformat(),
    'toplam_yayin': len(rows), 'asil_sayi': sum(1 for r in rows if r['mukerrer'] == '0'), 'mukerrer': sum(1 for r in rows if r['mukerrer'] != '0'),
    'ilk': rows[0]['tarih'] + ' / Sayı ' + rows[0]['sayi'], 'son': rows[-1]['tarih'] + ' / Sayı ' + rows[-1]['sayi'],
    'eksik_sayi_numarasi': rep['missing_numbers'], 'tarih_sirasi_ihlali': rep['nonmonotonic'],
    'kaynaklar_arasi_celiski': rep['conflicts'], 'mukerrer_tarihi_asil_sayidan_farkli': rep['mukerrer_date_differs_from_main'],
    'yalnizca_lexperada_olup_cikarilan': rep['dropped_lexpera_only'], 'tarih_kaynagi_dagilimi': dict(src),
    'tahmini_tarihli_sayilar': rep['tahmin'],
}
json.dump(summary, open(os.path.join(REPO, 'data', 'dogrulama_raporu.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps({k: (v if not isinstance(v, list) else len(v)) for k, v in summary.items()}, ensure_ascii=False, indent=1))
