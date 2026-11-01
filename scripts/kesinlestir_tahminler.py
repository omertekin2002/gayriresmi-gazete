#!/usr/bin/env python3
"""Tahmini tarihli sayıları kesinleştirir.

Türkiye içinden (resmigazete.gov.tr'ye doğrudan erişilebilen bir ağdan) çalıştırın:

    python3 scripts/kesinlestir_tahminler.py data/resmi_gazete_sayilari.csv kesinlesen.csv

Listede `tarih_kaynagi` "tahmin" olan her asıl sayının arşiv PDF'ini indirir (10 MB sınırı yoktur),
ilk sayfanın metninden künyedeki tarih adaylarını çıkarır ve `not` kolonundaki "en erken / en geç"
aralığına ve haftanın gününe uyan tek tarihi seçer. Sonuç CSV'sinde her sayı için bulunan tarih,
künyeden okunan haftanın günü ve kontrol için ilk sayfa metninin başı yer alır.

Gereksinimler: Python 3.9+, `curl`, `pdftotext` (poppler-utils).
"""
import csv, os, re, subprocess, sys, tempfile, datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rgdate import candidates  # noqa: E402

GUN = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']


def main(src, dst):
    rows = [r for r in csv.DictReader(open(src, encoding='utf-8')) if 'tahmin' in r['tarih_kaynagi'] and r['mukerrer'] == '0']
    print(f'{len(rows)} tahmini tarihli sayı', file=sys.stderr)
    out = []
    with tempfile.TemporaryDirectory() as tmp:
        for r in rows:
            n = r['sayi']
            m = re.search(r'en erken (\d{4}-\d\d-\d\d), en geç (\d{4}-\d\d-\d\d)', r['not'] or '')
            lo, hi = (m.group(1), m.group(2)) if m else (None, None)
            pdf = os.path.join(tmp, f'{n}.pdf')
            url = f'https://www.resmigazete.gov.tr/arsiv/{n}.pdf'
            ok = subprocess.run(['curl', '-sSfL', '--max-time', '300', '-o', pdf, url]).returncode == 0
            text = subprocess.run(['pdftotext', '-f', '1', '-l', '1', pdf, '-'], capture_output=True).stdout.decode('utf-8', 'replace') if ok else ''
            cands, wds, sayi, _ = candidates(text)
            dates = sorted({c[0] for c in cands if isinstance(c[0], datetime.date)})
            fit = [d for d in dates if (not lo or lo <= d.isoformat() <= hi) and (not wds or d.weekday() in wds)]
            out.append({'sayi': n, 'eski_tahmin': r['tarih'], 'aralik': f'{lo}…{hi}', 'bulunan_tarih': fit[0].isoformat() if len(fit) == 1 else '',
                        'adaylar': ' '.join(d.isoformat() for d in dates), 'kunyedeki_gun': ','.join(GUN[w] for w in wds),
                        'kunyedeki_sayi': sayi or '', 'indirildi': 'evet' if ok else 'hayır', 'ilk_sayfa': re.sub(r'\s+', ' ', text)[:200]})
            print(n, out[-1]['bulunan_tarih'] or '?', file=sys.stderr)
            if os.path.exists(pdf):
                os.remove(pdf)
    with open(dst, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()) if out else ['sayi'])
        w.writeheader(); w.writerows(out)
    print(f'{sum(1 for o in out if o["bulunan_tarih"])} / {len(out)} sayının tarihi kesinleşti → {dst}', file=sys.stderr)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
