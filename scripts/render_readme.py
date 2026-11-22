"""README.md'yi scripts/README.template.md, data/dogrulama_raporu.json, listeden (künye açıklamalarının adetleri ve etiketleri
için) ve kanit/ altındaki atıf dosyalarından (scripts/atif_dogrula.py ile; atıf karşılaştırmasının ayrıntıları için) üretir.
kullanım: render_readme.py <depo>
Eski iki argümanlı biçim (render_readme.py <scratchpad> <depo>) yalnızca ilk derlemenin çalışma dizininde çalışır: şablonu
<scratchpad>/tools/README.template.md'den, raporda atif_dogrulama yoksa sayıları <scratchpad>/data/validation_stats.json'dan
okur; ikisi de depoda yoktur."""
import json, datetime, sys, re, os
if len(sys.argv) > 2:
    SCR, REPO = sys.argv[1], sys.argv[2]; TPL = f'{SCR}/tools/README.template.md'
else:
    REPO = sys.argv[1]; SCR = None; TPL = os.path.join(REPO, 'scripts', 'README.template.md')
s = json.load(open(f'{REPO}/data/dogrulama_raporu.json', encoding='utf-8'))
tpl = open(TPL, encoding='utf-8').read()
TR_AY = ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık']
def trdate(iso):
    d = datetime.date.fromisoformat(iso); return f'{d.day} {TR_AY[d.month - 1]} {d.year}'
son_iso, son_sayi = s['son'].split(' / Sayı ')
expl = {
    'resmî site günlük sayfası': 'resmigazete.gov.tr günlük sayfası (`eskiler/…htm`), 27.06.2000 sonrası',
    'arşiv PDF künyesi (OCR + haftanın günü kontrolü)': "Arşiv PDF'inin künyesi; OCR + haftanın günü + sıra kontrolü",
    'arşiv PDF künyesi (görsel okuma)': "Arşiv PDF'inin künyesi görüntü olarak okundu",
    'asıl sayının tarihi': 'Mükerrer nüsha; asıl sayıyla aynı gün (kendi künyesi de okundu, tarih aynı çıktı)',
    'aynı sayının mükerrer nüshasının künyesi': "Asıl sayının PDF'i okunamadı; aynı numaralı mükerrerin künyesinden",
    'komşu sayılardan kesin çıkarım': 'Künyedeki gün adı (varsa gün rakamı) ile önceki ve sonraki sayılardan tek bir tarih mümkün',
    'komşu sayılardan tahmin (kesin değil)': 'PDF indirilemedi/okunamadı; olası aralık `not` kolonunda',
    'TBMM kanun/karar kaydı (Resmî Gazete tarih ve sayısı)': "Künyeden tarih okunamadı (293'ün künyesinde gün rakamı basılı değil); TBMM kaydındaki yayım tarihi ve sayısından",
    'Resmî Gazete metinlerindeki tarih–sayı atfı': "Künye okunamadı; sonraki Resmî Gazete metinlerindeki atıftan",
    'künyedeki haftanın günü + komşu sayılar (künyedeki gün rakamı hatalı/kırık)': 'Künyedeki gün rakamı baskı hatası/kırık; künyedeki haftanın günü ve komşu sayılardan (gerekçe `not` kolonunda)',
}
f = lambda x: f'{x:,}'.replace(',', '.')
# data/resmi_gazete_sayilari.json'daki kısa kodlar (scripts/merge.py TAG / scripts/yerel_tamamla.py ETIKET ile aynı eşleme)
kod = {'künyedeki haftanın günü + komşu sayılar (künyedeki gün rakamı hatalı/kırık)': 'kunye_duzeltme', 'Resmî Gazete metinlerindeki tarih–sayı atfı': 'rg_atif',
       'TBMM kanun/karar kaydı (Resmî Gazete tarih ve sayısı)': 'tbmm', 'başka resmî metinlerde geçen tarih–sayı atfı': 'web_atif',
       'aynı sayının mükerrer nüshasının künyesi': 'muk_kunye', 'resmî site günlük sayfası': 'eskiler',
       'arşiv PDF künyesi (OCR + haftanın günü kontrolü)': 'arsiv_ocr', 'arşiv PDF künyesi (görsel okuma)': 'visual',
       'komşu sayılardan kesin çıkarım': 'arsiv_infer', 'asıl sayının tarihi': 'arsiv_muk', 'Lexpera günlük listesi': 'lexpera',
       'komşu sayılardan tahmin (kesin değil)': 'tahmin'}
rows = '\n'.join(f'| {k} | `{kod.get(k, "")}` | {f(v)} | {expl.get(k, "")} |' for k, v in sorted(s['tarih_kaynagi_dagilimi'].items(), key=lambda x: -x[1]))
tah = s['tahmini_tarihli_sayilar']
two = sum(1 for n, d, r in tah if r and (datetime.date.fromisoformat(r[1]) - datetime.date.fromisoformat(r[0])).days == 2)
gun = (datetime.date.fromisoformat(son_iso) - datetime.date(2000, 6, 27)).days + 1
gorsel = s['tarih_kaynagi_dagilimi'].get('arşiv PDF künyesi (görsel okuma)', 0)
rep = {'{SON}': trdate(son_iso), '{SON_SAYI}': son_sayi, '{TOPLAM}': f(s['toplam_yayin']), '{ASIL}': f(s['asil_sayi']), '{MUK}': f(s['mukerrer']),
       '{OLUSTURMA}': trdate(s['olusturma_tarihi']), '{GORSEL}': f(gorsel), '{GUN_SAYISI}': f(gun), '{KAYNAK_TABLO}': rows,
       '{TAHMIN}': f(len(tah)), '{TAHMIN_2GUN}': f(two)}
# Mükerrer yoklamalarının özeti (scripts/yerel_tamamla.py yoklama_ozeti → data/dogrulama_raporu.json: mukerrer_yoklama)
my = s.get('mukerrer_yoklama') or {}
parca, fark = [], 0
if my.get('arsiv'):
    a = my['arsiv']; fark += len(a['uyusmayan'])
    parca.append(f"arşivdeki `N_1.pdf`, `N_2.pdf` … adresleri {a['bas']}–{a['son']} arasındaki {f(a['yoklanan_sayi'])} sayı numarası için")
if my.get('gunluk'):
    g = my['gunluk']; fark += len(g['uyusmayan'])
    parca.append(f"{trdate(g['bas'])} – {trdate(g['son'])} arasındaki {f(g['yoklanan_gun'])} günün `M1`, `M2` … mükerrer sayfaları")
rep['{MUKERRER_YOKLAMA}'] = ''
if parca:
    sonuc = ('bulunan mükerrer adedi her yerde listeyle aynı çıktı' if not fark
             else f"{fark} gün ya da sayıda sitedeki adet listedekinden farklı (hangileri olduğu `data/dogrulama_raporu.json` içinde: `mukerrer_yoklama` → `uyusmayan`)")
    rep['{MUKERRER_YOKLAMA}'] = (f"{trdate(my['tarih'])} itibarıyla " + ', ayrıca '.join(parca) + f' siteden doğrudan yeniden yoklandı; {sonuc}.')
# Künyesinde yıl sorunlu sayılar: listenin `not` kolonundaki açıklamalardan sayılır (bu adetler ile {YIL_KIRIK_LISTE} ve
# {YIL_NOT_LISTE} elle yazılmaz; şablondaki yanlış basılmış ve basılı olmayan yılların numaraları, yıl ayrıntıları ve
# künye kusurlarının tek tek anlatımı ise elle yazılıdır)
import csv, collections, bisect, gzip
yil = {'yanlis': [], 'yok': [], 'kirik': []}
yil_anahtar = set()
with open(f'{REPO}/data/resmi_gazete_sayilari.csv', encoding='utf-8', newline='') as fh:
    liste = list(csv.DictReader(fh))
for r in liste:
    n = r['not'] or ''
    if 'künyede yıl yanlış basılmış' in n: tur = 'yanlis'
    elif 'künyede yıl basılı değil' in n: tur = 'yok'
    elif 'künyede yıl «' in n or 'künyede yılın ' in n: tur = 'kirik'
    else: continue
    yil[tur].append(int(r['sayi'])); yil_anahtar.add((r['sayi'], r['mukerrer']))
def aralikli(ns):
    """[8099, 8100, 8101, 8103] → '8099–8101, 8103' (art arda üç ve daha çok numara aralık olarak yazılır)"""
    ns, out, i = sorted(ns), [], 0
    while i < len(ns):
        j = i
        while j + 1 < len(ns) and ns[j + 1] == ns[j] + 1: j += 1
        out += [f'{ns[i]}–{ns[j]}'] if j - i >= 2 else [str(x) for x in ns[i:j + 1]]
        i = j + 1
    return ', '.join(out)
yil_hepsi = yil['yanlis'] + yil['yok'] + yil['kirik']
uyarilar = []
def ve_ile(ogeler):
    return ogeler[0] if len(ogeler) == 1 else ', '.join(ogeler[:-1]) + ' ve ' + ogeler[-1]
# Künyesinde gün ya da ay eksik, kırık ya da yanlış basılmış yayınlar: (sayı, mükerrer) → README'deki adı. ELLE TUTULUR: bu
# satırların `not` açıklamaları onları güvenilir biçimde ayırt eden ortak bir ibare taşımıyor. Böyle bir açıklama eklenir ya da
# kaldırılırsa burayı ve şablondaki anlatımı («Resmî kaynaktaki tutarsızlıklar») birlikte güncelleyin. Aşağıdaki kaba denetim
# (yıl açıklaması olmayıp `not`unda «gün rakam», «gün sayısı yok» ya da «ay adı» geçen satırlar) bu listeyle tutmazsa uyarır.
GUN_AY = [(('244', '0'), '244'), (('293', '0'), '293'), (('588', '1'), "588'in mükerreri"), (('1054', '0'), '1054'),
          (('1056', '0'), '1056'), (('8489', '0'), '8489'), (('10480', '0'), '10480'), (('14490', '0'), '14490'),
          (('15890', '0'), '15890'), (('16168', '0'), '16168')]
satir = {(r['sayi'], r['mukerrer']): r for r in liste}
gun_ay = {k for k, _ in GUN_AY}
kaba = {k for k, r in satir.items() if k not in yil_anahtar and any(x in (r['not'] or '') for x in ('gün rakam', 'gün sayısı yok', 'ay adı'))}
if kaba != gun_ay:
    uyarilar.append(f'render_readme.py GUN_AY, listenin `not` açıklamalarıyla tutmuyor: listede fazladan {sorted(kaba - gun_ay)}, '
                    f'açıklaması bulunamayan {sorted(gun_ay - kaba)}')
rep.update({'{YIL_YANLIS_N}': f(len(yil['yanlis'])), '{YIL_YOK_N}': f(len(yil['yok'])), '{YIL_KIRIK_N}': f(len(yil['kirik'])),
            '{YIL_NOT_N}': f(len(yil_hepsi)), '{YIL_KIRIK_LISTE}': aralikli(yil['kirik']), '{YIL_NOT_LISTE}': aralikli(yil_hepsi),
            '{GUN_AY_LISTE}': ', '.join(ad for _, ad in GUN_AY), '{KUNYE_NOT_N}': f(len(GUN_AY) + len(yil_hepsi))})
# Bu yayınların `tarih_kaynagi`: eksik ya da kusurlu kısım komşu sayılardan tamamlansa da tarihin geri kalanı ve gün adı
# künyeden okunduysa satır künye okumasının etiketini taşır; ayrı etiketli olanlar adlarıyla yazılır
KUNYE_ETIKETLERI = ('arşiv PDF künyesi (OCR + haftanın günü kontrolü)', 'arşiv PDF künyesi (görsel okuma)')
kusurlu = sorted((yil_anahtar | gun_ay) & set(satir), key=lambda k: (int(k[0]), int(k[1])))
etiketli = collections.Counter(satir[k]['tarih_kaynagi'] for k in kusurlu if satir[k]['tarih_kaynagi'] in KUNYE_ETIKETLERI)
ayri = {}
for k in kusurlu:
    e = satir[k]['tarih_kaynagi']
    if e not in KUNYE_ETIKETLERI:
        ayri.setdefault(kod.get(e, e), []).append(dict(GUN_AY).get(k, k[0] if k[1] == '0' else f'{k[0]} ({k[1]}. mükerrer)'))
cumle = []
if etiketli:
    cumle.append(f'Bunların {f(sum(etiketli.values()))} tanesi, tarihin geri kalanı ve gün adı künyeden okunduğu için künye okumasının '
                 'etiketini taşır (' + ', '.join(f'`{kod.get(e, e)}` {f(etiketli[e])}' for e in KUNYE_ETIKETLERI if etiketli[e]) + ')'
                 + ('; ayrı etiketli olanlar yalnızca ' + ve_ile([f"{', '.join(a)} (`{e}`)" for e, a in ayri.items()]) if ayri else '')
                 + '. Bu satırları `tarih_kaynagi` değil `not` kolonu ayırt eder.')
rep['{KUNYE_ETIKET_CUMLESI}'] = ''.join(cumle)
val = dict(s.get('atif_dogrulama') or json.load(open(f'{SCR}/data/validation_stats.json', encoding='utf-8')))
dag = s['tarih_kaynagi_dagilimi']
val['TBMM_COZ'] = dag.get('TBMM kanun/karar kaydı (Resmî Gazete tarih ve sayısı)', 0)
val['RG_COZ'] = dag.get('Resmî Gazete metinlerindeki tarih–sayı atfı', 0)
rep.update({'{' + k + '}': f(v) if isinstance(v, int) else str(v) for k, v in val.items()})
d = val.get('TBMM_DIGER') or 0
rep['{TBMM_DIGER_CUMLE}'] = f'; {f(d)} tanesi ise ikisi de değil, künyeye yeniden bakılmalı' if d else ''
# Bağımsız atıflarla doğrulamanın ayrıntıları: scripts/atif_dogrula.py'nin tanımlarıyla, depodaki kanıt dosyalarından. Liste
# değiştikçe değişebildikleri için elle yazılmaz: «aynı» sayılan sayılarda listeyle çelişen atıflar, karşılaştırmaya girmeyen
# atıflar ve sıraya sığan TBMM vakalarında tarihimizin kaynağı.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import atif_dogrula as AD
_, detay, _ = AD.hesapla(REPO)
ham, ham_say = AD.tbmm_ham(REPO)
if ham is None:
    raise SystemExit('render_readme.py: kanit/tbmm_kanunlar.jsonl.gz ya da kanit/tbmm_kararlar.jsonl.gz yok')
with gzip.open(os.path.join(REPO, 'kanit', 'atiflar.json.gz'), 'rt', encoding='utf-8') as fh:
    atiflar = json.load(fh)
ours = {int(r['sayi']): r for r in liste if r['mukerrer'] == '0'}
gune = collections.defaultdict(list)
for n, r in ours.items(): gune[r['tarih']].append(n)
kesin = sorted(n for n, r in ours.items() if not AD.tahmin_mi(r['tarih_kaynagi']))
def atif_sinifi(n, d):
    """Listedeki tarih atıf tarihlerinden biriyle tutan n sayısına yapılmış, listeyle çelişen d tarihli atıf; atif_dogrula.py'nin
    FARK kurallarıyla: 'typo' (d'de çıkmış bir sayının numarası n'den ya da d listedeki tarihten tek hane / komşu iki hanenin
    yer değiştirmesi kadar farklı), 'imkansiz' (d komşu sayıların tarih aralığına düşmüyor) ya da 'diger'."""
    ourd = ours[n]['tarih']
    if any(AD.one_edit(n, m) for m in gune.get(d, [])) or AD.one_edit(ourd.replace('-', ''), d.replace('-', '')):
        return 'typo'
    i, j = bisect.bisect_left(kesin, n), bisect.bisect_right(kesin, n)
    if (i > 0 and d < ours[kesin[i - 1]]['tarih']) or (j < len(kesin) and d > ours[kesin[j]]['tarih']):
        return 'imkansiz'
    return 'diger'
def gizli(cit):
    """{n: [(tarih, adet)]} → (sınıf → atıf adedi, sayı adedi): «aynı» sayılan sayılarda listedeki tarihle çelişen atıflar."""
    c, sayilar = collections.Counter(), set()
    for n, lst in cit.items():
        r = ours.get(n)
        if r is None or AD.kapsam(r['tarih_kaynagi']) or r['tarih'] not in {t for t, _ in lst}:
            continue
        for t, adet in lst:
            if t != r['tarih']:
                c[atif_sinifi(n, t)] += adet; sayilar.add(n)
    return c, len(sayilar)
def sinif_metni(c):
    parca = [(a, m) for a, m in ((c['typo'], 'tek haneli yazım hatası gibi'), (c['imkansiz'], 'sayı sırasıyla bağdaşmıyor'),
                                 (c['diger'], 'ikisi de değil, künyeye yeniden bakılmalı')) if a]
    return 'hepsi ' + parca[0][1] if len(parca) == 1 else ', '.join(f'{f(a)} tanesi {m}' for a, m in parca)
metin = lambda blok: {int(k): [(x['date'], x['count']) for x in v] for k, v in (atiflar.get(blok) or {}).items()}
son_sayi = max(ours)
for ad, cit in (('TBMM', {n: [(c['date'], 1) for c in lst] for n, lst in ham.items()}), ('HF', metin('cit_hf')), ('ERA1', metin('cit_era1'))):
    c, sayi_adedi = gizli(cit)
    disi = sorted(n for n in cit if n > son_sayi)
    garip = sorted(n for n in cit if n not in ours and n <= son_sayi)
    if garip:   # şablon yalnızca «son sayıdan büyük» numaraları anlatır; listede olmayan başka bir numara (0, eksik sayı) yazılmaz
        uyarilar.append(f'{ad} atıflarında listede olmayan ama son sayıdan büyük de olmayan numaralar var, README bunları anmıyor: {garip[:10]}')
    # Adet kayıt/atıf adedidir; bir numaraya birden çok kayıt varsa sayı adedi de yazılır («6 sayıya yapılmış 7 kayıt»)
    disi_adet = sum(a for n in disi for _, a in cit[n])
    rep.update({f'{{{ad}_GIZLI}}': f(sum(c.values())), f'{{{ad}_GIZLI_SAYI}}': f(sayi_adedi), f'{{{ad}_GIZLI_SINIF}}': sinif_metni(c),
                f'{{{ad}_LISTEDISI}}': f(disi_adet) if disi_adet == len(disi) else f'{f(len(disi))} sayıya yapılmış {f(disi_adet)}',
                f'{{{ad}_LISTEDISI_NUMARALAR}}': ', '.join(map(str, disi))})
rep['{TBMM_TARIHSIZ}'] = f(ham_say.get('tarih_ayristirilamadi', 0))
ETIKET_KAYNAGI = {   # «… vakada bizim tarihimiz X geliyor»
    'arşiv PDF künyesi (OCR + haftanın günü kontrolü)': "arşiv PDF'inin ilk sayfa metnindeki künyeden (OCR)",
    'arşiv PDF künyesi (görsel okuma)': 'künyenin görsel okumasından',
    'resmî site günlük sayfası': 'resmî günlük sayfadan',
    'aynı sayının mükerrer nüshasının künyesi': 'aynı numaralı mükerrerin künyesinden',
    'komşu sayılardan kesin çıkarım': 'künyedeki gün adı ve komşu sayılardan',
    'künyedeki haftanın günü + komşu sayılar (künyedeki gün rakamı hatalı/kırık)': 'künyedeki gün adı ve komşu sayılardan'}
sig = detay['TBMM_SIRAYA_SIGAN']
rep['{TBMM_SIRAYA_SIGAN_CUMLE}'] = ''
if sig:
    kaynak = collections.Counter(ETIKET_KAYNAGI.get(ours[n]['tarih_kaynagi'], f"«{ours[n]['tarih_kaynagi']}» kaynağından") for n in sig)
    dokum = next(iter(kaynak)) if len(kaynak) == 1 else ', '.join(f'{f(a)} tanesinde {k}' for k, a in kaynak.most_common())
    yerel = set()
    if os.path.exists(os.path.join(REPO, 'kanit', 'yerel_okumalar.jsonl.gz')):
        with gzip.open(os.path.join(REPO, 'kanit', 'yerel_okumalar.jsonl.gz'), 'rt', encoding='utf-8') as fh:
            yerel = {json.loads(l).get('anahtar') for l in fh}
    yeniden = [n for n in sig if str(n) in yerel]
    kayit = ('bu vakalarda künyenin yeniden okunduğuna ya da günlük sayfanın yeniden kontrol edildiğine dair kayıt depoda yok' if not yeniden
             else 'hepsinin künyesi yerel tamamlamada yeniden okundu (`kanit/yerel_okumalar.jsonl.gz`)' if len(yeniden) == len(sig)
             else f'{f(len(yeniden))} tanesinin künyesi yerel tamamlamada yeniden okundu (`kanit/yerel_okumalar.jsonl.gz`), öbürlerinin '
                  'yeniden okunduğuna ya da günlük sayfasının yeniden kontrol edildiğine dair kayıt depoda yok')
    # Bu vakaların hangisi yukarıdaki tek haneli yazım hatalarından (TBMM kaydında sayı ya da tarih yanlış yazılmış)
    typo_sayi = [n for n in sig if n in set(detay['TBMM_TYPO']['sayi'])]
    typo_tarih = [n for n in sig if n in set(detay['TBMM_TYPO']['tarih'])]
    typo = len(typo_sayi) + len(typo_tarih)
    typo_parca = [(len(x), m) for x, m in ((typo_sayi, 'sayı'), (typo_tarih, 'tarih')) if x]
    tur = ', '.join(f'{f(a)} tanesinde ' + ('TBMM kaydındaki ' if i == 0 else '') + m for i, (a, m) in enumerate(typo_parca))
    bas = (f'Sıraya sığan {f(len(sig))} vakada ' if not typo else
           f"Sıraya sığan {f(len(sig))} vakanın {'hepsi' if typo == len(sig) else f(typo) + ' tanesi'} bu tek haneli yazım "
           f"hatalarından ({tur} yanlış yazılmış); ")
    rep['{TBMM_SIRAYA_SIGAN_CUMLE}'] = f'{bas}bizim tarihimiz {dokum} geliyor; {kayit}.'
out = tpl
for k, v in rep.items(): out = out.replace(k, v)
left = re.findall(r'\{[A-Z_0-9]+\}', out)
assert not left, left
open(f'{REPO}/README.md', 'w', encoding='utf-8', newline='\n').write(out)
for u in uyarilar:
    print('UYARI:', u)
print('ok', two, gun)
