"""README.md'yi scripts/README.template.md, data/dogrulama_raporu.json ve (künye yılı açıklamalarının adetleri için) listeden üretir.
kullanım: render_readme.py <depo>            (derleme ortamında eski biçim: render_readme.py <scratchpad> <depo>)"""
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
# Künyesinde yıl sorunlu sayılar: listenin `not` kolonundaki açıklamalardan sayılır (adetler ve numara listeleri elle yazılmaz)
import csv
yil = {'yanlis': [], 'yok': [], 'kirik': []}
with open(f'{REPO}/data/resmi_gazete_sayilari.csv', encoding='utf-8', newline='') as fh:
    for r in csv.DictReader(fh):
        n = r['not'] or ''
        if 'künyede yıl yanlış basılmış' in n: yil['yanlis'].append(int(r['sayi']))
        elif 'künyede yıl basılı değil' in n: yil['yok'].append(int(r['sayi']))
        elif 'künyede yıl «' in n or 'künyede yılın ' in n: yil['kirik'].append(int(r['sayi']))
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
rep.update({'{YIL_YANLIS_N}': f(len(yil['yanlis'])), '{YIL_YOK_N}': f(len(yil['yok'])), '{YIL_KIRIK_N}': f(len(yil['kirik'])),
            '{YIL_NOT_N}': f(len(yil_hepsi)), '{YIL_KIRIK_LISTE}': aralikli(yil['kirik']), '{YIL_NOT_LISTE}': aralikli(yil_hepsi),
            '{KUNYE_NOT_N}': f(10 + len(yil_hepsi))})   # 10: gün ya da ayı eksik/kırık/yanlış basılmış 244, 293, 588 mük., 1054, 1056, 8489, 10480, 14490, 15890, 16168
val = dict(s.get('atif_dogrulama') or json.load(open(f'{SCR}/data/validation_stats.json', encoding='utf-8')))
dag = s['tarih_kaynagi_dagilimi']
val['TBMM_COZ'] = dag.get('TBMM kanun/karar kaydı (Resmî Gazete tarih ve sayısı)', 0)
val['RG_COZ'] = dag.get('Resmî Gazete metinlerindeki tarih–sayı atfı', 0)
rep.update({'{' + k + '}': f(v) if isinstance(v, int) else str(v) for k, v in val.items()})
out = tpl
for k, v in rep.items(): out = out.replace(k, v)
left = re.findall(r'\{[A-Z_0-9]+\}', out)
assert not left, left
open(f'{REPO}/README.md', 'w', encoding='utf-8', newline='\n').write(out)
print('ok', two, gun)
