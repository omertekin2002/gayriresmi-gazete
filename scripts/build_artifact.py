#!/usr/bin/env python3
"""Build the artifact page (single HTML file) from data/resmi_gazete_sayilari.csv.
usage: build_artifact.py <list.csv> <artifact_dir>   (depoda: python3 scripts/build_artifact.py data/resmi_gazete_sayilari.csv site)
rows: [yyyymmdd, n, muk, src, noteIdx(-1 = none), url-path (only when it differs from the page's default URL rule)]"""
import csv, json, os, sys
CSV, A = sys.argv[1], sys.argv[2]
SRC = {'resmî site günlük sayfası': 0, 'arşiv PDF künyesi (OCR + haftanın günü kontrolü)': 1, 'arşiv PDF künyesi (görsel okuma)': 2,
       'asıl sayının tarihi': 3, 'aynı sayının mükerrer nüshasının künyesi': 4, 'komşu sayılardan kesin çıkarım': 5,
       'komşu sayılardan tahmin (kesin değil)': 6, 'TBMM kanun/karar kaydı (Resmî Gazete tarih ve sayısı)': 7,
       'Resmî Gazete metinlerindeki tarih–sayı atfı': 8, 'künyedeki haftanın günü + komşu sayılar (künyedeki gün rakamı hatalı/kırık)': 9}
BASE = 'https://www.resmigazete.gov.tr/'

def default_url(date, n, muk):
    y, m, d = date[:4], date[5:7], date[8:10]
    if date >= '2000-06-27':
        return f'{BASE}eskiler/{y}/{m}/{y}{m}{d}' + (f'M{muk}' if muk else '') + '.htm'
    return f'{BASE}arsiv/{n}' + (f'_{muk}' if muk else '') + ('T' if n <= 1053 and not muk else '') + '.pdf'

rows, notes, nidx = [], [], {}
for r in csv.DictReader(open(CSV, encoding='utf-8')):
    n, muk = int(r['sayi']), int(r['mukerrer'])
    src = SRC[r['tarih_kaynagi']]
    row = [int(r['tarih'].replace('-', '')), n, muk, src]
    note = r['not'] or ''
    url = r['url'] or ''
    alt = url[len(BASE):] if url.startswith(BASE) and url != default_url(r['tarih'], n, muk) else ''
    if note or alt:
        if note and note not in nidx: nidx[note] = len(notes); notes.append(note)
        row.append(nidx[note] if note else -1)
        if alt: row.append(alt)
    rows.append(row)
data = json.dumps({'rows': rows, 'notes': notes}, ensure_ascii=False, separators=(',', ':'))
open(os.path.join(A, 'data.json'), 'w', encoding='utf-8').write(data)
rd = lambda p: open(os.path.join(A, p), encoding='utf-8').read()
html = rd('head.html') + rd('body.html') + '\n' + '<script type="application/json" id="rg-data">' + data.replace('</', '<\\/') + '</script>\n<script>\n' + rd('app.js') + '\n</script>\n'
open(os.path.join(A, 'gayriresmi-gazete.html'), 'w', encoding='utf-8').write(html)
from collections import Counter
print(len(rows), 'rows', len(notes), 'notes', sum(1 for r in rows if len(r) > 5), 'alt urls', dict(Counter(r[3] for r in rows)))
