#!/usr/bin/env python3
"""Copy final data into the repository and write the yearly summary + validation summary.
kullanım: build_outputs.py <D> <OUT> <depo>

İlk derlemenin (15 Kasım 2026) son adımıdır; bakımda kullanılmaz: listeyi, JSON'u, yıllık özeti ve raporu artık
scripts/yerel_tamamla.py yazar. Girdileri ilk derlemenin çalışma dizinindedir ve depoda yoktur: <OUT>/resmi_gazete_sayilari.csv
ve .json (scripts/merge.py çıktısı), <D>/merge_report.json (son hâli kanit/birlestirme_raporu.json.gz) ve
<D>/validation_stats.json (tanımları scripts/atif_dogrula.py'de yeniden kuruldu). Bugünkü depoya karşı çalıştırılırsa data/
dosyalarını <OUT>'taki listeyle değiştirir ve raporu baştan yazar (yerel_tamamlama ve mukerrer_yoklama kayıtları düşer).
Girdilerden biri eksikse ya da okunamıyorsa (UTF-8 olmayan CSV, ayrıştırılamayan JSON), liste boşsa ya da raporda veya
listede beklenen bir alan yoksa hiçbir dosya yazmadan durur: bütün girdiler ilk yazmadan önce okunur, çıktılar bellekte hesaplanır."""
import csv, json, os, sys, collections, shutil, datetime
if len(sys.argv) < 4:
    sys.exit('kullanım: build_outputs.py <D> <OUT> <depo>')
D, OUT, REPO = sys.argv[1], sys.argv[2], sys.argv[3]
# Önce bütün girdiler denetlenir, okunur ve çıktılar bellekte hesaplanır: bir girdi eksik ya da bozuksa data/ yarı yazılmış kalmasın
girdiler = [os.path.join(OUT, 'resmi_gazete_sayilari.csv'), os.path.join(OUT, 'resmi_gazete_sayilari.json'),
            os.path.join(D, 'merge_report.json'), os.path.join(D, 'validation_stats.json')]
eksik = [p for p in girdiler if not os.path.isfile(p)]
if eksik:
    sys.exit('build_outputs.py: girdi eksik, hiçbir dosya yazılmadı (ilk derlemenin çalışma dizini gerekir; listeyi '
             'güncellemek için scripts/yerel_tamamla.py): ' + ', '.join(eksik))
try:
    rep = json.load(open(os.path.join(D, 'merge_report.json')))
    val = json.load(open(os.path.join(D, 'validation_stats.json')))
    # JSON listesi olduğu gibi kopyalanır; burada yalnızca ayrıştırılabildiği denetlenir
    json.load(open(os.path.join(OUT, 'resmi_gazete_sayilari.json'), encoding='utf-8'))
    rows = list(csv.DictReader(open(os.path.join(OUT, 'resmi_gazete_sayilari.csv'), encoding='utf-8')))
    if not rows:
        raise ValueError('resmi_gazete_sayilari.csv içinde satır yok')
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
    src = collections.Counter(r['tarih_kaynagi'] for r in rows)
    summary = {
        'olusturma_tarihi': datetime.date.today().isoformat(),
        'toplam_yayin': len(rows), 'asil_sayi': sum(1 for r in rows if r['mukerrer'] == '0'), 'mukerrer': sum(1 for r in rows if r['mukerrer'] != '0'),
        'ilk': rows[0]['tarih'] + ' / Sayı ' + rows[0]['sayi'], 'son': rows[-1]['tarih'] + ' / Sayı ' + rows[-1]['sayi'],
        'eksik_sayi_numarasi': rep['missing_numbers'], 'tarih_sirasi_ihlali': rep['nonmonotonic'],
        'kaynaklar_arasi_celiski': rep['conflicts'], 'mukerrer_tarihi_asil_sayidan_farkli': rep['mukerrer_date_differs_from_main'],
        'yalnizca_lexperada_olup_cikarilan': rep['dropped_lexpera_only'], 'tarih_kaynagi_dagilimi': dict(src),
        'tahmini_tarihli_sayilar': rep['tahmin'],
        'atif_dogrulama': val,
    }
except (ValueError, KeyError, TypeError) as e:   # UnicodeDecodeError ve JSONDecodeError da ValueError'dur
    sys.exit(f'build_outputs.py: girdi okunamadı ya da beklenen alanı yok, hiçbir dosya yazılmadı ({type(e).__name__}: {e})')
os.makedirs(os.path.join(REPO, 'data'), exist_ok=True)
for f in ('resmi_gazete_sayilari.csv', 'resmi_gazete_sayilari.json'):
    shutil.copy(os.path.join(OUT, f), os.path.join(REPO, 'data', f))
with open(os.path.join(REPO, 'data', 'yillik_ozet.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['yil', 'asil_sayi', 'mukerrer', 'toplam', 'ilk_sayi', 'son_sayi', 'tahmini_tarih'])
    w.writeheader(); [w.writerow(e) for e in y.values()]
json.dump(summary, open(os.path.join(REPO, 'data', 'dogrulama_raporu.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps({k: (v if not isinstance(v, list) else len(v)) for k, v in summary.items()}, ensure_ascii=False, indent=1))
