#!/usr/bin/env python3
"""Listedeki açık kalemleri, resmigazete.gov.tr'ye doğrudan erişebilen bir bilgisayardan tamamlar.

Bulut ortamındaki derlemede iki engel vardı: site yurt dışından erişime kapalıydı ve kullanılan indirme
aracı 10 MB'tan büyük PDF'leri kabul etmiyordu. Bu betik PDF'leri doğrudan (boyut sınırı olmadan) indirir,
künyeyi okur ve sonuçları listeye işler. Yalnızca Python standart kütüphanesi + poppler (pdftotext,
pdftoppm) ya da PyMuPDF (`pip install pymupdf`) gerekir.

Komutlar (depo kökünden çalıştırın):
  python3 scripts/yerel_tamamla.py baglanti            # siteye erişimi ve PDF araçlarını sınar
  python3 scripts/yerel_tamamla.py liste               # data/acik_kalemler.csv'yi yeniden üretir
  python3 scripts/yerel_tamamla.py indir_oku [--tur tahmin,atif,buyuk_mukerrer,kontrol] [--bekle 1.5] [--sakla]
  python3 scripts/yerel_tamamla.py durum               # okunanların özeti; görsel kontrol gerekenleri listeler
  python3 scripts/yerel_tamamla.py uygula [--kuru]     # okumaları listeye işler, tüm çıktıları yeniden yazar
  python3 scripts/yerel_tamamla.py yeni [--bitis YYYY-MM-DD]   # listenin son tarihinden bugüne yeni sayılar
  python3 scripts/yerel_tamamla.py mukerrer_tara --bas 2000-06-27 --son 2013-12-31   # günlük sayfa mükerrer yoklaması (rapor)
  python3 scripts/yerel_tamamla.py arsiv_mukerrer_tara --bas 1 --son 24095          # arsiv/N_k.pdf yoklaması (rapor)
  python3 scripts/yerel_tamamla.py yeniden_yaz         # CSV elle düzeltildiyse: sırala, doğrula, JSON/özet/rapor/README'yi yeniden yaz

Çalışma dosyaları `yerel/` dizinine yazılır (git'e girmez):
  yerel/okuma.jsonl        her indirilen dosya için okuma kaydı (kaldığı yerden devam eder)
  yerel/kunye/<anahtar>.png        ilk sayfanın üst kısmı (künye)
  yerel/sayfa1/<anahtar>.png       otomatik karar verilemeyenlerin ilk sayfasının tamamı
  yerel/gorsel_gerekli.txt         görsel kontrol bekleyen anahtarlar ve görüntü yolları
  yerel/gorsel.json                görsel okuma sonuçları (elle ya da Claude ile doldurulur, biçimi aşağıda)

yerel/gorsel.json biçimi (anahtar → okuma):
  {"15389":   {"tarih": "1975-10-20", "kunyedeki_gun": "Pazartesi", "kunyedeki_sayi": 15389, "mukerrer": false},
   "17915_1": {"tarih": "1982-12-31", "kunyedeki_gun": "Cuma", "kunyedeki_sayi": 17915, "mukerrer": true, "not": "..."},
   "8244":    {"karar": "listede_birak", "not": "künye okunaklı değil"}}
  - "tarih" künyede basılı tarihtir (miladi, YYYY-MM-DD). Basılı tarih açıkça hatalıysa "zorla": true ve "not" ile gerekçe yazın.
  - "karar": "listede_birak" kalemi değiştirmeden kapatır (gerekçesi kanit/yerel_okumalar.jsonl.gz'ye yazılır).
"""
import argparse, collections, csv, datetime, gzip, html, json, os, re, shutil, subprocess, sys, time
import urllib.error, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from rgdate import MONTH_MAP, candidates, fold  # noqa: E402

BASE = 'https://www.resmigazete.gov.tr/'
LISTE = os.path.join(REPO, 'data', 'resmi_gazete_sayilari.csv')
JSONF = os.path.join(REPO, 'data', 'resmi_gazete_sayilari.json')
YILLIK = os.path.join(REPO, 'data', 'yillik_ozet.csv')
RAPOR = os.path.join(REPO, 'data', 'dogrulama_raporu.json')
ACIK = os.path.join(REPO, 'data', 'acik_kalemler.csv')
KANIT = os.path.join(REPO, 'kanit', 'yerel_okumalar.jsonl.gz')
YEREL = os.path.join(REPO, 'yerel')
OKUMA = os.path.join(YEREL, 'okuma.jsonl')
GORSEL = os.path.join(YEREL, 'gorsel.json')
UA = 'Mozilla/5.0 (compatible; gayriresmi-gazete veri derleme)'
GUN = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']
GUN_NO = {fold(g): i for i, g in enumerate(GUN)}

# tarih_kaynagi: JSON'daki kod ↔ CSV'deki etiket (scripts/merge.py ile aynı)
ETIKET = {
    'kunye_duzeltme': 'künyedeki haftanın günü + komşu sayılar (künyedeki gün rakamı hatalı/kırık)',
    'rg_atif': 'Resmî Gazete metinlerindeki tarih–sayı atfı', 'tbmm': 'TBMM kanun/karar kaydı (Resmî Gazete tarih ve sayısı)',
    'web_atif': 'başka resmî metinlerde geçen tarih–sayı atfı', 'muk_kunye': 'aynı sayının mükerrer nüshasının künyesi',
    'eskiler': 'resmî site günlük sayfası', 'arsiv_ocr': 'arşiv PDF künyesi (OCR + haftanın günü kontrolü)',
    'visual': 'arşiv PDF künyesi (görsel okuma)', 'arsiv_infer': 'komşu sayılardan kesin çıkarım', 'arsiv_muk': 'asıl sayının tarihi',
    'lexpera': 'Lexpera günlük listesi', 'tahmin': 'komşu sayılardan tahmin (kesin değil)'}
KOD = {v: k for k, v in ETIKET.items()}
ATIF_KODLARI = ('tbmm', 'rg_atif', 'muk_kunye')
BUYUK_NOT = 'sınırını aştığı için indirilemedi'
# PDF'i okunabilen ama künyesi bir kez daha gözle kontrol edilmesi istenen kalemler (anahtar → gerekçe).
# Derleme sırasında bu listedeki 13 kalemin hepsi kontrol edilip kapatıldı (gerekçeleri listenin `not` kolonunda);
# yeni bir şüpheli künye bulunursa buraya eklenebilir.
KONTROL = {}
KONTROL_KAPATILAN = {
    '54': 'künyede basılı tarih ile haftanın günü tutmuyor', '77': 'künyede basılı tarih ile haftanın günü tutmuyor',
    '207': 'künyede basılı tarih ile haftanın günü tutmuyor', '259': 'künyede basılı tarih ile haftanın günü tutmuyor',
    '494': 'künyede basılı tarih ile haftanın günü tutmuyor', '635': 'künyede basılı tarih ile haftanın günü tutmuyor',
    '18223': 'künyede basılı tarih ile haftanın günü tutmuyor',
    '8244': 'OCR künyede haftanın gününü okuyamadı', '8257': 'OCR künyede haftanın gününü okuyamadı',
    '8266': 'OCR künyede haftanın gününü okuyamadı', '8290': 'OCR künyede haftanın gününü okuyamadı',
    '8291': 'OCR künyede haftanın gününü okuyamadı',
    '588_1': 'mükerrer künyesindeki tarih (1927-05-01) asıl sayınınkinden (1927-04-28) farklı',
}
ACIK_ALANLAR = ['tur', 'anahtar', 'sayi', 'mukerrer', 'pdf_url', 'listedeki_tarih', 'tarih_kaynagi', 'en_erken', 'en_gec', 'aciklama']


# ----------------------------------------------------------------------------- yardımcılar
def iso(s): return datetime.date.fromisoformat(s)


def oku_liste():
    return list(csv.DictReader(open(LISTE, encoding='utf-8')))


def anahtar_url(url):
    m = re.search(r'/arsiv/(\d+(?:_\d+)?)T?\.pdf$', url or '')
    return m.group(1) if m else None


def istek(url, aralik=None, deneme=3, zaman=900, ilk=None):
    """GET; (durum, gövde) döner. 404 → (404, b''); ağ hatasında tekrar dener.
    `ilk` verilirse gövdenin yalnızca ilk `ilk` baytı okunur (sunucu Range'i yok sayıp büyük dosya gönderse bile)."""
    son = None
    for i in range(deneme):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA, **({'Range': aralik} if aralik else {})})
            with urllib.request.urlopen(req, timeout=zaman) as r:
                return r.status, (r.read(ilk) if ilk else r.read())
        except urllib.error.HTTPError as e:
            if e.code in (404, 410):
                return e.code, b''
            son = f'HTTP {e.code}'
        except Exception as e:  # zaman aşımı, bağlantı kopması
            son = f'{type(e).__name__}: {e}'
        time.sleep(5 * (i + 1))
    return None, son.encode() if son else b''


def indir(url, hedef, deneme=3):
    """Büyük dosyayı akış halinde indirir. (durum, bayt) döner."""
    son = None
    for i in range(deneme):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=900) as r, open(hedef + '.part', 'wb') as f:
                shutil.copyfileobj(r, f, 1 << 20)
            os.replace(hedef + '.part', hedef)
            return 200, os.path.getsize(hedef)
        except urllib.error.HTTPError as e:
            if e.code in (404, 410):
                return e.code, 0
            son = f'HTTP {e.code}'
        except Exception as e:
            son = f'{type(e).__name__}: {e}'
        time.sleep(10 * (i + 1))
    return son, 0


def pdf_metin(yol, sayfa):
    if shutil.which('pdftotext'):
        r = subprocess.run(['pdftotext', '-f', str(sayfa), '-l', str(sayfa), yol, '-'], capture_output=True, timeout=300)
        return r.stdout.decode('utf-8', 'replace')
    import fitz  # PyMuPDF
    with fitz.open(yol) as d:
        return d[sayfa - 1].get_text() if len(d) >= sayfa else ''


def pdf_bilgi(yol):
    if shutil.which('pdfinfo'):
        out = subprocess.run(['pdfinfo', yol], capture_output=True, timeout=120).stdout.decode('utf-8', 'replace')
        m = re.search(r'^Pages:\s+(\d+)', out, re.M)
        return int(m.group(1)) if m else None
    import fitz
    with fitz.open(yol) as d:
        return len(d)


def pdf_goruntu(yol, hedef, genislik, yukseklik=None):
    """İlk sayfayı `genislik` px genişlikte gri PNG olarak yazar; yukseklik verilirse üstten kırpar."""
    os.makedirs(os.path.dirname(hedef), exist_ok=True)
    if shutil.which('pdftoppm'):
        cmd = ['pdftoppm', '-f', '1', '-l', '1', '-gray', '-png', '-singlefile', '-scale-to-x', str(genislik), '-scale-to-y', '-1']
        if yukseklik:
            cmd += ['-x', '0', '-y', '0', '-W', str(genislik), '-H', str(yukseklik)]
        subprocess.run(cmd + [yol, hedef[:-4]], capture_output=True, timeout=300)
    else:
        import fitz
        with fitz.open(yol) as d:
            p = d[0]
            z = genislik / p.rect.width
            clip = fitz.Rect(0, 0, p.rect.width, (yukseklik / z) if yukseklik else p.rect.height)
            p.get_pixmap(matrix=fitz.Matrix(z, z), clip=clip, colorspace=fitz.csGRAY).save(hedef)
    return hedef if os.path.isfile(hedef) else None


# ----------------------------------------------------------------------------- açık kalemler
def acik_kalemler(rows):
    """Listedeki her açık kalemi ve tarih aralığını (önceki/sonraki kesin tarihli asıl sayı) üretir."""
    kapali = set()
    if os.path.exists(KANIT):
        for l in gzip.open(KANIT, 'rt', encoding='utf-8'):
            r = json.loads(l)
            if r.get('sonuc') in ('uygulandi', 'listede_birak', 'dogrulandi'):
                kapali.add(r['anahtar'])
    mains = {int(r['sayi']): r for r in rows if r['mukerrer'] == '0'}
    nmax = max(mains)
    guvenilir = lambda r: KOD.get(r['tarih_kaynagi']) != 'tahmin'

    def komsu(n, yon):
        k = n + yon
        while 1 <= k <= nmax and not guvenilir(mains[k]):
            k += yon
        return mains[k]['tarih'] if 1 <= k <= nmax else ''

    out = []
    for r in rows:
        n, muk = int(r['sayi']), int(r['mukerrer'])
        kod = KOD.get(r['tarih_kaynagi'], r['tarih_kaynagi'])
        key = anahtar_url(r['url']) or (f'{n}_{muk}' if muk else str(n))
        tur = None
        if muk == 0 and kod == 'tahmin':
            tur, acik = 'tahmin', 'arşiv PDF\'i 10 MB\'tan büyük; tarih komşu sayılardan tahmin'
        elif muk == 0 and kod in ATIF_KODLARI and n >= 300:   # 293'ün künyesinde gün basılı değil, atıf tarihi kalır
            tur, acik = 'atif', f'arşiv PDF\'i 10 MB\'tan büyük; tarih atıftan ({r["tarih_kaynagi"]}), künyeyle doğrulanmadı'
        elif muk and BUYUK_NOT in (r['not'] or ''):
            tur, acik = 'buyuk_mukerrer', 'mükerrer PDF\'i 10 MB\'tan büyük; içeriği görülmedi, tarihi asıl sayınınki kabul edildi'
        elif key in KONTROL:
            tur, acik = 'kontrol', KONTROL[key]
        if not tur or key in kapali:
            continue
        if muk:
            lo = mains[n]['tarih']; hi = mains[n + 1]['tarih'] if n + 1 in mains else (iso(lo) + datetime.timedelta(days=7)).isoformat()
        else:
            lo, hi = komsu(n, -1) or '1921-01-01', komsu(n, +1) or datetime.date.today().isoformat()
        url = r['url'] if '/arsiv/' in r['url'] else f'{BASE}arsiv/{n}' + (f'_{muk}' if muk else '') + '.pdf'
        out.append({'tur': tur, 'anahtar': key, 'sayi': n, 'mukerrer': muk, 'pdf_url': url, 'listedeki_tarih': r['tarih'],
                    'tarih_kaynagi': r['tarih_kaynagi'], 'en_erken': lo, 'en_gec': hi, 'aciklama': acik})
    return out


def yaz_acik(kalemler):
    with open(ACIK, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=ACIK_ALANLAR)
        w.writeheader(); w.writerows(kalemler)
    print(f'{ACIK}: {len(kalemler)} açık kalem', dict(collections.Counter(k["tur"] for k in kalemler)))


# ----------------------------------------------------------------------------- okuma ve otomatik karar
def otomatik_karar(k, metin):
    cands, wds, sayi, muk = candidates(metin)
    tarihler = sorted({c[0] for c in cands if isinstance(c[0], datetime.date)})
    lo, hi = iso(k['en_erken']), iso(k['en_gec'])
    aralikta = [d for d in tarihler if lo <= d <= hi]
    uyan = [d for d in aralikta if not wds or d.weekday() in wds]
    n = int(k['sayi'])
    kayit = {'adaylar': [d.isoformat() for d in tarihler], 'kunyedeki_gun': [GUN[w] for w in sorted(set(wds))],
             'kunyedeki_sayi': sayi, 'mukerrer_ibaresi': muk}
    neden = None
    if k['tur'] == 'kontrol':
        neden = 'kontrol kalemi: künyeye gözle bakılacak'
    elif len(uyan) != 1:
        neden = f'aralıkta ({lo}…{hi}) haftanın gününe uyan {len(uyan)} tarih adayı'
    elif not wds and lo != hi:
        neden = 'künyede haftanın günü okunamadı'
    elif sayi is not None and sayi != n:
        neden = f'künyede okunan sayı {sayi}, beklenen {n}'
    elif int(k['mukerrer']) and not muk:
        neden = 'künyede "mükerrer" ibaresi okunamadı'
    elif not int(k['mukerrer']) and muk:
        neden = 'asıl sayı beklenirken künyede "mükerrer" ibaresi var'
    if neden:
        kayit.update(durum='gorsel_gerekli', neden=neden, otomatik_tarih=uyan[0].isoformat() if len(uyan) == 1 else None)
        return kayit
    t = uyan[0].isoformat()
    if k['tur'] == 'atif' and t != k['listedeki_tarih']:
        kayit.update(durum='celiski', neden=f'künye {t}, listedeki (atıftan) {k["listedeki_tarih"]}', otomatik_tarih=t)
    else:
        kayit.update(durum='kesin', otomatik_tarih=t)
    return kayit


def son_okumalar():
    rec = {}
    if os.path.exists(OKUMA):
        for l in open(OKUMA, encoding='utf-8'):
            try:
                r = json.loads(l)
            except Exception:
                continue
            rec[r['anahtar']] = r
    return rec


def cmd_indir_oku(a):
    os.makedirs(os.path.join(YEREL, 'pdf'), exist_ok=True)
    turler = set(a.tur.split(','))
    kalemler = [k for k in csv.DictReader(open(ACIK, encoding='utf-8')) if k['tur'] in turler]
    onceki = son_okumalar()
    yap = [k for k in kalemler if onceki.get(k['anahtar'], {}).get('durum') in (None, 'hata')]
    if a.sinir:
        yap = yap[:a.sinir]
    print(f'{len(kalemler)} kalem, {len(yap)} tanesi indirilecek', file=sys.stderr)
    for i, k in enumerate(yap, 1):
        key = k['anahtar']
        pdf = os.path.join(YEREL, 'pdf', key + '.pdf')
        if not (os.path.isfile(pdf) and open(pdf, 'rb').read(5) == b'%PDF-'):
            durum, boyut = indir(k['pdf_url'], pdf)
            time.sleep(a.bekle)
        else:
            durum, boyut = 200, os.path.getsize(pdf)
        r = {'anahtar': key, 'tur': k['tur'], 'sayi': int(k['sayi']), 'mukerrer': int(k['mukerrer']), 'url': k['pdf_url'],
             'en_erken': k['en_erken'], 'en_gec': k['en_gec'], 'listedeki_tarih': k['listedeki_tarih'],
             'zaman': datetime.datetime.now().isoformat(timespec='seconds')}
        if durum != 200:
            r.update(durum='404' if durum in (404, 410) else 'hata', hata=str(durum))
        elif open(pdf, 'rb').read(5) != b'%PDF-':
            r.update(durum='hata', hata='indirilen dosya PDF değil (HTML hata sayfası olabilir)')
            os.remove(pdf)
        else:
            r['bayt'] = boyut
            r['sayfa'] = pdf_bilgi(pdf)
            t1 = pdf_metin(pdf, 1)
            r['text1'] = t1[:3500]
            if len(t1.strip()) < 200:
                r['text2'] = pdf_metin(pdf, 2)[:1500]
            r.update(otomatik_karar(k, t1 + '\n' + r.get('text2', '')))
            r['kunye_png'] = pdf_goruntu(pdf, os.path.join(YEREL, 'kunye', key + '.png'), 1100, 760)
            if r['durum'] != 'kesin':
                r['sayfa1_png'] = pdf_goruntu(pdf, os.path.join(YEREL, 'sayfa1', key + '.png'), 1400)
            if not a.sakla:
                os.remove(pdf)
        with open(OKUMA, 'a', encoding='utf-8') as f:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
        print(f'[{i}/{len(yap)}] {key} {r["durum"]} {r.get("otomatik_tarih") or ""} {r.get("neden") or r.get("hata") or ""}', file=sys.stderr)
    cmd_durum(a)


def cmd_durum(a=None):
    rec = son_okumalar()
    g = json.load(open(GORSEL, encoding='utf-8')) if os.path.exists(GORSEL) else {}
    c = collections.Counter((r['tur'], r['durum']) for r in rec.values())
    for (t, d), n in sorted(c.items()):
        print(f'{t:15s} {d:15s} {n}')
    bekleyen = [r for r in rec.values() if r['durum'] in ('gorsel_gerekli', 'celiski') and r['anahtar'] not in g]
    os.makedirs(YEREL, exist_ok=True)
    with open(os.path.join(YEREL, 'gorsel_gerekli.txt'), 'w', encoding='utf-8') as f:
        for r in bekleyen:
            f.write('\t'.join([r['anahtar'], r['tur'], f'{r["en_erken"]}…{r["en_gec"]}', r.get('neden', ''),
                               r.get('kunye_png') or '', r.get('sayfa1_png') or '']) + '\n')
    print(f'görsel kontrol bekleyen: {len(bekleyen)} (yerel/gorsel_gerekli.txt) · gorsel.json kayıtları: {len(g)}')


# ----------------------------------------------------------------------------- uygulama
def not_parcalari(s):
    return [p for p in (s or '').split(' | ') if p]


def yaz_ciktilar(rows, ek_rapor=None):
    """rows: CSV satırları (dict). Sıralar, sıra numarası verir, doğrular ve data/ dosyalarını yazar."""
    for r in rows:
        r['gun'] = GUN[iso(r['tarih']).weekday()]
    rows.sort(key=lambda r: (r['tarih'], int(r['sayi']), int(r['mukerrer'])))
    for i, r in enumerate(rows, 1):
        r['sira'] = str(i)
    # doğrulama
    mains = sorted((int(r['sayi']), r['tarih']) for r in rows if r['mukerrer'] == '0')
    nums = [n for n, _ in mains]
    hatalar = []
    if nums != list(range(1, len(nums) + 1)):
        hatalar.append('asıl sayı numaraları 1..N kesintisiz değil')
    ihlal = [(a, b) for a, b in zip(mains, mains[1:]) if b[1] < a[1]]
    if ihlal:
        hatalar.append(f'tarih sırası ihlali: {ihlal[:5]}')
    mset = {n for n in nums}
    yetim = [r['sayi'] for r in rows if r['mukerrer'] != '0' and int(r['sayi']) not in mset]
    if yetim:
        hatalar.append(f'asıl sayısı olmayan mükerrer: {yetim[:5]}')
    cift = [k for k, v in collections.Counter((r['sayi'], r['mukerrer']) for r in rows).items() if v > 1]
    if cift:
        hatalar.append(f'çift kayıt: {cift[:5]}')
    if hatalar:
        raise SystemExit('DOĞRULAMA BAŞARISIZ, hiçbir dosya yazılmadı:\n  ' + '\n  '.join(hatalar))
    alanlar = ['sira', 'tarih', 'gun', 'sayi', 'mukerrer', 'yayin_adi', 'url', 'tarih_kaynagi', 'not']
    with open(LISTE, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f); w.writerow(alanlar)
        for r in rows:
            w.writerow([r[k] for k in alanlar])
    json.dump([{'sira': int(r['sira']), 'tarih': r['tarih'], 'sayi': int(r['sayi']), 'mukerrer': int(r['mukerrer']), 'yayin_adi': r['yayin_adi'],
                'url': r['url'], 'tarih_kaynagi': KOD.get(r['tarih_kaynagi'], r['tarih_kaynagi']), 'not': r['not'] or None} for r in rows],
              open(JSONF, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    y = collections.OrderedDict()
    for r in rows:
        e = y.setdefault(r['tarih'][:4], {'yil': r['tarih'][:4], 'asil_sayi': 0, 'mukerrer': 0, 'toplam': 0, 'ilk_sayi': None, 'son_sayi': None, 'tahmini_tarih': 0})
        e['toplam'] += 1
        if r['mukerrer'] == '0':
            n = int(r['sayi']); e['asil_sayi'] += 1
            e['ilk_sayi'] = n if e['ilk_sayi'] is None else min(e['ilk_sayi'], n); e['son_sayi'] = n if e['son_sayi'] is None else max(e['son_sayi'], n)
        else:
            e['mukerrer'] += 1
        if KOD.get(r['tarih_kaynagi']) == 'tahmin':
            e['tahmini_tarih'] += 1
    with open(YILLIK, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['yil', 'asil_sayi', 'mukerrer', 'toplam', 'ilk_sayi', 'son_sayi', 'tahmini_tarih'])
        w.writeheader(); [w.writerow(e) for e in y.values()]
    rap = json.load(open(RAPOR, encoding='utf-8'))
    tah = []
    for r in rows:
        if KOD.get(r['tarih_kaynagi']) == 'tahmin':
            m = re.search(r'en erken (\S+), en geç ([0-9-]+)', r['not'] or '')
            tah.append([int(r['sayi']), r['tarih'], [m.group(1), m.group(2)] if m else None])
    mdate = {int(r['sayi']): r['tarih'] for r in rows if r['mukerrer'] == '0'}
    rap.update({'olusturma_tarihi': datetime.date.today().isoformat(), 'toplam_yayin': len(rows),
                'asil_sayi': len(nums), 'mukerrer': len(rows) - len(nums),
                'ilk': rows[0]['tarih'] + ' / Sayı ' + rows[0]['sayi'], 'son': rows[-1]['tarih'] + ' / Sayı ' + rows[-1]['sayi'],
                'eksik_sayi_numarasi': [], 'tarih_sirasi_ihlali': [],
                'mukerrer_tarihi_asil_sayidan_farkli': [[int(r['sayi']), int(r['mukerrer']), r['tarih'], mdate[int(r['sayi'])]] for r in rows if r['mukerrer'] != '0' and r['tarih'] != mdate[int(r['sayi'])]],
                'tarih_kaynagi_dagilimi': dict(collections.Counter(r['tarih_kaynagi'] for r in rows)), 'tahmini_tarihli_sayilar': tah})
    if ek_rapor:
        rap.setdefault('yerel_tamamlama', []).append(ek_rapor)
    json.dump(rap, open(RAPOR, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    rr = subprocess.run([sys.executable, os.path.join(HERE, 'render_readme.py'), REPO], capture_output=True, text=True)
    print('README:', (rr.stdout or rr.stderr).strip()[:300])
    yaz_acik(acik_kalemler(rows))


def cmd_uygula(a):
    rows = oku_liste()
    by_key = {}
    for r in rows:
        by_key[anahtar_url(r['url']) or (f'{r["sayi"]}_{r["mukerrer"]}' if r['mukerrer'] != '0' else r['sayi'])] = r
    kalemler = {k['anahtar']: k for k in csv.DictReader(open(ACIK, encoding='utf-8'))}
    rec = son_okumalar()
    g = json.load(open(GORSEL, encoding='utf-8')) if os.path.exists(GORSEL) else {}
    kanit, degisen, bekleyen, reddedilen = [], [], [], []
    for key, k in kalemler.items():
        r, gv = rec.get(key), g.get(key)
        row = by_key.get(key)
        if row is None:
            reddedilen.append((key, 'listede satırı bulunamadı')); continue
        ev = {'anahtar': key, 'tur': k['tur'], 'okuma': {x: r.get(x) for x in ('url', 'bayt', 'sayfa', 'durum', 'neden', 'adaylar', 'kunyedeki_gun',
                                                                          'kunyedeki_sayi', 'mukerrer_ibaresi', 'otomatik_tarih', 'text1', 'zaman')} if r else None,
              'gorsel': gv, 'onceki': {'tarih': row['tarih'], 'tarih_kaynagi': row['tarih_kaynagi'], 'not': row['not']}}
        if gv and gv.get('karar') == 'listede_birak':
            ev['sonuc'] = 'listede_birak'; kanit.append(ev); continue
        if gv and gv.get('tarih'):
            tarih, kod, gun, sayi, muk = gv['tarih'], 'visual', gv.get('kunyedeki_gun'), gv.get('kunyedeki_sayi'), gv.get('mukerrer')
        elif r and r.get('durum') == 'kesin':
            tarih, kod, gun, sayi, muk = r['otomatik_tarih'], 'arsiv_ocr', None, r.get('kunyedeki_sayi'), r.get('mukerrer_ibaresi')
        else:
            bekleyen.append(key); continue
        n, m = int(k['sayi']), int(k['mukerrer'])
        sorun = []
        try:
            d = iso(tarih)
        except Exception:
            sorun.append(f'geçersiz tarih {tarih!r}'); d = None
        if d and not (k['en_erken'] <= tarih <= k['en_gec']):
            sorun.append(f'tarih {tarih} aralık dışında ({k["en_erken"]}…{k["en_gec"]})')
        if d and gun and GUN_NO.get(fold(gun)) is not None and GUN_NO[fold(gun)] != d.weekday():
            sorun.append(f'künyedeki gün {gun}, {tarih} ise {GUN[d.weekday()]}')
        if sayi not in (None, '') and int(sayi) != n:
            sorun.append(f'künyedeki sayı {sayi} ≠ {n}')
        if m and muk is False:
            sorun.append('mükerrer olması beklenen dosyada mükerrer ibaresi yok')
        if sorun and not (gv and gv.get('zorla')):
            reddedilen.append((key, '; '.join(sorun))); ev['sonuc'] = 'reddedildi'; ev['sorun'] = sorun; kanit.append(ev); continue
        eski_t, eski_e = row['tarih'], row['tarih_kaynagi']
        if k['tur'] == 'kontrol':
            if tarih == eski_t:
                ev['sonuc'] = 'dogrulandi'; kanit.append(ev)
                row['not'] = ' | '.join(not_parcalari(row['not']) + ['künye yerel indirmeyle yeniden okundu; tarih doğrulandı'])
                degisen.append((key, eski_t, tarih, 'doğrulandı')); continue
        parcalar = []
        for p in not_parcalari(row['not']):
            if BUYUK_NOT in p:
                if 'tahmin edildi' in p:
                    parcalar.append(f'önceki tahmin: {eski_t} ({p[p.find("(") + 1:p.rfind(")")]})' if '(' in p else f'önceki tahmin: {eski_t}')
                continue
            if KOD.get(eski_e) in ATIF_KODLARI and (p.startswith('tarih ') or 'mükerrer nüshasının künyesinden' in p):
                parcalar.append(f'önceki kaynak ({eski_e}, {eski_t}' + (', künyeyle aynı' if eski_t == tarih else ', künyeden farklı') + f'): {p}')
                continue
            parcalar.append(p)
        bas = 'arşiv PDF\'i 10 MB\'tan büyük; künye yerel indirmeyle okundu' if k['tur'] != 'kontrol' else 'künye yerel indirmeyle yeniden okundu'
        if gv and gv.get('zorla'):
            bas += '; basılı tarih kullanılmadı: ' + (gv.get('not') or 'gerekçe yazılmamış')
        elif gv and gv.get('not'):
            bas += '; ' + gv['not']
        if m and tarih != by_key.get(str(n), {}).get('tarih'):
            bas += f'; mükerrer nüshanın künyesindeki tarih ({tarih}) asıl sayınınkinden farklı'
        row['tarih'], row['tarih_kaynagi'], row['not'] = tarih, ETIKET[kod], ' | '.join([bas] + parcalar)
        ev['sonuc'] = 'uygulandi'; ev['yeni'] = {'tarih': tarih, 'tarih_kaynagi': row['tarih_kaynagi']}; kanit.append(ev)
        degisen.append((key, eski_t, tarih, ETIKET[kod]))
    print(f'uygulanacak: {len(degisen)} · bekleyen (okuma/görsel yok): {len(bekleyen)} · reddedilen: {len(reddedilen)}')
    for x in degisen[:400]:
        print('  ', *x)
    for x in reddedilen:
        print('  REDDEDİLDİ', *x)
    if a.kuru:
        print('--kuru: hiçbir dosya yazılmadı'); return
    if not degisen and not any(e.get('sonuc') == 'listede_birak' for e in kanit):
        print('değişiklik yok'); return
    eski = []
    if os.path.exists(KANIT):
        eski = [json.loads(l) for l in gzip.open(KANIT, 'rt', encoding='utf-8')]
    with gzip.open(KANIT, 'wt', encoding='utf-8', compresslevel=9) as f:
        for e in eski + kanit:
            f.write(json.dumps(e, ensure_ascii=False) + '\n')
    yaz_ciktilar(rows, {'tarih': datetime.date.today().isoformat(), 'uygulanan': len(degisen), 'reddedilen': len(reddedilen), 'bekleyen': len(bekleyen)})


# ----------------------------------------------------------------------------- yeni sayılar (günlük sayfalar)
def coz(b):
    try:
        return b.decode('utf-8')
    except UnicodeDecodeError:
        return b.decode('cp1254', 'replace')


def gunluk_oku(b):
    """Günlük sayfa HTML'inden (tarih, sayı, mükerrer no, yayımlanmadı mı) çıkarır."""
    t = html.unescape(re.sub(r'<[^>]+>', ' ', re.sub(r'(?is)<(script|style)[^>]*>.*?</\1>', ' ', coz(b))))
    t = re.sub(r'\s+', ' ', t)
    f = fold(t)
    yok = 'yayimlanmamaktadir' in f or 'yayimlanmamistir' in f
    m = re.search(r'(\d{1,2}) ([a-z]+) (\d{4}) tarihli ve (\d{4,6}) sayili', f)
    sayi, tarih = (int(m.group(4)), None) if m else (None, None)
    if m and MONTH_MAP.get(m.group(2)):
        try:
            tarih = datetime.date(int(m.group(3)), MONTH_MAP[m.group(2)], int(m.group(1)))
        except ValueError:
            pass
    if sayi is None:
        m2 = re.search(r'sayi ?: ?(\d{4,6})', f)
        sayi = int(m2.group(1)) if m2 else None
    if tarih is None:
        cands = candidates(t[:1500])[0]
        tarih = next((c[0] for c in cands if isinstance(c[0], datetime.date)), None)
    mk = re.search(r'(\d+)\s*\.?\s*mukerrer', f)
    return {'tarih': tarih.isoformat() if tarih else None, 'sayi': sayi, 'mukerrer': int(mk.group(1)) if mk else 0, 'yayimlanmadi': yok}


def gunluk_url(d, k=0):
    return f'{BASE}eskiler/{d:%Y}/{d:%m}/{d:%Y%m%d}' + (f'M{k}' if k else '') + '.htm'


def cmd_yeni(a):
    rows = oku_liste()
    mains = sorted((int(r['sayi']), r) for r in rows if r['mukerrer'] == '0')
    # 1) öz-sınama: listede zaten olan son 3 günü yeniden oku, ayrıştırıcı aynı sonucu vermeli
    for n, r in mains[-3:]:
        d = iso(r['tarih'])
        st, b = istek(gunluk_url(d))
        p = gunluk_oku(b) if st == 200 else {}
        ok = st == 200 and p.get('sayi') == n and p.get('tarih') == r['tarih']
        print(f'öz-sınama {r["tarih"]} sayı {n}: {"tamam" if ok else "UYUŞMUYOR"} {p}', file=sys.stderr)
        if not ok:
            raise SystemExit('Ayrıştırıcı bilinen günü doğru okumadı; gunluk_oku() işlevini sayfa yapısına göre düzeltin.')
        time.sleep(a.bekle)
    son_n, son_r = mains[-1]
    bitis = iso(a.bitis) if a.bitis else datetime.date.today()
    d = iso(son_r['tarih']) + datetime.timedelta(days=1)
    yeni, bekleyen = [], son_n + 1
    while d <= bitis:
        st, b = istek(gunluk_url(d)); time.sleep(a.bekle)
        if st != 200:
            print(f'{d} ana sayfa: {st} (sayı yok ya da henüz yayımlanmadı)', file=sys.stderr); d += datetime.timedelta(days=1); continue
        p = gunluk_oku(b)
        if p['yayimlanmadi'] and not p['sayi']:
            print(f'{d}: Resmî Gazete yayımlanmamış', file=sys.stderr); d += datetime.timedelta(days=1); continue
        if p['tarih'] != d.isoformat() or p['sayi'] != bekleyen:
            raise SystemExit(f'{d}: beklenmeyen künye {p} (beklenen sayı {bekleyen}); elle inceleyin: {gunluk_url(d)}')
        yeni.append({'tarih': d.isoformat(), 'sayi': str(p['sayi']), 'mukerrer': '0', 'url': gunluk_url(d)})
        k = 1
        while True:
            st, b = istek(gunluk_url(d, k)); time.sleep(a.bekle)
            if st != 200:
                break
            pm = gunluk_oku(b)
            if pm['sayi'] not in (None, p['sayi']):
                raise SystemExit(f'{gunluk_url(d, k)}: mükerrer sayfasında farklı sayı {pm}')
            yeni.append({'tarih': d.isoformat(), 'sayi': str(p['sayi']), 'mukerrer': str(k), 'url': gunluk_url(d, k)})
            k += 1
        print(f'{d}: sayı {p["sayi"]}, {k - 1} mükerrer', file=sys.stderr)
        bekleyen += 1
        d += datetime.timedelta(days=1)
    if not yeni:
        print('yeni sayı yok'); return
    for y in yeni:
        y.update(gun='', sira='', yayin_adi='T.C. Resmî Gazete', tarih_kaynagi=ETIKET['eskiler'], **{'not': ''})
    print(f'{len(yeni)} yeni satır ({sum(1 for y in yeni if y["mukerrer"] == "0")} asıl)')
    if a.kuru:
        return
    yaz_ciktilar(rows + yeni, {'tarih': datetime.date.today().isoformat(), 'yeni_satir': len(yeni), 'son': yeni[-1]['tarih']})


# ----------------------------------------------------------------------------- yoklama raporları (listeyi değiştirmez)
def cmd_mukerrer_tara(a):
    rows = oku_liste()
    liste = collections.Counter(r['tarih'] for r in rows if r['mukerrer'] != '0' and KOD.get(r['tarih_kaynagi']) == 'eskiler')
    out = os.path.join(YEREL, 'mukerrer_tarama.csv'); os.makedirs(YEREL, exist_ok=True)
    yazilan = set()
    if os.path.exists(out):
        yazilan = {l.split(',')[0] for l in open(out, encoding='utf-8')}
    d, son = iso(a.bas), iso(a.son)
    with open(out, 'a', encoding='utf-8') as f:
        while d <= son:
            if d.isoformat() not in yazilan:
                k = 0
                while True:
                    st, _ = istek(gunluk_url(d, k + 1), aralik='bytes=0-2047', ilk=2048, zaman=60); time.sleep(a.bekle)
                    if st not in (200, 206):
                        break
                    k += 1
                if st not in (200, 206, 404, 410):
                    f.write(f'{d},hata,{st}\n')
                else:
                    f.write(f'{d},{k},{liste.get(d.isoformat(), 0)}\n')
                f.flush()
            d += datetime.timedelta(days=1)
    fark = [l.strip() for l in open(out, encoding='utf-8') if l.split(',')[1] == 'hata' or l.split(',')[1] != l.strip().split(',')[2]]
    print(f'{out}: tarih,sitedeki_mukerrer,listedeki_mukerrer · uyuşmayan/hatalı {len(fark)} gün')
    for l in fark[:50]:
        print('  ', l)


def cmd_arsiv_mukerrer_tara(a):
    rows = oku_liste()
    liste = collections.Counter(int(r['sayi']) for r in rows if r['mukerrer'] != '0' and r['tarih'] < '2000-06-27')
    out = os.path.join(YEREL, 'arsiv_mukerrer_tarama.csv'); os.makedirs(YEREL, exist_ok=True)
    yazilan = set()
    if os.path.exists(out):
        yazilan = {l.split(',')[0] for l in open(out, encoding='utf-8')}
    with open(out, 'a', encoding='utf-8') as f:
        for n in range(a.bas, a.son + 1):
            if str(n) in yazilan:
                continue
            k = 0
            while True:
                st, _ = istek(f'{BASE}arsiv/{n}_{k + 1}.pdf', aralik='bytes=0-1023', ilk=1024, zaman=60); time.sleep(a.bekle)
                if st not in (200, 206):
                    break
                k += 1
            f.write(f'{n},{k if st in (404, 410) else "hata"},{liste.get(n, 0)}\n'); f.flush()
    fark = [l.strip() for l in open(out, encoding='utf-8') if l.split(',')[1] != l.strip().split(',')[2]]
    print(f'{out}: sayi,arsivdeki_mukerrer,listedeki_mukerrer · uyuşmayan/hatalı {len(fark)}')
    for l in fark[:50]:
        print('  ', l)


def cmd_baglanti(a):
    ok = True
    st, b = istek(BASE + 'arsiv/1T.pdf', deneme=1, zaman=60)
    print('arsiv/1T.pdf:', st, 'PDF' if b[:5] == b'%PDF-' else b[:80])
    ok &= st == 200 and b[:5] == b'%PDF-'
    st, b = istek(gunluk_url(datetime.date(2026, 11, 1)), deneme=1, zaman=60)
    p = gunluk_oku(b) if st == 200 else None
    print('eskiler/2026/11/20261101.htm:', st, p)
    ok &= bool(p and p['sayi'] == 33417)
    araclar = [x for x in ('pdftotext', 'pdftoppm', 'pdfinfo') if shutil.which(x)]
    try:
        import fitz  # noqa: F401
        araclar.append('pymupdf')
    except Exception:
        pass
    print('PDF araçları:', araclar or 'YOK — poppler kurun ya da `pip install pymupdf`')
    ok &= bool(araclar)
    print('TAMAM' if ok else 'SORUN VAR')
    sys.exit(0 if ok else 1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest='cmd', required=True)
    sp.add_parser('baglanti')
    sp.add_parser('liste')
    p = sp.add_parser('indir_oku'); p.add_argument('--tur', default='tahmin,atif,buyuk_mukerrer,kontrol'); p.add_argument('--bekle', type=float, default=1.5)
    p.add_argument('--sakla', action='store_true', help='PDF\'leri yerel/pdf/ içinde tut'); p.add_argument('--sinir', type=int, default=0)
    sp.add_parser('durum')
    sp.add_parser('yeniden_yaz')
    p = sp.add_parser('uygula'); p.add_argument('--kuru', action='store_true')
    p = sp.add_parser('yeni'); p.add_argument('--bitis'); p.add_argument('--bekle', type=float, default=1.0); p.add_argument('--kuru', action='store_true')
    p = sp.add_parser('mukerrer_tara'); p.add_argument('--bas', required=True); p.add_argument('--son', required=True); p.add_argument('--bekle', type=float, default=1.0)
    p = sp.add_parser('arsiv_mukerrer_tara'); p.add_argument('--bas', type=int, required=True); p.add_argument('--son', type=int, required=True); p.add_argument('--bekle', type=float, default=1.0)
    a = ap.parse_args()
    if a.cmd == 'liste':
        yaz_acik(acik_kalemler(oku_liste()))
    elif a.cmd == 'yeniden_yaz':
        yaz_ciktilar(oku_liste(), {'tarih': datetime.date.today().isoformat(), 'elle_duzeltme': True})
    else:
        {'baglanti': cmd_baglanti, 'indir_oku': cmd_indir_oku, 'durum': cmd_durum, 'uygula': cmd_uygula, 'yeni': cmd_yeni,
         'mukerrer_tara': cmd_mukerrer_tara, 'arsiv_mukerrer_tara': cmd_arsiv_mukerrer_tara}[a.cmd](a)


if __name__ == '__main__':
    main()
