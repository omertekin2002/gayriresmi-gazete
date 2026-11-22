#!/usr/bin/env python3
"""Listedeki açık kalemleri, resmigazete.gov.tr'ye doğrudan erişebilen bir bilgisayardan tamamlar.

Bulut ortamındaki derlemede iki engel vardı: site yurt dışından erişime kapalıydı ve kullanılan indirme
aracı 10 MB'tan büyük PDF'leri kabul etmiyordu. Bu betik PDF'leri doğrudan (boyut sınırı olmadan) indirir,
künyeyi okur ve sonuçları listeye işler. Yalnızca Python standart kütüphanesi + poppler (pdftotext,
pdftoppm) ya da PyMuPDF (`pip install pymupdf`) gerekir.

Komutlar (depo kökünden çalıştırın):
  python3 scripts/yerel_tamamla.py baglanti            # siteye erişimi ve PDF araçlarını sınar
  python3 scripts/yerel_tamamla.py liste               # data/acik_kalemler.csv'yi yeniden üretir
  python3 scripts/yerel_tamamla.py indir_oku [--tur tahmin,atif,buyuk_mukerrer,kontrol] [--bekle 1.5] [--sakla] [--sinir N]
  python3 scripts/yerel_tamamla.py yeniden_karar       # indirilmiş künyelerin kararını güncel kural ve aralıklarla yeniden verir (ağa çıkmaz)
  python3 scripts/yerel_tamamla.py durum               # okunanların özeti; görsel kontrol gerekenleri listeler
  python3 scripts/yerel_tamamla.py uygula [--kuru]     # okumaları listeye işler, tüm çıktıları yeniden yazar
  python3 scripts/yerel_tamamla.py yeni [--bitis YYYY-MM-DD]   # listenin son tarihinden bugüne yeni sayılar (+ son günlerin geç gelen mükerrerleri)
  python3 scripts/yerel_tamamla.py mukerrer_tara --bas 2000-06-27 --son 2026-11-17 [--yeniden]   # günlük sayfa mükerrer yoklaması (rapor)
  python3 scripts/yerel_tamamla.py arsiv_mukerrer_tara --bas 1 --son 24095 [--yeniden]         # arsiv/N_k.pdf yoklaması (rapor)
  python3 scripts/yerel_tamamla.py yoklama_ozeti       # yoklama sonuçlarını güncel listeyle karşılaştırır, rapora ve README'ye yazar
  python3 scripts/yerel_tamamla.py yeniden_yaz         # CSV elle düzeltildiyse: sırala, doğrula, JSON/özet/rapor/README'yi yeniden yaz

Çalışma dosyaları `yerel/` dizinine yazılır (git'e girmez):
  yerel/okuma.jsonl        her indirilen dosya için okuma kaydı (kaldığı yerden devam eder)
  yerel/kunye/<anahtar>.png        ilk sayfanın üst kısmı (künye)
  yerel/sayfa1/<anahtar>.png       otomatik karar verilemeyenlerin ilk sayfasının tamamı
  yerel/gorsel_gerekli.txt         görsel kontrol bekleyen anahtarlar ve görüntü yolları
  yerel/gorsel.json                görsel okuma sonuçları (elle ya da Claude ile doldurulur, biçimi aşağıda)

yerel/gorsel.json biçimi (anahtar → okuma):
  {"15389":   {"tarih": "1975-10-20", "kunyedeki_gun": "Pazartesi", "kunyedeki_sayi": 15389, "mukerrer": false},
   "17915_1": {"tarih": "1982-12-31", "kunyedeki_gun": "Cuma", "kunyedeki_sayi": 17915, "mukerrer": true, "mukerrer_sirasi": null, "not": "..."},
   "15873":   {"tarih": "1977-03-09", "kunyedeki_gun": "Çarşamba", "kunyedeki_sayi": 15973, "mukerrer": false,
               "sayi_baski_hatasi": true, "not": "künyede 15973 basılı; içerik ve komşu sayılar 15873'ü gösteriyor"},
   "8244":    {"karar": "listede_birak", "not": "künye okunaklı değil"}}
  - Bir okuma kaydında "tarih", "kunyedeki_gun", "kunyedeki_sayi" ve "mukerrer" (true/false) ZORUNLUDUR; künyede gerçekten
    basılı olmayan ya da okunamayan gün adı / sayı için değer null yazılır ve nedeni "not" alanında açıklanır. Bilinmeyen
    alan adı, tanınmayan gün adı ya da sayı olmayan bir "kunyedeki_sayi" kaydın tümünü reddettirir ("zorla" bunu aşamaz).
  - "tarih" künyede basılı tarihtir (miladi, YYYY-MM-DD; Rumi 1336–1341 yılları için +584). `uygula` tarihi komşu sayıların
    verdiği aralıkla (en_erken…en_gec), gün adıyla ve künyedeki sayı numarasıyla denetler; tutmayan kayıt reddedilir.
    Asıl sayı beklenirken "mukerrer": true ya da mükerrer dosyasında "mukerrer": false her durumda reddedilir.
  - "mukerrer_sirasi": künyede basılı mükerrer sırası ("2 nci Mükerrer" → 2; sıra basılı değilse null). Dosya adındaki
    sırayla (`_1`, `_2`) tutmayan kayıt reddedilir; `_2` ve sonrası dosyalarda yazılması zorunludur.
  - Basılı tarih açıkça bir baskı hatasıysa (ör. gün adı ve komşu sayılar başka bir günü gösteriyorsa) "tarih"e listeye
    yazılacak DOĞRU tarihi koyun, "zorla": true ekleyin ve "not" alanına kanıtı yazın; "not" boşsa kayıt reddedilir.
    "zorla" yalnızca aralık / gün adı / sayı numarası uyuşmazlığını ve otomatik kararla çelişkiyi aşar; asıl sayı / mükerrer
    ve mükerrer sırası uyuşmazlığını aşmaz.
  - Künyede sayı numarasının bir hanesi kırık, silik ya da yanlış basılmışsa: "kunyedeki_sayi"ya BASILI numarayı yazın,
    "sayi_baski_hatasi": true ekleyin ve "not" alanında açıklayın. Tarih ve gün adı denetimi aynen yapılır.
  - Aynı kalem için hem otomatik (OCR) karar hem görsel okuma varsa ve tarihleri farklıysa kayıt reddedilir ("zorla" ile aşılır).
  - "karar": "listede_birak" kalemi değiştirmeden kapatır (gerekçesi kanit/yerel_okumalar.jsonl.gz'ye yazılır);
    "karar": "beklet" kalemi açık bırakır (otomatik karar olsa bile uygulanmaz). İkisinde de "not" zorunludur.
"""
import argparse, collections, contextlib, csv, datetime, gzip, html, json, os, re, shutil, subprocess, sys, time
import urllib.error, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from rgdate import MONTH_MAP, candidates, fold, norm_text  # noqa: E402

BASE = 'https://www.resmigazete.gov.tr/'
LISTE = os.path.join(REPO, 'data', 'resmi_gazete_sayilari.csv')
JSONF = os.path.join(REPO, 'data', 'resmi_gazete_sayilari.json')
YILLIK = os.path.join(REPO, 'data', 'yillik_ozet.csv')
RAPOR = os.path.join(REPO, 'data', 'dogrulama_raporu.json')
ACIK = os.path.join(REPO, 'data', 'acik_kalemler.csv')
KANIT = os.path.join(REPO, 'kanit', 'yerel_okumalar.jsonl.gz')
KANIT_GUNLUK = os.path.join(REPO, 'kanit', 'yerel_gunluk.jsonl.gz')   # `yeni` komutunun siteden okuduğu günlük sayfalar
YEREL = os.path.join(REPO, 'yerel')
OKUMA = os.path.join(YEREL, 'okuma.jsonl')
GORSEL = os.path.join(YEREL, 'gorsel.json')
TARAMA_GUNLUK = os.path.join(YEREL, 'mukerrer_tarama.csv')
TARAMA_ARSIV = os.path.join(YEREL, 'arsiv_mukerrer_tarama.csv')
KANIT_YOKLAMA = os.path.join(REPO, 'kanit', 'yerel_mukerrer_yoklama.json.gz')   # yoklama_ozeti'nin özetlediği ham yoklama sonuçları
YAZIM = os.path.join(YEREL, 'yazim_bitmedi')   # yaz_ciktilar() çalışırken durur; kalmışsa önceki çalışma çıktıları yazarken kesilmiştir
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
# Yeni bir şüpheli künye bulunursa anahtarı buraya eklenir: `liste` + `indir_oku --tur kontrol` dosyayı yeniden indirir, künyeye
# bakılıp yerel/gorsel.json doldurulur ve `uygula` çalıştırılır (kontrol kalemlerinde otomatik karar verilmez). Kalem kapanınca
# anahtarı KONTROL_KAPATILAN'a taşıyın: kapanmış olması yalnızca kanıt dosyasındaki kayda bağlı kalmasın. Daha önce bu yolla
# kapatılmış bir anahtar, kanıt kaydındakinden FARKLI bir gerekçe metniyle eklendiğinde yeniden açılır; yerel/gorsel.json'da duran
# eski okuması yeniden uygulanmaz (künye yeniden indirilip okunur, kayıt güncellenir). Kanıt kaydında gerekçe ("kontrol_gerekcesi")
# yoksa karşılaştırılacak metin de yoktur: anahtar hangi metinle eklenirse eklensin (KONTROL_KAPATILAN'daki metinle de) kalem yeniden
# açılır. Kasım 2026'da işlenen dokuz kontrol kaleminin (6126, 10908, 11979, 24273_1, 24281_1, 244, 293, 1054, 1056) kanıt
# kayıtları bu alan eklenmeden önce yazıldı.
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
    # Yerel tamamlama (Kasım 2026); sonuçları kanit/yerel_okumalar.jsonl.gz'de ve listenin `not` kolonunda.
    # İlk üçünde OCR metninin gövdesindeki başka bir tarih, künyedeki tarihin yerine seçilmişti: tarihleri düzeltildi.
    '6126': 'liste tarihi (1945-10-07) künyede basılı gün adıyla (Cumartesi) tutmuyordu; 1945-10-06 olarak düzeltildi',
    '10908': 'liste tarihi (1961-09-15) künyede basılı gün adıyla (Cumartesi) tutmuyordu; 1961-09-16 olarak düzeltildi',
    '11979': 'liste tarihi (1965-04-20) künyede basılı gün adıyla (Pazartesi) tutmuyordu; 1965-04-19 olarak düzeltildi',
    # Günlük sayfadan tarihlenen iki mükerrerin 10 MB'tan büyük arşiv PDF'i: künyeleri okundu, tarih doğrulandı.
    '24273_1': 'günlük sayfadan tarihlenen mükerrerin 10 MB\'tan büyük arşiv PDF\'i; künyesi okundu, tarih doğrulandı',
    '24281_1': 'günlük sayfadan tarihlenen mükerrerin 10 MB\'tan büyük arşiv PDF\'i; künyesi okundu, tarih doğrulandı',
    # Künyesinde gün rakamı basılı olmayan / ay adı yanlış basılmış dört sayı: künyeleri yeniden okundu, tarih doğrulandı.
    '244': 'künyede ay adı yanlış basılmış; tarih künyedeki gün adı ve komşu sayılardan (doğrulandı)',
    '293': 'künyede gün rakamı basılı değil; tarih TBMM kaydından, künyedeki gün adı ve komşu sayılarla doğrulandı',
    '1054': 'künyede gün rakamı basılı değil; tarih künyedeki gün adı ve komşu sayılardan (doğrulandı)',
    '1056': 'künyede gün rakamı basılı değil; tarih künyedeki gün adı ve komşu sayılardan (doğrulandı)',
}
ACIK_ALANLAR = ['tur', 'anahtar', 'sayi', 'mukerrer', 'pdf_url', 'listedeki_tarih', 'tarih_kaynagi', 'en_erken', 'en_gec', 'aciklama']


# ----------------------------------------------------------------------------- yardımcılar
def iso(s): return datetime.date.fromisoformat(s)


def oku_liste():
    return list(csv.DictReader(open(LISTE, encoding='utf-8')))


@contextlib.contextmanager
def yaz(yol, **kw):
    """Çıktı dosyasını önce <yol>.tmp'ye yazar, bitince yerine koyar: yarıda kesilen çalışma dosyayı boş ya da yarım bırakmaz."""
    kw.setdefault('newline', '\n')   # Windows'ta da LF: depodaki dosyalarla aynı baytlar (csv yazıcıları newline='' ile kendi satır sonunu yazar)
    with open(yol + '.tmp', 'w', encoding='utf-8', **kw) as f:
        yield f
    os.replace(yol + '.tmp', yol)


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
                beklenen = r.headers.get('Content-Length')
                shutil.copyfileobj(r, f, 1 << 20)
            alinan = os.path.getsize(hedef + '.part')
            if beklenen and beklenen.isdigit() and alinan != int(beklenen):
                raise IOError(f'eksik indirme: {alinan}/{beklenen} bayt')
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
_BUYUK = None


def buyuk_dosyalar():
    """Bulut taramasında sunucunun var olduğunu bildirdiği ama 10 MB sınırı yüzünden indirilemeyen arşiv dosyaları."""
    global _BUYUK
    if _BUYUK is None:
        _BUYUK = set()
        yol = os.path.join(REPO, 'kanit', 'arsiv_pdf_ilk_sayfa.jsonl.gz')
        for l in gzip.open(yol, 'rt', encoding='utf-8'):
            if '"error"' in l:
                r = json.loads(l)
                if r.get('status') == 'error' and re.search(r'maxContent|10 ?MB', r.get('error') or ''):   # identity.py ile aynı kural
                    _BUYUK.add(r['key'])
    return _BUYUK


def acik_kalemler(rows):
    """Listedeki her açık kalemi ve tarih aralığını (önceki/sonraki kesin tarihli asıl sayı) üretir."""
    kapali = set()
    if os.path.exists(KANIT):
        satir = {anahtar_url(r['url']) or (f'{r["sayi"]}_{r["mukerrer"]}' if r['mukerrer'] != '0' else r['sayi']): r for r in rows}
        for l in gzip.open(KANIT, 'rt', encoding='utf-8'):
            r = json.loads(l)
            if r['anahtar'] in KONTROL and r.get('kontrol_gerekcesi') != KONTROL[r['anahtar']]:
                continue   # anahtar KONTROL'e bu kayıttan sonra (yeniden) eklenmiş: eski kayıt kalemi kapalı tutmaz
            # 'uygulandi' kalemler kaynak etiketi değiştiği için zaten düşer; 'kontrol' kalemleri ise etiketle değil KONTROL
            # sözlüğüyle seçildiğinden burada kapatılır. Kanıt dosyası listeden ÖNCE yazılır: çalışma arada kesildiyse satır hâlâ
            # kayıttaki "önceki" hâlindedir; o durumda kalem açık kalır ve bir sonraki `uygula` onu yeniden işler.
            if r.get('sonuc') == 'listede_birak':
                kapali.add(r['anahtar'])
            elif r.get('sonuc') == 'dogrulandi' or (r.get('sonuc') == 'uygulandi' and r.get('tur') == 'kontrol'):
                x, o = satir.get(r['anahtar']), r['onceki']
                if x and (x['tarih'], x['tarih_kaynagi'], x['not']) != (o['tarih'], o['tarih_kaynagi'], o['not']):
                    kapali.add(r['anahtar'])
    eksik = sorted(set(KONTROL) - {anahtar_url(r['url']) or (f'{r["sayi"]}_{r["mukerrer"]}' if r['mukerrer'] != '0' else r['sayi']) for r in rows})
    if eksik and eksik != getattr(acik_kalemler, 'uyarilan', None):   # aynı çalışmada bir kez söylenir
        acik_kalemler.uyarilan = eksik
        print(f'UYARI: KONTROL sözlüğündeki {", ".join(map(repr, eksik))} listede hiçbir satırla eşleşmiyor (yazım hatası olabilir); iş listesine girmedi')
    buyuk = buyuk_dosyalar()
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
        elif muk and key in buyuk and kod == 'arsiv_muk':   # sunucu "çok büyük" dedi ve künyesi henüz okunmadı
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
# Künyedeki "Mükerrer" ibaresi: kendi satırında ("Mükerrer", "2. Mükerrer", "(Mükerrer)") ya da "Sayı : N Mükerrer" satırında.
# Gövde metnindeki "… tarihli ve 17914 mükerrer sayılı Resmî Gazete" / "… 20666 sayılı mükerrer Resmî Gazete" atıfları sayılmaz.
_MUK_SATIR = re.compile(r'(?m)^[^\na-z0-9]*(?:s\s*a\s*[yj]\s*[i1la]\s*[:;.]?\s*[\d ]+\s+)?(?:(\d)\s*[.\-]?\s*)?mukerrer[^\na-z0-9]*$')


def kunye_isaretleri(metin, n):
    """(sayı numarası künye metninde ayrı bir sözcük olarak geçiyor mu, künyede "Mükerrer" ibaresi var mı, basılı mükerrer sırası)."""
    t = norm_text(metin)
    m = _MUK_SATIR.search(t[:900])
    sira = (int(m.group(1)) if m.group(1) else 1) if m else 0
    sayi_var = bool(re.search(r'(?<!\d)' + r'\s?'.join(str(n)) + r'(?!\d)', t[:700]))
    return sayi_var, bool(m), sira


def otomatik_karar(k, metin, sayfa2=False):
    """Künye metninden otomatik karar. `sayfa2`: ilk sayfada metin yoksa ve karar metni 2. sayfadan geliyorsa True."""
    cands, wds, sayi, _ = candidates(metin)
    tarihler = sorted({c[0] for c in cands if isinstance(c[0], datetime.date)})
    lo, hi = iso(k['en_erken']), iso(k['en_gec'])
    aralikta = [d for d in tarihler if lo <= d <= hi]
    uyan = [d for d in aralikta if not wds or d.weekday() in wds]
    n, m = int(k['sayi']), int(k['mukerrer'])
    sayi_var, muk, sira = kunye_isaretleri(metin, n)
    kayit = {'adaylar': [d.isoformat() for d in tarihler], 'kunyedeki_gun': [GUN[w] for w in sorted(set(wds))],
             'kunyedeki_sayi': sayi, 'sayi_metinde': sayi_var, 'mukerrer_ibaresi': muk, 'mukerrer_sirasi': sira or None}
    neden = None
    if k['tur'] == 'kontrol':
        neden = 'kontrol kalemi: künyeye gözle bakılacak'
    elif sayfa2:
        neden = 'ilk sayfada metin yok; 2. sayfanın metninden otomatik karar verilmez'
    elif len(uyan) != 1:
        neden = f'aralıkta ({lo}…{hi}) haftanın gününe uyan {len(uyan)} tarih adayı'
    elif wds and uyan[0].weekday() != wds[0]:   # candidates() gün adlarını metin sırasıyla verir: ilki künyedekidir
        neden = 'tarih, künye metnindeki ilk gün adıyla tutmuyor (gövdedeki başka bir tarih olabilir)'
    elif not wds and lo != hi:
        neden = 'künyede haftanın günü okunamadı'
    elif sayi is not None and sayi != n:
        neden = f'künyede okunan sayı {sayi}, beklenen {n}'
    elif sayi is None and not sayi_var:
        neden = 'künyede sayı numarası okunamadı'
    elif m and not muk:
        neden = 'künyede "mükerrer" ibaresi okunamadı'
    elif not m and muk:
        neden = 'asıl sayı beklenirken künyede "mükerrer" ibaresi var'
    elif m and sira != m:
        neden = f'künyedeki mükerrer sırası {sira}, dosya adındaki {m}'
    if neden:
        kayit.update(durum='gorsel_gerekli', neden=neden, otomatik_tarih=uyan[0].isoformat() if len(uyan) == 1 else None)
        return kayit
    t = uyan[0].isoformat()
    if k['tur'] == 'atif' and t != k['listedeki_tarih']:
        kayit.update(durum='celiski', neden=f'künye {t}, listedeki (atıftan) {k["listedeki_tarih"]}', otomatik_tarih=t)
    else:
        kayit.update(durum='kesin', otomatik_tarih=t)
    return kayit


def guncel_karar(k, r):
    """Saklanan okuma kaydının kararını güncel tür, güncel aralık ve güncel kuralla yeniden verir (dosyaya dokunmaz)."""
    if r and 'text1' in r:
        r = {x: v for x, v in r.items() if x not in ('durum', 'neden', 'otomatik_tarih')}
        r.update(otomatik_karar(k, r['text1'] + '\n' + r.get('text2', ''), sayfa2='text2' in r), tur=k['tur'])
    return r


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
    # kaydı olmayan / hatalı kalanlar, türü okumadan sonra değişenler (KONTROL'e sonradan eklenenler) ve başka bir gerekçeyle
    # yeniden açılan kontrol kalemleri indirilir
    yap = [k for k in kalemler if onceki.get(k['anahtar'], {}).get('durum') in (None, 'hata') or onceki[k['anahtar']].get('tur') != k['tur']
           or (k['tur'] == 'kontrol' and onceki[k['anahtar']].get('kontrol_gerekcesi') != k['aciklama'])]
    if a.sinir:
        yap = yap[:a.sinir]
    print(f'{len(kalemler)} kalem, {len(yap)} tanesi indirilecek', file=sys.stderr)
    for i, k in enumerate(yap, 1):
        key = k['anahtar']
        pdf = os.path.join(YEREL, 'pdf', key + '.pdf')
        # KONTROL'e (yeniden) eklenen kalem: önceki okumadan `--sakla` ile yerel/pdf/ içinde kalmış kopya okunmaz, dosya yeniden indirilir
        if k['tur'] == 'kontrol' and key in onceki and onceki[key].get('kontrol_gerekcesi') != k['aciklama'] and os.path.isfile(pdf):
            os.remove(pdf)
        if not (os.path.isfile(pdf) and open(pdf, 'rb').read(5) == b'%PDF-'):
            durum, boyut = indir(k['pdf_url'], pdf)
            time.sleep(a.bekle)
        else:
            durum, boyut = 200, os.path.getsize(pdf)
        r = {'anahtar': key, 'tur': k['tur'], 'sayi': int(k['sayi']), 'mukerrer': int(k['mukerrer']), 'url': k['pdf_url'],
             'en_erken': k['en_erken'], 'en_gec': k['en_gec'], 'listedeki_tarih': k['listedeki_tarih'],
             'zaman': datetime.datetime.now().isoformat(timespec='seconds')}
        if k['tur'] == 'kontrol':
            r['kontrol_gerekcesi'] = k['aciklama']
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
            r.update(otomatik_karar(k, t1 + '\n' + r.get('text2', ''), sayfa2='text2' in r))
            r['kunye_png'] = pdf_goruntu(pdf, os.path.join(YEREL, 'kunye', key + '.png'), 1100, 760)
            if r['durum'] != 'kesin':
                r['sayfa1_png'] = pdf_goruntu(pdf, os.path.join(YEREL, 'sayfa1', key + '.png'), 1400)
            if not a.sakla:
                os.remove(pdf)
        with open(OKUMA, 'a', encoding='utf-8') as f:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
        print(f'[{i}/{len(yap)}] {key} {r["durum"]} {r.get("otomatik_tarih") or ""} {r.get("neden") or r.get("hata") or ""}', file=sys.stderr)
    cmd_durum(a)


def cmd_yeniden_karar(a=None):
    """İndirilip okunmuş künyelerin kararını güncel kurallar ve güncel tarih aralıklarıyla yeniden verir; ağa çıkmaz.
    (Kurallar sıkılaştırıldığında ya da komşu sayıların tarihi kesinleşip aralıklar değiştiğinde kullanılır.)"""
    kalemler = {k['anahtar']: k for k in acik_kalemler(oku_liste())}
    degisen = 0
    for key, r in son_okumalar().items():
        k = kalemler.get(key)
        if not k or 'text1' not in r:
            continue
        yeni = dict(r)
        for x in ('neden', 'otomatik_tarih', 'durum'):
            yeni.pop(x, None)
        yeni.update(otomatik_karar(k, r['text1'] + '\n' + r.get('text2', ''), sayfa2='text2' in r))
        yeni.update(tur=k['tur'], en_erken=k['en_erken'], en_gec=k['en_gec'], listedeki_tarih=k['listedeki_tarih'])
        ayni = all(yeni.get(x) == r.get(x) for x in ('durum', 'otomatik_tarih', 'neden', 'en_erken', 'en_gec', 'tur',
                                                     'sayi_metinde', 'mukerrer_ibaresi', 'mukerrer_sirasi')) and 'sayi_metinde' in r
        if ayni:
            continue
        pdf = os.path.join(YEREL, 'pdf', key + '.pdf')
        if yeni['durum'] != 'kesin' and not yeni.get('sayfa1_png') and os.path.isfile(pdf):
            yeni['sayfa1_png'] = pdf_goruntu(pdf, os.path.join(YEREL, 'sayfa1', key + '.png'), 1400)
        yeni['yeniden_karar'] = datetime.datetime.now().isoformat(timespec='seconds')
        with open(OKUMA, 'a', encoding='utf-8') as f:
            f.write(json.dumps(yeni, ensure_ascii=False) + '\n')
        degisen += 1
        print(f'{key}: {r.get("durum")} {r.get("otomatik_tarih") or ""} → {yeni["durum"]} {yeni.get("otomatik_tarih") or ""} {yeni.get("neden") or ""}', file=sys.stderr)
    print(f'yeniden karar: {degisen} kayıt değişti')
    cmd_durum(a)


def gorsel_eski(key, ham, row, eski):
    """gorsel.json kaydı, bu anahtar için daha önce işlenmiş okumanın birebir aynısı mı? Öyleyse kalem yeniden açıldıktan sonra
    künyeye bakılmamıştır: kayıt uygulanmaz, kalem bekler. (Satır kanıt kaydındaki "önceki" hâlindeyse o kayıt yarıda kesilmiş
    bir çalışmanındır; engel değildir.)"""
    simdi = {'tarih': row['tarih'], 'tarih_kaynagi': row['tarih_kaynagi'], 'not': row['not']}
    return any(e['anahtar'] == key and e.get('gorsel') == ham and
               (e.get('sonuc') == 'listede_birak' or (e.get('sonuc') in ('uygulandi', 'dogrulandi') and e.get('onceki') != simdi)) for e in eski)


def cmd_durum(a=None):
    rec = son_okumalar()
    g = json.load(open(GORSEL, encoding='utf-8')) if os.path.exists(GORSEL) else {}
    rows = oku_liste()
    satir = {anahtar_url(r['url']) or (f'{r["sayi"]}_{r["mukerrer"]}' if r['mukerrer'] != '0' else r['sayi']): r for r in rows}
    eski = [json.loads(l) for l in gzip.open(KANIT, 'rt', encoding='utf-8')] if os.path.exists(KANIT) else []
    acik = {k['anahtar']: k for k in acik_kalemler(rows)}   # güncel iş listesi ve güncel tarih aralıkları
    eski_aralik = {key: (r.get('en_erken'), r.get('en_gec')) for key, r in rec.items()}
    rec = {key: guncel_karar(acik[key], r) if key in acik else r for key, r in rec.items()}   # `uygula` ile aynı karar
    c = collections.Counter((r['tur'], r['durum'], 'açık' if r['anahtar'] in acik else 'kapandı') for r in rec.values())
    for (t, d, ac), n in sorted(c.items()):
        print(f'{t:15s} {d:15s} {ac:8s} {n}')
    def girildi(key):   # gorsel.json'da biçimi geçerli, 'beklet' olmayan (ve daha önce işlenmemiş) bir kayıt var mı
        if key not in g or gorsel_eski(key, g[key], satir[key], eski):
            return False
        gv, sorun = gorsel_denetle(g[key])
        return not sorun and gv.get('karar') != 'beklet'
    bekleyen = [r for r in rec.values() if r['anahtar'] in acik and r['durum'] in ('gorsel_gerekli', 'celiski') and not girildi(r['anahtar'])]
    eskimis = [r['anahtar'] for r in rec.values() if r['anahtar'] in acik and 'text1' in r
               and eski_aralik[r['anahtar']] != (acik[r['anahtar']]['en_erken'], acik[r['anahtar']]['en_gec'])]
    os.makedirs(YEREL, exist_ok=True)
    with open(os.path.join(YEREL, 'gorsel_gerekli.txt'), 'w', encoding='utf-8') as f:
        for r in bekleyen:
            k = acik[r['anahtar']]
            f.write('\t'.join([r['anahtar'], r['tur'], f'{k["en_erken"]}…{k["en_gec"]}', r.get('neden', ''),
                               r.get('kunye_png') or '', r.get('sayfa1_png') or '']) + '\n')
    print(f'görsel kontrol bekleyen: {len(bekleyen)} (yerel/gorsel_gerekli.txt) · gorsel.json kayıtları: {len(g)}')
    if eskimis:
        print(f'tarih aralığı okumadan sonra değişen {len(eskimis)} kalem var ({", ".join(eskimis[:8])}…): `yeniden_karar` çalıştırın')


# ----------------------------------------------------------------------------- uygulama
def not_parcalari(s):
    return [p for p in (s or '').split(' | ') if p]


def kanit_denetle(rows=None):
    """Listeye ya da rapora göre yerel okumalar uygulanmışsa kanıt dosyası da yerinde olmalıdır: kapanan kalemler ve README'deki
    "künye aynı / farklı" sayıları oradan okunur. Dosya yoksa hiçbir şey yazmadan çıkar."""
    if os.path.exists(KANIT):
        return
    # Çalışma günlüğü tek başına yeterli değil: yarıda kesilip onarılan bir `uygula` günlüğe 'uygulanan' yazmaz; liste ise her zaman gösterir
    listede = any('künye yerel indirmeyle' in (r.get('not') or '') for r in (oku_liste() if rows is None else rows))
    gunlukte = os.path.exists(RAPOR) and any(e.get('uygulanan') or e.get('kapatilan')
                                             for e in json.load(open(RAPOR, encoding='utf-8')).get('yerel_tamamlama', []))
    if listede or gunlukte:
        raise SystemExit('kanit/yerel_okumalar.jsonl.gz yok ama listeye / rapora göre yerel okumalar uygulanmış; dosyayı geri getirin '
                         '(ör. git checkout -- kanit/yerel_okumalar.jsonl.gz). Hiçbir dosya yazılmadı.')


def dogrula(rows):
    """Listenin bütünlüğünü denetler; sorun varsa hiçbir şey yazmadan çıkar."""
    try:
        for r in rows:
            if not re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', r['tarih']):
                raise ValueError(f'{r["tarih"]!r} YYYY-AA-GG biçiminde değil (sayı {r["sayi"]})')
            iso(r['tarih'])
    except ValueError as e:
        raise SystemExit(f'DOĞRULAMA BAŞARISIZ, hiçbir dosya yazılmadı: geçersiz tarih ({e})')
    mains = sorted((int(r['sayi']), r['tarih']) for r in rows if r['mukerrer'] == '0')
    nums = [n for n, _ in mains]
    hatalar = []
    if nums != list(range(1, len(nums) + 1)):
        hatalar.append('asıl sayı numaraları 1..N kesintisiz değil')
    ihlal = [(a, b) for a, b in zip(mains, mains[1:]) if b[1] < a[1]]
    if ihlal:
        hatalar.append(f'tarih sırası ihlali: {ihlal[:5]}')
    # Art arda iki asıl sayı aynı tarihi taşımaz: ilk derlemenin 10908 ve 11979 hatalarında (künye yerine OCR metninin
    # gövdesindeki tarih seçilmişti) liste tarihi komşu sayınınkiyle aynıydı (EKSIKLER.md 3.1)
    ayni_gun = [(a, b) for a, b in zip(mains, mains[1:]) if b[1] == a[1]]
    if ayni_gun:
        hatalar.append(f'art arda iki asıl sayı aynı tarihte: {ayni_gun[:5]}')
    # tarih_kaynagi yalnızca ETIKET'teki etiketlerden biri olabilir (elle düzeltmedeki bir yazım hatası JSON'a ve
    # scripts/build_artifact.py'ye ulaşmasın)
    etiketsiz = [(r['sayi'], r['mukerrer'], r['tarih_kaynagi']) for r in rows if r['tarih_kaynagi'] not in KOD]
    if etiketsiz:
        hatalar.append(f'tanınmayan tarih_kaynagi etiketi (geçerli etiketler: scripts/yerel_tamamla.py ETIKET): {etiketsiz[:5]}')
    mset = {n for n in nums}
    yetim = [r['sayi'] for r in rows if r['mukerrer'] != '0' and int(r['sayi']) not in mset]
    if yetim:
        hatalar.append(f'asıl sayısı olmayan mükerrer: {yetim[:5]}')
    mt = dict(mains)   # her mükerrer, asıl sayısının tarihi ile bir sonraki asıl sayının tarihi arasında olmalı
    sapan = [(r['sayi'], r['mukerrer'], r['tarih']) for r in rows if r['mukerrer'] != '0' and int(r['sayi']) in mt
             and not mt[int(r['sayi'])] <= r['tarih'] <= mt.get(int(r['sayi']) + 1, '9999-12-31')]
    if sapan:
        hatalar.append(f'mükerrer tarihi, asıl sayısı ile bir sonraki asıl sayının tarihleri arasında değil: {sapan[:5]}')
    cift = [k for k, v in collections.Counter((r['sayi'], r['mukerrer']) for r in rows).items() if v > 1]
    if cift:
        hatalar.append(f'çift kayıt: {cift[:5]}')
    if hatalar:
        raise SystemExit('DOĞRULAMA BAŞARISIZ, hiçbir dosya yazılmadı:\n  ' + '\n  '.join(hatalar))


def readme_uyarilari(rr):
    """render_readme.py çıktısındaki «UYARI: …» satırlarını (ör. GUN_AY listesi `not` kolonuyla tutmuyor) kısaltmadan basar ve
    çıktının geri kalanını döndürür. README'yi yeniden üreten her yol bunu çağırır: uyarı hiçbir yolda yutulmasın."""
    kalan = []
    for l in (rr.stdout or '').splitlines():
        if l.startswith('UYARI'):
            print('README:', l)
        else:
            kalan.append(l)
    return '\n'.join(kalan)


def yaz_ciktilar(rows, ek_rapor=None):
    """rows: CSV satırları (dict). Doğrular, sıralar, sıra numarası verir ve data/ dosyalarını yazar."""
    dogrula(rows)
    kanit_denetle(rows)
    os.makedirs(YEREL, exist_ok=True)
    # Liste ve JSON'u değiştirmeyen bir `yeniden_yaz` (elle düzeltme yapılmadan çalıştırılmış) "Liste tarihi"ni ilerletmez ve
    # çalışma günlüğüne kayıt düşmez; yarıda kesilmiş bir yazımın (YAZIM işareti) onarımı bunun dışındadır.
    onceki_cikti = None if os.path.exists(YAZIM) else [open(p, 'rb').read() if os.path.exists(p) else None for p in (LISTE, JSONF)]
    open(YAZIM, 'w').close()   # bütün çıktılar yazılınca silinir; `uygula` kalmış işareti görürse çıktıları yeniden yazar
    for r in rows:
        r['gun'] = GUN[iso(r['tarih']).weekday()]
    rows.sort(key=lambda r: (r['tarih'], int(r['sayi']), int(r['mukerrer'])))
    for i, r in enumerate(rows, 1):
        r['sira'] = str(i)
    nums = [int(r['sayi']) for r in rows if r['mukerrer'] == '0']
    alanlar = ['sira', 'tarih', 'gun', 'sayi', 'mukerrer', 'yayin_adi', 'url', 'tarih_kaynagi', 'not']
    with yaz(LISTE, newline='') as f:
        w = csv.writer(f); w.writerow(alanlar)
        for r in rows:
            w.writerow([r[k] for k in alanlar])
    with yaz(JSONF) as f:
        json.dump([{'sira': int(r['sira']), 'tarih': r['tarih'], 'sayi': int(r['sayi']), 'mukerrer': int(r['mukerrer']), 'yayin_adi': r['yayin_adi'],
                    'url': r['url'], 'tarih_kaynagi': KOD.get(r['tarih_kaynagi'], r['tarih_kaynagi']), 'not': r['not'] or None} for r in rows],
                  f, ensure_ascii=False, indent=0)
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
    with yaz(YILLIK, newline='') as f:
        w = csv.DictWriter(f, fieldnames=['yil', 'asil_sayi', 'mukerrer', 'toplam', 'ilk_sayi', 'son_sayi', 'tahmini_tarih'])
        w.writeheader(); [w.writerow(e) for e in y.values()]
    rap = json.load(open(RAPOR, encoding='utf-8'))
    degismedi = (onceki_cikti is not None and None not in onceki_cikti and onceki_cikti == [open(p, 'rb').read() for p in (LISTE, JSONF)]
                 and bool(ek_rapor) and set(ek_rapor) == {'tarih', 'elle_duzeltme'} and bool(rap.get('olusturma_tarihi')))
    tah = []
    for r in rows:
        if KOD.get(r['tarih_kaynagi']) == 'tahmin':
            m = re.search(r'en erken (\S+), en geç ([0-9-]+)', r['not'] or '')
            tah.append([int(r['sayi']), r['tarih'], [m.group(1), m.group(2)] if m else None])
    mdate = {int(r['sayi']): r['tarih'] for r in rows if r['mukerrer'] == '0'}
    rap.update({'olusturma_tarihi': rap['olusturma_tarihi'] if degismedi else datetime.date.today().isoformat(), 'toplam_yayin': len(rows),
                'asil_sayi': len(nums), 'mukerrer': len(rows) - len(nums),
                'ilk': rows[0]['tarih'] + ' / Sayı ' + rows[0]['sayi'], 'son': rows[-1]['tarih'] + ' / Sayı ' + rows[-1]['sayi'],
                'eksik_sayi_numarasi': [], 'tarih_sirasi_ihlali': [],
                'mukerrer_tarihi_asil_sayidan_farkli': [[int(r['sayi']), int(r['mukerrer']), r['tarih'], mdate[int(r['sayi'])]] for r in rows if r['mukerrer'] != '0' and r['tarih'] != mdate[int(r['sayi'])]],
                'tarih_kaynagi_dagilimi': dict(collections.Counter(r['tarih_kaynagi'] for r in rows)), 'tahmini_tarihli_sayilar': tah})
    # Bağımsız atıflarla doğrulama istatistikleri: liste değiştikçe (atıftan/tahminden gelen tarihler künyeden kesinleştikçe)
    # karşılaştırma kümesi de değişir; bu yüzden her yazışta depodaki kanıt dosyalarından yeniden hesaplanır.
    import atif_dogrula
    st, detay, uyarilar = atif_dogrula.hesapla(REPO)      # az önce yazılan CSV'yi okur
    e1, dag = detay['ARSIV_ILK_SAYFA_ATIFLARI'], rap['tarih_kaynagi_dagilimi']
    yerel = collections.Counter()
    if os.path.exists(KANIT):
        for l in gzip.open(KANIT, 'rt', encoding='utf-8'):
            e = json.loads(l)
            if e.get('tur') == 'atif' and e.get('sonuc') == 'uygulandi':
                yerel['ATIF_KUNYE_AYNI' if e['yeni']['tarih'] == e['onceki']['tarih'] else 'ATIF_KUNYE_FARKLI'] += 1
            if e.get('tur') == 'tahmin' and e.get('sonuc') == 'uygulandi':
                yerel['TAHMIN_KUNYE_AYNI' if e['yeni']['tarih'] == e['onceki']['tarih'] else 'TAHMIN_KUNYE_FARKLI'] += 1
    rap['atif_dogrulama'] = dict(
        st, TBMM_SIRAYA_SIGAN=len(detay['TBMM_SIRAYA_SIGAN']), TBMM_DIGER=len(detay['TBMM_DIGER']), HF_SIRAYA_SIGAN=len(detay['HF_SIRAYA_SIGAN']),
        ERA1_SAYI=e1['SAYI'], ERA1_AYNI=e1['AYNI'], ERA1_FARK=e1['FARK'], ERA1_IMKANSIZ=e1['IMKANSIZ'],
        TBMM_COZ=dag.get(ETIKET['tbmm'], 0), RG_COZ=dag.get(ETIKET['rg_atif'], 0),
        ATIF_KUNYE_AYNI=yerel['ATIF_KUNYE_AYNI'], ATIF_KUNYE_FARKLI=yerel['ATIF_KUNYE_FARKLI'],
        TAHMIN_KUNYE_AYNI=yerel['TAHMIN_KUNYE_AYNI'], TAHMIN_KUNYE_FARKLI=yerel['TAHMIN_KUNYE_FARKLI'])
    for u in uyarilar:
        print('UYARI (atıf doğrulama):', u)
    if ek_rapor and not degismedi:
        gunluk = rap.setdefault('yerel_tamamlama', [])
        # Yalnızca sayaç taşımayan kayıtlar (elle düzeltme, onarım) art arda yinelenmez. `uygula` ve `yeni` kayıtları sayaç taşır:
        # aynı gün aynı sayaçlarla iki ayrı çalışma olabilir (sabah günün sayısı, akşam geç yayımlanan mükerreri), ikisi de yazılır.
        sayacsiz = set(ek_rapor) <= {'tarih', 'elle_duzeltme', 'onarim'}
        if not (sayacsiz and gunluk and gunluk[-1] == ek_rapor):
            gunluk.append(ek_rapor)
    with yaz(RAPOR) as f:
        json.dump(rap, f, ensure_ascii=False, indent=1)
    rr = subprocess.run([sys.executable, os.path.join(HERE, 'render_readme.py'), REPO], capture_output=True, text=True)
    print('README:', (readme_uyarilari(rr) or rr.stderr).strip()[:300])
    yaz_acik(acik_kalemler(rows))
    os.remove(YAZIM)
    if rr.returncode:
        raise SystemExit('README.md yeniden üretilemedi (veri dosyaları yazıldı): ' + rr.stderr.strip()[-400:])


GORSEL_ALANLAR = {'tarih', 'kunyedeki_gun', 'kunyedeki_sayi', 'mukerrer', 'mukerrer_sirasi', 'not', 'zorla', 'sayi_baski_hatasi', 'karar'}
KARARLAR = ('listede_birak', 'beklet')


def gorsel_denetle(gv):
    """yerel/gorsel.json'daki bir kaydın biçimini denetler; (temizlenmiş kayıt, sorun listesi) döner.
    Biçim sorunu olan kayıt hiç uygulanmaz ("zorla" yalnızca içerik uyuşmazlıklarını aşar)."""
    if not isinstance(gv, dict):
        return None, ['kayıt bir nesne değil']
    g = {x: (v.strip() if isinstance(v, str) else v) for x, v in gv.items()}
    sorun = []
    bilinmeyen = sorted(set(g) - GORSEL_ALANLAR)
    if bilinmeyen:
        sorun.append('bilinmeyen alan: ' + ', '.join(bilinmeyen))
    notu = g.get('not')
    if notu is not None and not isinstance(notu, str):
        sorun.append('"not" bir metin olmalı')
        notu = ''
    for b in ('zorla', 'sayi_baski_hatasi'):
        if b in g and not isinstance(g[b], bool):
            sorun.append(f'"{b}" true ya da false olmalı')
    if 'karar' in g:
        karar = fold(g['karar']) if isinstance(g['karar'], str) else None
        if karar not in KARARLAR:
            sorun.append(f'bilinmeyen karar {g["karar"]!r} (geçerli: {", ".join(KARARLAR)})')
        g['karar'] = karar
        if not notu:
            sorun.append('"karar" için gerekçe ("not") yazılmamış')
        if g.get('tarih'):
            sorun.append('"karar" ile birlikte "tarih" verilemez')
        return g, sorun
    for alan in ('tarih', 'kunyedeki_gun', 'kunyedeki_sayi', 'mukerrer'):
        if alan not in g:
            sorun.append(f'zorunlu alan eksik: {alan}')
    try:
        if not (isinstance(g.get('tarih'), str) and re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', g['tarih'])):
            raise ValueError
        iso(g['tarih'])
    except Exception:
        sorun.append(f'geçersiz tarih {g.get("tarih")!r} (YYYY-AA-GG olmalı)')
    gun = g.get('kunyedeki_gun')
    if gun is None:
        if 'kunyedeki_gun' in g and not notu:
            sorun.append('"kunyedeki_gun" null ise nedeni "not" alanına yazılmalı')
    elif not isinstance(gun, str) or GUN_NO.get(fold(gun)) is None:
        sorun.append(f'tanınmayan gün adı {gun!r}')
    sayi = g.get('kunyedeki_sayi')
    if isinstance(sayi, str) and sayi.isascii() and sayi.isdigit():
        g['kunyedeki_sayi'] = sayi = int(sayi)
    if sayi is None:
        if 'kunyedeki_sayi' in g and not notu:
            sorun.append('"kunyedeki_sayi" null ise nedeni "not" alanına yazılmalı')
    elif isinstance(sayi, bool) or not isinstance(sayi, int):
        sorun.append(f'"kunyedeki_sayi" bir sayı değil: {sayi!r}')
    if 'mukerrer' in g and not isinstance(g['mukerrer'], bool):
        sorun.append('"mukerrer" true ya da false olmalı')
    ms = g.get('mukerrer_sirasi')
    if ms is not None and (isinstance(ms, bool) or not isinstance(ms, int)):
        sorun.append(f'"mukerrer_sirasi" bir sayı ya da null olmalı: {ms!r}')
    if (g.get('zorla') or g.get('sayi_baski_hatasi')) and not notu:
        sorun.append('"zorla" / "sayi_baski_hatasi" için gerekçe ("not") yazılmamış')
    return g, sorun


def cmd_uygula(a):
    kanit_denetle()
    rows = oku_liste()
    by_key = {}
    for r in rows:
        by_key[anahtar_url(r['url']) or (f'{r["sayi"]}_{r["mukerrer"]}' if r['mukerrer'] != '0' else r['sayi'])] = r
    # İş listesi diskteki CSV'den değil güncel listeden kurulur: yarıda kesilmiş bir çalışmadan sonra yinelemek zararsızdır
    # ve tarih aralıkları (komşu sayılar kesinleştikçe daralır) her zaman günceldir.
    kalemler = {k['anahtar']: k for k in acik_kalemler(rows)}
    rec = son_okumalar()
    g = json.load(open(GORSEL, encoding='utf-8')) if os.path.exists(GORSEL) else {}
    if not isinstance(g, dict):
        raise SystemExit('yerel/gorsel.json bir nesne (anahtar → okuma) olmalı')

    def farkli_mukerrerler():
        asil = {r['sayi']: r['tarih'] for r in rows if r['mukerrer'] == '0'}
        return {(r['sayi'], r['mukerrer']): (r['tarih'], asil.get(r['sayi'])) for r in rows if r['mukerrer'] != '0' and r['tarih'] != asil.get(r['sayi'])}
    fark_once = farkli_mukerrerler()
    kanit, degisen, bekleyen, reddedilen, kapanan = [], [], [], [], []
    eski = [json.loads(l) for l in gzip.open(KANIT, 'rt', encoding='utf-8')] if os.path.exists(KANIT) else []
    eski_gorselli = []   # yeniden açılmış kalemler: gorsel.json'daki kayıt daha önce işlenmiş okumanın aynısı

    def reddet(key, ev, sorun):
        reddedilen.append((key, '; '.join(sorun)))
        ev['sonuc'] = 'reddedildi'; ev['sorun'] = sorun; kanit.append(ev)

    for key, k in kalemler.items():
        r, ham = rec.get(key), g.get(key)
        r = guncel_karar(k, r)   # karar saklanan kayıttan alınmaz: güncel tür, güncel aralık ve güncel kuralla yeniden verilir
        row = by_key.get(key)
        if row is None:
            reddedilen.append((key, 'listede satırı bulunamadı')); continue
        ev = {'anahtar': key, 'tur': k['tur'], 'kontrol_gerekcesi': KONTROL.get(key),
              'okuma': {x: r.get(x) for x in ('url', 'bayt', 'sayfa', 'durum', 'neden', 'adaylar', 'kunyedeki_gun', 'kunyedeki_sayi', 'sayi_metinde',
                                             'mukerrer_ibaresi', 'mukerrer_sirasi', 'otomatik_tarih', 'text1', 'text2', 'zaman', 'yeniden_karar')} if r else None,
              'gorsel': ham, 'aralik': [k['en_erken'], k['en_gec']],
              'onceki': {'tarih': row['tarih'], 'tarih_kaynagi': row['tarih_kaynagi'], 'not': row['not']}}
        gv = None
        if ham is not None and gorsel_eski(key, ham, row, eski):
            bekleyen.append(key); eski_gorselli.append(key); continue
        if ham is not None:
            gv, bicim = gorsel_denetle(ham)
            if bicim:
                reddet(key, ev, ['gorsel.json: ' + s for s in bicim]); continue
            if gv.get('karar') == 'beklet':
                bekleyen.append(key); continue
            if gv.get('karar') == 'listede_birak':
                ev['sonuc'] = 'listede_birak'; kanit.append(ev); kapanan.append((key, gv['not'])); continue
        n, m = int(k['sayi']), int(k['mukerrer'])
        otomatik = r['otomatik_tarih'] if r and r.get('durum') == 'kesin' else None
        if gv:
            tarih, kod, gun, sayi, muk, sira = gv['tarih'], 'visual', gv['kunyedeki_gun'], gv['kunyedeki_sayi'], gv['mukerrer'], gv.get('mukerrer_sirasi')
        elif otomatik:
            tarih, kod, gun, sayi, muk, sira = otomatik, 'arsiv_ocr', None, r.get('kunyedeki_sayi'), bool(r.get('mukerrer_ibaresi')), r.get('mukerrer_sirasi')
        else:
            bekleyen.append(key); continue
        d = iso(tarih)
        asilabilir, kesin_sorun, sayi_notu = [], [], None      # asilabilir: "zorla" ile aşılabilen içerik uyuşmazlıkları
        if not (k['en_erken'] <= tarih <= k['en_gec']):
            asilabilir.append(f'tarih {tarih} aralık dışında ({k["en_erken"]}…{k["en_gec"]})')
        if gun and GUN_NO[fold(gun)] != d.weekday():
            asilabilir.append(f'künyedeki gün {gun}, {tarih} ise {GUN[d.weekday()]}')
        baski = bool(gv and gv.get('sayi_baski_hatasi'))
        if sayi is not None and int(sayi) != n:
            if baski:
                sayi_notu = f'künyede sayı numarası {sayi} olarak basılı (doğrusu {n})'
            else:
                asilabilir.append(f'künyedeki sayı {sayi}, beklenen {n}')
        elif baski and sayi is None:
            sayi_notu = 'künyedeki sayı numarası tam okunamıyor'
        elif baski:
            kesin_sorun.append('"sayi_baski_hatasi" verilmiş ama künyedeki sayı beklenenle aynı')
        if gv and otomatik and otomatik != tarih:
            asilabilir.append(f'görsel okuma ({tarih}) otomatik OCR kararıyla ({otomatik}) çelişiyor')
        if m and muk is not True:
            kesin_sorun.append('mükerrer olması beklenen dosyanın künyesinde mükerrer ibaresi yok')
        if not m and muk is True:
            kesin_sorun.append('asıl sayı beklenirken künyede mükerrer ibaresi var')
        if m and muk is True and sira is not None and sira != m:
            kesin_sorun.append(f'künyedeki mükerrer sırası {sira}, dosya adındaki {m}')
        if m >= 2 and muk is True and sira is None:
            kesin_sorun.append(f'{m}. mükerrer dosyası için künyedeki sıra ("mukerrer_sirasi") yazılmalı')
        zorla = bool(gv and gv.get('zorla'))
        sorun = kesin_sorun + ([] if zorla else asilabilir)
        if sorun:
            reddet(key, ev, sorun); continue
        eski_t, eski_e = row['tarih'], row['tarih_kaynagi']
        if k['tur'] == 'kontrol' and tarih == eski_t:
            ev['sonuc'] = 'dogrulandi'; kanit.append(ev)
            ek = 'künye yerel indirmeyle yeniden okundu; tarih doğrulandı' + (f' ({gv["not"]})' if gv and gv.get('not') else '')
            row['not'] = ' | '.join(not_parcalari(row['not']) + [ek])
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
        if k['tur'] == 'kontrol':
            bas = f'künye yerel indirmeyle yeniden okundu; tarih düzeltildi (önceki: {eski_t}, {eski_e})'
        else:
            bas = 'arşiv PDF\'i 10 MB\'tan büyük; künye yerel indirmeyle okundu'
        if zorla:
            bas += '; tarih elle verildi' + (', künye denetimi geçmedi (' + '; '.join(asilabilir) + ')' if asilabilir else ' ("zorla")') + ': ' + gv['not']
        elif sayi_notu:
            bas += f'; {sayi_notu}: {gv["not"]}'
        elif gv and gv.get('not'):
            bas += '; ' + gv['not']
        if m and tarih != by_key.get(str(n), {}).get('tarih'):
            bas += f'; mükerrer nüshanın künyesindeki tarih ({tarih}) asıl sayınınkinden farklı'
        row['tarih'], row['tarih_kaynagi'], row['not'] = tarih, ETIKET[kod], ' | '.join([bas] + parcalar)
        ev['sonuc'] = 'uygulandi'; ev['yeni'] = {'tarih': tarih, 'tarih_kaynagi': row['tarih_kaynagi']}; kanit.append(ev)
        degisen.append((key, eski_t, tarih, ETIKET[kod]))
    bilinen = set(kalemler) | {e['anahtar'] for e in eski}
    yabanci = sorted(x for x in g if x not in bilinen)
    print(f'uygulanacak: {len(degisen)} · kapatılacak (listede_birak): {len(kapanan)} · bekleyen (okuma/görsel yok): {len(bekleyen)} · reddedilen: {len(reddedilen)}')
    for x in degisen[:600]:
        print('  ', *x)
    for x in kapanan:
        print('   KAPATILDI (listede_birak)', *x)
    for x in reddedilen:
        print('  REDDEDİLDİ', *x)
    if bekleyen:
        print('  BEKLEYEN', ', '.join(bekleyen[:40]) + (' …' if len(bekleyen) > 40 else ''))
    if eski_gorselli:
        print(f'  UYARI: {", ".join(eski_gorselli)}: gorsel.json kaydı daha önce işlenmiş okumanın aynısı; uygulanmadı. Künyeyi yeniden '
              'indirip (`indir_oku --tur kontrol`) okuyun ve kaydı (en azından "not" alanını) güncelleyin')
    if yabanci:
        print(f'  UYARI: gorsel.json\'daki {len(yabanci)} anahtar iş listesinde yok (yazım hatası olabilir): {", ".join(yabanci[:20])}')
    for key in sorted(g):   # kapanmış bir kalem için sonradan girilmiş / değiştirilmiş görsel okuma uygulanmaz: en azından söylenir
        gv = g[key]
        if key not in kalemler and key in by_key and isinstance(gv, dict) and gv.get('tarih') and gv['tarih'] != by_key[key]['tarih']:
            print(f'  UYARI: {key} kapalı; gorsel.json kaydı uygulanmadı (listede {by_key[key]["tarih"]}, kayıtta {gv["tarih"]}). '
                  'Yeniden açmak için anahtarı KONTROL sözlüğüne, kanıt kaydındakinden farklı bir gerekçeyle ekleyin')
    for (s, mk), (t, ta) in sorted(farkli_mukerrerler().items()):
        if fark_once.get((s, mk)) != (t, ta):
            print(f'  DİKKAT: {s} sayısının {mk}. mükerreri ({t}) artık asıl sayıdan ({ta}) farklı tarihte; satırını ve notunu gözden geçirin')
    if a.kuru:
        print('--kuru: hiçbir dosya yazılmadı'); return
    if not degisen and not kapanan:
        # önceki bir çalışma liste yazıldıktan sonra kesildiyse rapor / README / iş listesi eski kalmış olabilir
        if os.path.exists(YAZIM) or (json.load(open(RAPOR, encoding='utf-8')).get('tarih_kaynagi_dagilimi')
                                     != dict(collections.Counter(r['tarih_kaynagi'] for r in rows))):
            print('değişiklik yok, ama önceki çalışma çıktıları yazarken kesilmiş ya da rapor listeyle tutmuyor; çıktılar yeniden yazılıyor')
            yaz_ciktilar(rows, {'tarih': datetime.date.today().isoformat(), 'onarim': True})
        else:
            print('değişiklik yok')
            # rapor yazıldıktan sonra kesilmiş bir çalışma README'yi / iş listesini eski bırakmış olabilir: ikisi de yeniden üretilir
            rr = subprocess.run([sys.executable, os.path.join(HERE, 'render_readme.py'), REPO], capture_output=True, text=True)
            readme_uyarilari(rr)
            yaz_acik(acik_kalemler(rows))
            if rr.returncode:
                raise SystemExit('README.md yeniden üretilemedi: ' + rr.stderr.strip()[-400:])
        return
    dogrula(rows)   # önce bütünlük denetimi: başarısızsa ne liste ne kanıt dosyası yazılır
    # Yinelenen kayıt olmasın: bu çalışmada yeniden değerlendirilen anahtarların eski retleri ve aynı başlangıç durumundan
    # (yarıda kesilmiş bir çalışmada) yazılmış eski kayıtları atılır.
    simdiki = {e['anahtar']: e for e in kanit}
    # ('listede_birak' satırı değiştirmez: kalem sonradan yeniden açılıp işlenirse o kayıt da aynı "önceki"yi taşır ama atılmaz)
    eski = [e for e in eski if not (e['anahtar'] in simdiki and (e.get('sonuc') == 'reddedildi' or
            (e.get('sonuc') != 'listede_birak' and e.get('onceki') == simdiki[e['anahtar']]['onceki'])))]
    with gzip.open(KANIT + '.tmp', 'wt', encoding='utf-8', compresslevel=9) as f:
        for e in eski + kanit:
            f.write(json.dumps(e, ensure_ascii=False) + '\n')
    os.replace(KANIT + '.tmp', KANIT)   # acik_kalemler() kapanan kalemleri buradan okur; liste yazılmadan önce yerinde olmalı
    yaz_ciktilar(rows, {'tarih': datetime.date.today().isoformat(), 'uygulanan': len(degisen), 'kapatilan': len(kapanan),
                        'reddedilen': len(reddedilen), 'bekleyen': len(bekleyen)})


# ----------------------------------------------------------------------------- yeni sayılar (günlük sayfalar)
def ciktilari_onar(rows):
    """`yeni` listeyi değiştirmediğinde çağrılır. Önceki bir çalışma liste (CSV) yazıldıktan sonra kesildiyse JSON / rapor eski ya da
    yarım kalmıştır: bütün çıktılar yeniden yazılır. Rapor güncelse yalnızca README yeniden üretilir (rapordan sonra kesilmiş olabilir)."""
    try:
        eski = (os.path.exists(YAZIM) or json.load(open(RAPOR, encoding='utf-8')).get('toplam_yayin') != len(rows)
                or len(json.load(open(JSONF, encoding='utf-8'))) != len(rows))
    except (OSError, ValueError):
        eski = True
    if eski:
        print('liste ile JSON / rapor tutmuyor (yarıda kesilmiş bir çalışma olabilir); çıktılar yeniden yazılıyor')
        yaz_ciktilar(rows, {'tarih': datetime.date.today().isoformat(), 'onarim': True})
        return
    rr = subprocess.run([sys.executable, os.path.join(HERE, 'render_readme.py'), REPO], capture_output=True, text=True)
    readme_uyarilari(rr)
    if rr.returncode:
        raise SystemExit('README.md yeniden üretilemedi: ' + rr.stderr.strip()[-400:])


def coz(b):
    try:
        return b.decode('utf-8')
    except UnicodeDecodeError:
        return b.decode('cp1254', 'replace')


def gunluk_oku(b, bitisik=False):
    """Günlük sayfa HTML'inden (tarih, sayı, künyedeki mükerrer sırası, yayımlanmadı mı, künye metni) çıkarır.
    İki künye biçimi tanınır; metinde hangisi ÖNCE geçiyorsa o alınır (gövdedeki "… tarihli ve … sayılı Resmî Gazete'de
    yayımlanan" atıfları künyeden sonra gelir):
      A) "17 Kasım 2026 Tarihli ve 33433 Sayılı Resmî Gazete [- (2.) Mükerrer]"            (2007 sonrası sayfalar)
      B) "Kuruluş : 7 Ekim 1920  8 Mart 2003 CUMARTESİ  Sayı : 25042 [Mükerrer]"            (2000–2006 sayfaları)
    `bitisik`: satır içi etiketler boşluk bırakmadan atılır ("<b>2</b><b>8 Mayıs" → "28 Mayıs"); yalnızca
    gunluk_oku_beklenen() üzerinden, olağan okuma beklenen değeri vermediğinde denenir."""
    s = re.sub(r'(?is)<(script|style)[^>]*>.*?</\1>', ' ', coz(b))
    if bitisik:
        s = re.sub(r'(?i)</?(?:b|i|u|em|strong|span|font|a)\b[^>]*>', '', s)
    t = html.unescape(re.sub(r'<[^>]+>', ' ', s))
    t = re.sub(r'\s+', ' ', t)
    f = fold(t)
    yok = 'yayimlanmamaktadir' in f or 'yayimlanmamistir' in f
    gunler = '|'.join(GUN_NO)
    # A biçiminde numaradan sonra "Sayılı" aranmaz: "… Tarihli ve 24170 (Mükerrer) Sayılı …" gibi künyeler de var
    ma = re.search(r'(\d{1,2}) ([a-z]+) (\d{4}) tarihli ve (\d{4,6})(?!\d)', f)
    mb = re.search(r'(\d{1,2}) ([a-z]+) (\d{4}) (?:' + gunler + r') ?-? ?sayi ?: ?(\d{4,6})', f)
    m = min((x for x in (ma, mb) if x), key=lambda x: x.start(), default=None)
    sayi, tarih, kuyruk, kunye = None, None, '', ''
    if m:
        sayi, kuyruk, kunye = int(m.group(4)), f[m.end():m.end() + 60], f[m.start():m.end() + 40]
        if MONTH_MAP.get(m.group(2)):
            try:
                tarih = datetime.date(int(m.group(3)), MONTH_MAP[m.group(2)], int(m.group(1)))
            except ValueError:
                pass
    else:
        m2 = re.search(r'sayi ?: ?(\d{4,6})', f)
        if m2:
            sayi, kuyruk, kunye = int(m2.group(1)), f[m2.end():m2.end() + 60], f[max(0, m2.start() - 60):m2.end() + 40]
    if tarih is None:   # künye başka bir biçimdeyse: metnin başındaki ilk tam tarih (kuruluş tarihi 7 Ekim 1920 hariç)
        for mt in re.finditer(r'(\d{1,2}) ([a-z]+) (\d{4})', f[:1500]):
            if MONTH_MAP.get(mt.group(2)):
                try:
                    d = datetime.date(int(mt.group(3)), MONTH_MAP[mt.group(2)], int(mt.group(1)))
                except ValueError:
                    continue
                if d != datetime.date(1920, 10, 7):
                    tarih = d
                    break
    # Mükerrer sırası yalnızca künyeden (sayı numarasının hemen ardından) okunur; bilgi amaçlıdır, URL'deki sırayla
    # karşılaştırılmaz (ör. 31.12.2002 M3 ve 15.07.2015 M2 sayfalarında yalnızca "Mükerrer" yazar, bazı M sayfalarında ibare hiç yok).
    mk = re.search(r'(?:(\d{1,2})\s*\.\s*)?mukerrer', kuyruk)
    return {'tarih': tarih.isoformat() if tarih else None, 'sayi': sayi, 'mukerrer': int(mk.group(1) or 1) if mk else 0, 'yayimlanmadi': yok,
            'kunye': kunye.strip()}


def gunluk_oku_beklenen(b, tarih, sayi):
    """gunluk_oku; olağan okuma beklenen (tarih, sayı) çiftini vermezse satır içi etiketleri bitiştirerek bir kez daha dener.
    Bugün doğru okunan hiçbir sayfanın sonucu değişmez; beklenen değeri yalnızca sayfada gerçekten yazıyorsa verir."""
    p = gunluk_oku(b)
    if (p['tarih'], p['sayi']) != (tarih, sayi):
        q = gunluk_oku(b, bitisik=True)
        if (q['tarih'], q['sayi']) == (tarih, sayi):
            return q
    return p


def gunluk_url(d, k=0):
    return f'{BASE}eskiler/{d:%Y}/{d:%m}/{d:%Y%m%d}' + (f'M{k}' if k else '') + '.htm'


def gunluk_kanit_oku():
    if not os.path.exists(KANIT_GUNLUK):
        return []
    return [json.loads(l) for l in gzip.open(KANIT_GUNLUK, 'rt', encoding='utf-8')]


def gunluk_kanit_yaz(yeni_kayitlar):
    """`yeni` komutunun siteden okuduklarını kanit/yerel_gunluk.jsonl.gz'ye ekler (kayıtlar silinmez, yenileri sona eklenir)."""
    hepsi = gunluk_kanit_oku() + yeni_kayitlar
    with gzip.open(KANIT_GUNLUK + '.tmp', 'wt', encoding='utf-8', compresslevel=9) as f:
        for e in hepsi:
            f.write(json.dumps(e, ensure_ascii=False) + '\n')
    os.replace(KANIT_GUNLUK + '.tmp', KANIT_GUNLUK)


def mukerrer_sayfalari(d, sayi, bekle, ilk_k=1, listede=0):
    """d gününün M{ilk_k}, M{ilk_k+1} … sayfalarını 404'e kadar okur. (bulunan sıra numaraları, kanıt kayıtları) döner.
    Geçici bir hatada ya da sayfa o günün mükerreri gibi görünmüyorsa hiçbir şey yazılmadan çıkılır."""
    bulunan, kanit, k = [], [], ilk_k
    while True:
        st, b = istek(gunluk_url(d, k)); time.sleep(bekle)
        if st in (404, 410):
            kanit.append({'k': k, 'durum': st})
            return bulunan, kanit
        if st != 200:
            raise SystemExit(f'{gunluk_url(d, k)}: {st} {b[:200]!r} — mükerrer yoklaması tamamlanamadı, hiçbir şey yazılmadı; '
                             'daha sonra yeniden çalıştırın')
        pm = gunluk_oku_beklenen(b, d.isoformat(), sayi)
        if (pm['sayi'] != sayi or pm['tarih'] != d.isoformat()) and k > listede:   # listede zaten olan mükerrer: yalnızca kaydedilir
            raise SystemExit(f'{gunluk_url(d, k)}: sayfa bu günün mükerreri gibi görünmüyor {pm}; elle inceleyin')
        if k > 10:
            raise SystemExit(f'{d}: 10\'dan fazla mükerrer sayfası; elle inceleyin')
        bulunan.append(k); kanit.append({'k': k, 'durum': 200, 'okunan': pm})
        k += 1


def cmd_yeni(a):
    rows = oku_liste()
    kanit_denetle(rows)   # siteye gitmeden ve günlük kanıt dosyasına yazmadan önce
    dogrula(rows)         # liste bozuksa siteye hiç gidilmez
    mains = sorted((int(r['sayi']), r) for r in rows if r['mukerrer'] == '0')
    simdi = lambda: datetime.datetime.now().isoformat(timespec='seconds')
    satir = lambda t, n, k, d: {'tarih': t, 'sayi': str(n), 'mukerrer': str(k), 'url': gunluk_url(d, k)}
    # 1) Öz-sınama: sondan geriye doğru, doğru okunan ilk bilinen güne kadar (en çok 8 gün). Tek bir günün künyesi sitede
    #    hatalı olabilir (yıl eksik, yanlış numara …) ve o gün listeye elle eklenmiş olabilir; ayrıştırıcıyı sınamak için bir
    #    önceki güne bakılır. Yeni eklenen her satır aşağıda zaten beklenen tarih ve numarayla ayrıca denetlenir.
    for n, r in reversed(mains[-8:]):
        st, b = istek(gunluk_url(iso(r['tarih']))); time.sleep(a.bekle)
        if st != 200:
            raise SystemExit(f'öz-sınama {r["tarih"]}: sayfa okunamadı ({st} {b[:120]!r}); hiçbir şey yazılmadı, daha sonra yeniden çalıştırın')
        p = gunluk_oku_beklenen(b, r['tarih'], n)
        ok = p['sayi'] == n and p['tarih'] == r['tarih']
        print(f'öz-sınama {r["tarih"]} sayı {n}: {"tamam" if ok else "UYUŞMUYOR (künye sitede hatalı olabilir; bir önceki güne bakılıyor)"} {p}',
              file=sys.stderr)
        if ok:
            break
    else:
        raise SystemExit('Ayrıştırıcı bilinen son 8 günün hiçbirini doğru okumadı; gunluk_oku() işlevini sayfa yapısına göre düzeltin.')
    son_n, son_r = mains[-1]
    bitis = iso(a.bitis) if a.bitis else datetime.date.today()
    yeni, kanit, bekleyen, yok404, atlanan, gec_gun = [], [], son_n + 1, [], [], {}
    # 2) Listede zaten olan günler: (a) son 10 sayının, eklendikten SONRA yayımlanmış olabilecek mükerrerleri;
    #    (b) ham kaydı kanıt dosyalarında olmayan günler (ilk derlemenin taramasından sonra eklenmiş, kaydı tutulmamış) baştan okunur.
    muk_say = collections.Counter(int(r['sayi']) for r in rows if r['mukerrer'] != '0')
    yol = os.path.join(REPO, 'kanit', 'gunluk_sayfalar.json.gz')
    ilk_son = max(json.load(gzip.open(yol, 'rt', encoding='utf-8'))) if os.path.exists(yol) else '9999-12-31'
    kanitli = {e['tarih'] for e in gunluk_kanit_oku() if e.get('okunan')}
    yayimsiz = {e['tarih'] for e in gunluk_kanit_oku() if (e.get('okunan') or {}).get('yayimlanmadi') and not e['okunan'].get('sayi')}
    kanitsiz = {n for n, r in mains if '/eskiler/' in r['url'] and r['tarih'] > ilk_son and r['tarih'] not in kanitli}
    for n, r in mains:
        if '/eskiler/' not in r['url'] or not (n in kanitsiz or n > son_n - 10):
            continue
        dd = iso(r['tarih'])
        if n in kanitsiz:
            st, b = istek(gunluk_url(dd)); time.sleep(a.bekle)
            if st != 200:
                raise SystemExit(f'{gunluk_url(dd)}: {st} {b[:200]!r} — sayfa okunamadı, hiçbir şey yazılmadı; daha sonra yeniden çalıştırın')
            p = gunluk_oku_beklenen(b, r['tarih'], n)
            tutuyor = p['sayi'] == n and p['tarih'] == r['tarih']
            if not tutuyor:   # satır elle eklenmiş: sayfada ne yazıyorsa kanıt olarak kaydedilir, çalışma durdurulmaz
                print(f'UYARI: {gunluk_url(dd)}: künye listedeki {r["tarih"]} / sayı {n} ile tutmuyor {p}; okunan künye kanıta kaydediliyor', file=sys.stderr)
                # künye tanınan iki biçime uymuyorsa `kunye` boş kalır ya da gövdedeki bir atfı gösterir: sayfada gerçekte ne yazdığı
                # kanıtta görünsün diye sayfa metninin başı da saklanır
                p = dict(p, sayfa_basi=re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', re.sub(r'(?is)<(script|style)[^>]*>.*?</\1>', ' ', coz(b))))).strip()[:400])
            bulunan, mk = mukerrer_sayfalari(dd, n, a.bekle, 1, listede=muk_say[n])
            if len(bulunan) < muk_say[n]:
                raise SystemExit(f'{dd}: listede {muk_say[n]} mükerrer var ama sitede {len(bulunan)} mükerrer sayfası bulundu; elle inceleyin')
            kanit.append({'tarih': r['tarih'], 'url': gunluk_url(dd), 'durum': 200, 'okunan': p, 'listede': {'tarih': r['tarih'], 'sayi': n},
                          'listeyle_tutuyor': tutuyor, 'mukerrer_sayfalari': mk, 'zaman': simdi()})
            gec = [k for k in bulunan if k > muk_say[n]]
        else:
            gec, mk = mukerrer_sayfalari(dd, n, a.bekle, muk_say[n] + 1)
            if gec:
                kanit.append({'tarih': r['tarih'], 'url': gunluk_url(dd), 'gec_mukerrer_sayfalari': mk, 'zaman': simdi()})
        if gec:
            gec_gun[r['tarih']] = gec[-1]   # o günün sitedeki mükerrer sayfası adedi (M1 … M{k} kesintisiz)
        for k in gec:
            yeni.append(satir(r['tarih'], n, k, dd))
            print(f'{dd}: sayı {n} için sonradan yayımlanmış {k}. mükerrer', file=sys.stderr)
    # 3) Yeni günler
    d = iso(son_r['tarih']) + datetime.timedelta(days=1)
    while d <= bitis:
        st, b = istek(gunluk_url(d)); time.sleep(a.bekle)
        if st in (404, 410):
            print(f'{d} ana sayfa: {st} (sayı yok ya da henüz yayımlanmadı)', file=sys.stderr)
            if d < datetime.date.today():   # 27.06.2000'den beri geçmiş her günün sayfası sitede var (gazetenin yayımlanmadığı günlerin de)
                yok404.append(d.isoformat()); atlanan.append({'tarih': d.isoformat(), 'url': gunluk_url(d), 'durum': st, 'zaman': simdi()})
            d += datetime.timedelta(days=1); continue
        if st != 200:
            raise SystemExit(f'{gunluk_url(d)}: {st} {b[:200]!r} — günün ana sayfası okunamadı, hiçbir şey yazılmadı; '
                             'daha sonra yeniden çalıştırın')
        p = gunluk_oku_beklenen(b, d.isoformat(), bekleyen)
        if p['yayimlanmadi'] and not p['sayi']:
            print(f'{d}: Resmî Gazete yayımlanmamış', file=sys.stderr)
            # README "her günün M sayfaları kontrol edildi" der: gazetenin yayımlanmadığı günün M sayfaları da yoklanır (bugüne dek hiç çıkmadı)
            listede = sum(1 for r in rows if r['mukerrer'] != '0' and r['tarih'] == d.isoformat() and '/eskiler/' in r['url'])
            bulunan, mk = mukerrer_sayfalari(d, None, a.bekle, 1, listede=listede)
            if len(bulunan) != listede:
                raise SystemExit(f'{d}: gazetenin yayımlanmadığı günde sitede {len(bulunan)} mükerrer sayfası var, listede {listede}; '
                                 f'hiçbir şey yazılmadı, elle inceleyin: {gunluk_url(d, 1)}')
            if d.isoformat() not in yayimsiz:   # sonraki sayı listeye girene dek her çalıştırmada yeniden okunur; kanıta bir kez yazılır
                kanit.append({'tarih': d.isoformat(), 'url': gunluk_url(d), 'durum': 200, 'okunan': p, 'mukerrer_sayfalari': mk, 'zaman': simdi()})
            d += datetime.timedelta(days=1); continue
        if p['tarih'] != d.isoformat() or p['sayi'] != bekleyen:
            raise SystemExit(f'{d}: beklenmeyen künye {p} (beklenen sayı {bekleyen}); elle inceleyin: {gunluk_url(d)}')
        bulunan, mk = mukerrer_sayfalari(d, p['sayi'], a.bekle, 1)
        yeni += [satir(d.isoformat(), p['sayi'], k, d) for k in [0] + bulunan]
        kanit += atlanan; atlanan = []   # sayfası olmayan geçmiş günler: sonraki sayı listeye girerken bir kez kaydedilir
        kanit.append({'tarih': d.isoformat(), 'url': gunluk_url(d), 'durum': 200, 'okunan': p, 'mukerrer_sayfalari': mk, 'zaman': simdi()})
        print(f'{d}: sayı {p["sayi"]}, {len(bulunan)} mükerrer', file=sys.stderr)
        bekleyen += 1
        d += datetime.timedelta(days=1)
    for y in yeni:
        y.update(gun='', sira='', yayin_adi='T.C. Resmî Gazete', tarih_kaynagi=ETIKET['eskiler'], **{'not': ''})
    print(f'{len(yeni)} yeni satır ({sum(1 for y in yeni if y["mukerrer"] == "0")} asıl) · {len(kanit)} gün için kanıt kaydı')

    def gecmis_404():   # yazma bittikten sonra: "yeni sayı yok" / çıkış kodu 0, sayfası bulunamayan geçmiş günleri gizlemesin
        if yok404:
            raise SystemExit(f'UYARI: geçmiş {len(yok404)} günün ana sayfası sitede yok (404): {yok404[0]} … {yok404[-1]}. 27.06.2000\'den beri her '
                             'günün sayfası vardı (gazetenin yayımlanmadığı günlerin de); sayfa henüz konmamış, kaldırılmış ya da adres düzeni '
                             'değişmiş olabilir. Okunabilen günler yukarıdaki gibi işlendi; bu günleri elle inceleyin.')
    if a.kuru or not (yeni or kanit):
        if not yeni:
            print('yeni sayı yok')
        if not a.kuru:
            ciktilari_onar(rows)
        return gecmis_404()
    dogrula(rows + yeni)          # kanıt yazıldıktan sonra durduracak bir denetim kalmasın
    if gec_gun:
        tarama_tohumla()          # depodaki ham yoklama sonucu okunamıyorsa kanıt yazılmadan önce durur
    if kanit:
        gunluk_kanit_yaz(kanit)   # kanıt listeden önce yazılır
    # Günlük yoklama dosyası bu günleri eski (mükerrer yayımlanmadan önceki) adetle tutuyorsa güncel adet sona eklenir; dosyada son
    # satır geçerlidir. Yoksa `yoklama_ozeti` eski yoklamayı yeni listeyle karşılaştırıp olmayan bir uyuşmazlık bildirir ve
    # `mukerrer_tara` dosyada kaydı olan günü yeniden yoklamaz.
    eski = tarama_oku(TARAMA_GUNLUK)
    ek = ''.join(f'{g},{k}\n' for g, k in gec_gun.items() if g in eski and eski[g] != k)
    ozet_eskidi = any(g in eski for g in gec_gun)   # yoklamanın kapsadığı bir güne mükerrer eklendi: özetin liste tarafı da eskidi
    if ek:
        yarim = open(TARAMA_GUNLUK, 'rb').read()[-1:] != b'\n'
        with open(TARAMA_GUNLUK, 'a', encoding='utf-8') as f:
            f.write(('\n' if yarim else '') + ek)
        print(f'{TARAMA_GUNLUK}: {ek.count(chr(10))} günün mükerrer adedi güncellendi')
    if yeni:
        yaz_ciktilar(rows + yeni, {'tarih': datetime.date.today().isoformat(), 'yeni_satir': len(yeni), 'son': max(y['tarih'] for y in yeni)})
    else:
        print('yeni sayı yok (yalnızca kanıt kayıtları yazıldı)')
        ciktilari_onar(rows)
    if ozet_eskidi:
        # Güncel adet yalnızca git'e girmeyen yerel/ dosyasında kalmasın: depodaki ham sonuç (kanit/) ve rapordaki özet de yenilenir.
        # Yoksa bu durumdan alınan yeni bir klonda `yoklama_ozeti` eski adeti yeni listeyle karşılaştırıp uyuşmazlık bildirir.
        # Yoklama dosyası güncel adeti zaten tutuyorsa da (gün, mükerreri yayımlandıktan sonra ama listeye girmeden önce yoklanmış)
        # özet yenilenir: rapordaki ve README'deki uyuşmazlık, mükerrer listeye girince ortadan kalkmıştır.
        try:
            cmd_yoklama_ozeti()
        except SystemExit as e:
            print(f'UYARI: yoklama özeti yenilenemedi ({e}); yoklama dosyalarını tamamlayıp `yoklama_ozeti` çalıştırın')
    gecmis_404()


# ----------------------------------------------------------------------------- yoklama raporları (listeyi değiştirmez)
def tarama_oku(out):
    """Yoklama dosyasını okur (anahtar → sitedeki mükerrer adedi); dosyaya DOKUNMAZ (çalışan bir yoklama aynı dosyaya ekliyor
    olabilir). 'hata' satırları, yarım kalmış satırlar ve eski biçimin üçüncü kolonu (o andaki liste adedi) yok sayılır;
    okunamayan anahtarlar bir sonraki çalıştırmada yeniden yoklanır."""
    kayit = {}
    if os.path.exists(out):
        for l in open(out, encoding='utf-8'):
            p = l.strip().split(',')
            if len(p) >= 2 and p[1].isdigit():
                kayit[p[0]] = int(p[1])
    return kayit


def tarama_tohumla():
    """yerel/ altında yoklama dosyası yoksa (başka bir bilgisayar, yeni klon, silinmiş yerel/) onu depodaki ham sonuçtan
    (kanit/yerel_mukerrer_yoklama.json.gz) yeniden kurar; var olan dosyaya dokunmaz. Dosyanın zamanı yoklamanın yapıldığı güne
    çekilir: özetin tarihi dosya zamanından okunur."""
    if not os.path.exists(KANIT_YOKLAMA):
        return
    try:
        with gzip.open(KANIT_YOKLAMA, 'rt', encoding='utf-8') as f:
            ham = json.load(f)
        t = time.mktime(iso(ham['tarih']).timetuple())
    except Exception as e:   # yarım / bozuk dosya, eksik 'tarih'
        raise SystemExit(f'kanit/yerel_mukerrer_yoklama.json.gz okunamadı ({type(e).__name__}: {e}); dosyayı geri getirin '
                         '(ör. git checkout -- kanit/yerel_mukerrer_yoklama.json.gz). Hiçbir dosya yazılmadı.')
    os.makedirs(YEREL, exist_ok=True)
    for ad, yol in (('gunluk', TARAMA_GUNLUK), ('arsiv', TARAMA_ARSIV)):
        if ad in ham and not os.path.exists(yol):
            with yaz(yol) as f:
                f.writelines(f'{k},{v}\n' for k, v in ham[ad].items())
            os.utime(yol, (t, t))
            print(f'{yol}: yoktu; depodaki ham yoklama sonucundan ({ham["tarih"]}, {len(ham[ad])} kayıt) yeniden kuruldu', file=sys.stderr)


def tarama_yap(out, anahtarlar, url_of, liste_say, bekle, baslik, yeniden=False):
    """Her anahtar için k = 1, 2, … adreslerini yoklar; sitedeki adedi dosyaya ekler. Liste adedi dosyaya yazılmaz,
    rapor her çalıştırmada GÜNCEL listeyle karşılaştırılarak üretilir. Geçici hatalar dosyaya yazılmaz (yeniden yoklanır).
    (kayıtlar, tamam mı) döner; hata kaldıysa ya da yoklama yarıda durduysa tamam değildir.
    Kaydı listeyle tutan anahtar yeniden sorulmaz; `yeniden` verilirse istenen bütün anahtarlar baştan sorulur (kaldığı yerden devam etmez)."""
    tarama_tohumla()
    kayit, hatalar, ust_uste, sorulan = tarama_oku(out), {}, 0, 0
    istenen = set(anahtarlar)
    yarim = os.path.exists(out) and os.path.getsize(out) > 0 and open(out, 'rb').read()[-1:] != b'\n'
    with open(out, 'a', encoding='utf-8') as f:
        if yarim:   # yarıda kesilmiş son satıra yeni kayıt yapışmasın
            f.write('\n'); f.flush()
        for key in anahtarlar:
            if not yeniden and key in kayit and kayit[key] == liste_say(key):   # listeyle tutmayan kayıt yeniden yoklanır (ör. sonradan yayımlanmış mükerrer)
                continue
            k = 0; sorulan += 1
            while True:
                st, b = istek(url_of(key, k + 1), aralik='bytes=0-1023', ilk=1024, zaman=60); time.sleep(bekle)
                if st not in (200, 206):
                    break
                k += 1
                if k >= 10:
                    st, b = None, b'en az 10 mukerrer; elle inceleyin'; break
            if st in (404, 410):
                kayit[key] = k; f.write(f'{key},{k}\n'); f.flush(); ust_uste = 0
            else:
                hatalar[key] = f'{st} ' + (b or b'').decode('utf-8', 'replace')[:80]; ust_uste += 1
                if ust_uste >= 5:
                    print(f'art arda 5 hata (son: {key} {hatalar[key]}); yoklama durduruldu, daha sonra yeniden çalıştırın', file=sys.stderr)
                    break
    eksik = [k for k in anahtarlar if k not in kayit and k not in hatalar]
    fark = [f'{k},{v},{liste_say(k)}' for k, v in kayit.items() if k in istenen and v != liste_say(k)] + [f'{k},hata,{h}' for k, h in hatalar.items()]
    print(f'{out}: {baslik} · yoklanan {sum(1 for k in anahtarlar if k in kayit)}/{len(anahtarlar)} · uyuşmayan/hatalı {len(fark)}'
          + (f' · henüz yoklanmayan {len(eksik)}' if eksik else '')
          + f' · bu çalıştırmada siteye sorulan {sorulan} (kaydı listeyle tutanlar yeniden sorulmaz; hepsini yeniden sormak için --yeniden)')
    for l in fark[:200]:
        print('  ', l)
    return kayit, not (hatalar or eksik)


def cmd_mukerrer_tara(a):
    rows = oku_liste()
    liste = collections.Counter(r['tarih'] for r in rows if r['mukerrer'] != '0' and '/eskiler/' in r['url'])
    os.makedirs(YEREL, exist_ok=True)
    d, son, gunler = iso(a.bas), iso(a.son), []
    if d > son or son >= datetime.date.today():
        raise SystemExit('--bas <= --son < bugün olmalı: bugünün ve gelecek günlerin mükerreri henüz yayımlanmamış olabilir, '
                         'dosyaya yazılan "0" kaydı ise yeniden yoklanmaz (son günler için `yeni` komutu)')
    while d <= son:
        gunler.append(d.isoformat()); d += datetime.timedelta(days=1)
    kayit, tamam = tarama_yap(TARAMA_GUNLUK, gunler, lambda g, k: gunluk_url(iso(g), k), lambda g: liste.get(g, 0),
                              a.bekle, 'tarih,sitedeki_mukerrer,listedeki_mukerrer', yeniden=a.yeniden)
    # Ek denetim (istek atmaz): ilk taramada günün ana sayfasında, standart adreste bulunamayan bir mükerrer bağlantısı kaydedilmiş mi?
    yol = os.path.join(REPO, 'kanit', 'gunluk_sayfalar.json.gz')
    if os.path.exists(yol):
        gs = json.load(gzip.open(yol, 'rt', encoding='utf-8'))
        for g in gunler:
            bag = [int(x) for x in re.findall(g.replace('-', '') + r'[Mm](\d+)', str((gs.get(g) or {}).get('mukerrer_line') or ''))]
            if bag and g in kayit and max(bag) > kayit[g]:
                print(f'   {g}: ana sayfada {max(bag)}. mükerrer bağlantısı kayıtlı ama sitede {kayit[g]} mükerrer sayfası var; elle inceleyin '
                      '(12.06.2010 için bkz. EKSIKLER.md)')
    if not tamam:
        sys.exit(1)   # hata kaldı ya da yoklama yarıda durdu: yeniden çalıştırın


def cmd_arsiv_mukerrer_tara(a):
    rows = oku_liste()
    # liste tarafı tarihe göre değil sayı numarasına göre: 24093 ve 24095'in mükerrerleri 27.06.2000'den sonra (günlük sayfadan) tarihli
    liste = collections.Counter(int(r['sayi']) for r in rows if r['mukerrer'] != '0' and int(r['sayi']) <= 24095)
    if not 1 <= a.bas <= a.son <= 24095:   # 24095'ten sonrası günlük sayfalardan gelir; arşivde yalnızca tek tük mükerrer PDF'i var (24273_1, 24281_1)
        raise SystemExit('1 <= --bas <= --son <= 24095 olmalı (liste tarafı yalnızca 24095\'e kadar sayılır)')
    os.makedirs(YEREL, exist_ok=True)
    kayit, tamam = tarama_yap(TARAMA_ARSIV, [str(n) for n in range(a.bas, a.son + 1)],
                              lambda n, k: f'{BASE}arsiv/{n}_{k}.pdf', lambda n: liste.get(int(n), 0), a.bekle, 'sayi,arsivdeki_mukerrer,listedeki_mukerrer', yeniden=a.yeniden)
    if not tamam:
        sys.exit(1)


def yoklama_ozeti():
    """yerel/ altındaki yoklama dosyalarını (varsa) GÜNCEL listeyle karşılaştırır; ağa çıkmaz, var olan yoklama dosyalarına dokunmaz
    (dosya yoksa depodaki ham sonuçtan kurulur: tarama_tohumla)."""
    rows = oku_liste()
    gl = collections.Counter(r['tarih'] for r in rows if r['mukerrer'] != '0' and '/eskiler/' in r['url'])
    al = collections.Counter(int(r['sayi']) for r in rows if r['mukerrer'] != '0' and int(r['sayi']) <= 24095)
    oz = {'tarih': datetime.date.today().isoformat()}
    tarama_tohumla()
    g = tarama_oku(TARAMA_GUNLUK)
    if g:
        ks = sorted(g)
        oz['gunluk'] = {'bas': ks[0], 'son': ks[-1], 'yoklanan_gun': len(ks), 'kesintisiz': len(ks) == (iso(ks[-1]) - iso(ks[0])).days + 1,
                        'sitede_mukerrer': sum(g.values()), 'listede_mukerrer': sum(gl.get(k, 0) for k in ks),
                        'uyusmayan': [[k, g[k], gl.get(k, 0)] for k in ks if g[k] != gl.get(k, 0)]}
    a = {int(k): v for k, v in tarama_oku(TARAMA_ARSIV).items() if k.isdigit()}
    if a:
        ns = sorted(a)
        oz['arsiv'] = {'bas': ns[0], 'son': ns[-1], 'yoklanan_sayi': len(ns), 'kesintisiz': len(ns) == ns[-1] - ns[0] + 1,
                       'arsivde_mukerrer': sum(a.values()), 'listede_mukerrer': sum(al.get(n, 0) for n in ns if n <= 24095),
                       'uyusmayan': [[n, a[n], al.get(n, 0)] for n in ns if a[n] != al.get(n, 0)]}
    return oz, {'gunluk': g, 'arsiv': a}


def cmd_yoklama_ozeti(a=None):
    """Yoklama sonuçlarını data/dogrulama_raporu.json'a ('mukerrer_yoklama') ve README'ye işler."""
    oz, ham = yoklama_ozeti()
    for ad in ('gunluk', 'arsiv'):
        if ad in oz:
            print(ad, {k: v for k, v in oz[ad].items() if k != 'uyusmayan'}, '· uyuşmayan:', oz[ad]['uyusmayan'])
    if len(oz) == 1:
        print('yerel/ altında yoklama dosyası yok; rapor değiştirilmedi'); return
    for ad in [ad for ad in ('gunluk', 'arsiv') if ad in oz and not oz[ad]['kesintisiz']]:
        print(f'UYARI: {ad} yoklama dosyasında boşluk var (yoklama bitmemiş ya da hatalar kalmış); özete alınmadı. '
              'Aynı yoklama komutunu yeniden çalıştırıp eksikleri tamamlayın.')
        del oz[ad]
    if len(oz) == 1:
        raise SystemExit('tamamlanmış yoklama yok; rapor ve README değiştirilmedi')
    # özetin tarihi ham sonucun en son değiştiği yoklamanın günüdür (yoklama dosyalarına son yazılış), özetin yazıldığı gün değil;
    # aynı adetleri bulan sonraki bir yoklama (ör. --yeniden) tarihi ilerletmez (aşağıda)
    oz['tarih'] = max(datetime.date.fromtimestamp(os.path.getmtime(p)) for ad, p in (('gunluk', TARAMA_GUNLUK), ('arsiv', TARAMA_ARSIV)) if ad in oz).isoformat()
    # Dosya zamanı kopyalama / yedekten dönme ile de değişir: ham sonuç depodakiyle birebir aynıysa depodaki tarih korunur ve
    # kanıt dosyası yeniden yazılmaz (sıkıştırılmış baytlar zlib sürümüne göre değişebilir).
    yeni_ham = {ad: {str(k): v for k, v in ham[ad].items()} for ad in ('gunluk', 'arsiv') if ad in oz}
    depo = None
    if os.path.exists(KANIT_YOKLAMA):
        try:
            with gzip.open(KANIT_YOKLAMA, 'rt', encoding='utf-8') as f:
                depo = json.load(f)
        except Exception:
            depo = None
    ham_ayni = isinstance(depo, dict) and depo.get('tarih') and {k: v for k, v in depo.items() if k != 'tarih'} == yeni_ham
    if ham_ayni:
        oz['tarih'] = depo['tarih']
    rap = json.load(open(RAPOR, encoding='utf-8'))
    eski = rap.get('mukerrer_yoklama') or {}
    for ad in ('gunluk', 'arsiv'):   # rapordaki özet, yerel/ altında eksik kalmış ya da hiç olmayan bir dosya yüzünden daralmasın / silinmesin
        if ad in eski and (ad not in oz or oz[ad]['bas'] > eski[ad]['bas'] or oz[ad]['son'] < eski[ad]['son']):
            raise SystemExit(f'rapordaki {ad} özeti ({eski[ad]["bas"]}–{eski[ad]["son"]}) yerel/ altındaki yoklama dosyasının kapsadığından geniş '
                             '(dosya yok, yarım ya da başka bir aralık için); özet silinmesin diye hiçbir şey yazılmadı')
    rap['mukerrer_yoklama'] = oz
    # Ham sonuçlar özetle birlikte depoya yazılır (yerel/ git'e girmez). mtime=0: aynı içerik aynı baytları verir.
    if not ham_ayni:
        with open(KANIT_YOKLAMA + '.tmp', 'wb') as fb, gzip.GzipFile(filename='', fileobj=fb, mode='wb', compresslevel=9, mtime=0) as f:
            f.write(json.dumps({'tarih': oz['tarih'], **{ad: ham[ad] for ad in ('gunluk', 'arsiv') if ad in oz}}, ensure_ascii=False, sort_keys=True).encode('utf-8'))
        os.replace(KANIT_YOKLAMA + '.tmp', KANIT_YOKLAMA)
    with yaz(RAPOR) as f:
        json.dump(rap, f, ensure_ascii=False, indent=1)
    rr = subprocess.run([sys.executable, os.path.join(HERE, 'render_readme.py'), REPO], capture_output=True, text=True)
    print('README:', (readme_uyarilari(rr) or rr.stderr).strip()[:300])
    if rr.returncode:
        raise SystemExit('README.md yeniden üretilemedi: ' + rr.stderr.strip()[-400:])


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
    print('PDF araçları:', araclar or 'YOK (yalnızca arşiv PDF\'i okumak / indir_oku için gerekir: poppler kurun ya da `pip install pymupdf`)')
    print('TAMAM' if ok else 'SORUN VAR')
    sys.exit(0 if ok else 1)


def tarih_arg(s):
    try:
        return iso(s).isoformat()
    except ValueError:
        raise argparse.ArgumentTypeError(f'{s!r} geçerli bir tarih değil (YYYY-AA-GG olmalı)')


def main():
    for akis in (sys.stdout, sys.stderr):
        try:
            akis.reconfigure(errors='replace')
        except Exception:
            pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest='cmd', required=True)
    sp.add_parser('baglanti')
    sp.add_parser('liste')
    p = sp.add_parser('indir_oku'); p.add_argument('--tur', default='tahmin,atif,buyuk_mukerrer,kontrol'); p.add_argument('--bekle', type=float, default=1.5)
    p.add_argument('--sakla', action='store_true', help='PDF\'leri yerel/pdf/ içinde tut'); p.add_argument('--sinir', type=int, default=0)
    sp.add_parser('durum')
    sp.add_parser('yeniden_karar')
    sp.add_parser('yoklama_ozeti')
    sp.add_parser('yeniden_yaz')
    p = sp.add_parser('uygula'); p.add_argument('--kuru', action='store_true')
    p = sp.add_parser('yeni'); p.add_argument('--bitis', type=tarih_arg); p.add_argument('--bekle', type=float, default=1.0); p.add_argument('--kuru', action='store_true')
    p = sp.add_parser('mukerrer_tara'); p.add_argument('--bas', required=True, type=tarih_arg); p.add_argument('--son', required=True, type=tarih_arg); p.add_argument('--bekle', type=float, default=1.0)
    p.add_argument('--yeniden', action='store_true', help='kaydı listeyle tutan günleri de yeniden yokla')
    p = sp.add_parser('arsiv_mukerrer_tara'); p.add_argument('--bas', type=int, required=True); p.add_argument('--son', type=int, required=True); p.add_argument('--bekle', type=float, default=1.0)
    p.add_argument('--yeniden', action='store_true', help='kaydı listeyle tutan sayıları da yeniden yokla')
    a = ap.parse_args()
    if a.cmd == 'liste':
        yaz_acik(acik_kalemler(oku_liste()))
    elif a.cmd == 'yeniden_yaz':
        yaz_ciktilar(oku_liste(), {'tarih': datetime.date.today().isoformat(), 'elle_duzeltme': True})
    else:
        {'baglanti': cmd_baglanti, 'indir_oku': cmd_indir_oku, 'durum': cmd_durum, 'yeniden_karar': cmd_yeniden_karar, 'uygula': cmd_uygula, 'yeni': cmd_yeni,
         'mukerrer_tara': cmd_mukerrer_tara, 'arsiv_mukerrer_tara': cmd_arsiv_mukerrer_tara, 'yoklama_ozeti': cmd_yoklama_ozeti}[a.cmd](a)


if __name__ == '__main__':
    main()
