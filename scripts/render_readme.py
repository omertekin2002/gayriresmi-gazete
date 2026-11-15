"""README.md'yi scripts/README.template.md ve data/dogrulama_raporu.json'dan üretir.
kullanım: render_readme.py <depo>            (derleme ortamında eski biçim: render_readme.py <scratchpad> <depo>)"""
import json, datetime, sys, re, os
if len(sys.argv) > 2:
    SCR, REPO = sys.argv[1], sys.argv[2]; TPL = f'{SCR}/tools/README.template.md'
else:
    REPO = sys.argv[1]; SCR = None; TPL = os.path.join(REPO, 'scripts', 'README.template.md')
s = json.load(open(f'{REPO}/data/dogrulama_raporu.json'))
tpl = open(TPL, encoding='utf-8').read()
TR_AY = ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık']
def trdate(iso):
    d = datetime.date.fromisoformat(iso); return f'{d.day} {TR_AY[d.month - 1]} {d.year}'
son_iso, son_sayi = s['son'].split(' / Sayı ')
expl = {
    'resmî site günlük sayfası': 'resmigazete.gov.tr günlük sayfası (`eskiler/…htm`), 27.06.2000 sonrası',
    'arşiv PDF künyesi (OCR + haftanın günü kontrolü)': "Arşiv PDF'inin künyesi; OCR + haftanın günü + sıra kontrolü",
    'arşiv PDF künyesi (görsel okuma)': "Arşiv PDF'inin künyesi görüntü olarak okundu",
    'asıl sayının tarihi': 'Mükerrer nüsha; asıl sayıyla aynı gün',
    'aynı sayının mükerrer nüshasının künyesi': "Asıl sayının PDF'i okunamadı; aynı numaralı mükerrerin künyesinden",
    'komşu sayılardan kesin çıkarım': 'Önceki ve sonraki sayılardan tek bir tarih mümkün',
    'komşu sayılardan tahmin (kesin değil)': 'PDF indirilemedi/okunamadı; olası aralık `not` kolonunda',
    'TBMM kanun/karar kaydı (Resmî Gazete tarih ve sayısı)': "PDF indirilemedi; TBMM kaydındaki yayım tarihi ve sayısından",
    'Resmî Gazete metinlerindeki tarih–sayı atfı': "PDF indirilemedi; sonraki Resmî Gazete metinlerindeki atıftan",
    'künyedeki haftanın günü + komşu sayılar (künyedeki gün rakamı hatalı/kırık)': 'Künyedeki gün rakamı baskı hatası/kırık; künyedeki haftanın günü ve komşu sayılardan (gerekçe `not` kolonunda)',
}
f = lambda x: f'{x:,}'.replace(',', '.')
rows = '\n'.join(f'| {k} | {f(v)} | {expl.get(k, "")} |' for k, v in sorted(s['tarih_kaynagi_dagilimi'].items(), key=lambda x: -x[1]))
tah = s['tahmini_tarihli_sayilar']
two = sum(1 for n, d, r in tah if r and (datetime.date.fromisoformat(r[1]) - datetime.date.fromisoformat(r[0])).days == 2)
gun = (datetime.date.fromisoformat(son_iso) - datetime.date(2000, 6, 27)).days + 1
gorsel = s['tarih_kaynagi_dagilimi'].get('arşiv PDF künyesi (görsel okuma)', 0)
rep = {'{SON}': trdate(son_iso), '{SON_SAYI}': son_sayi, '{TOPLAM}': f(s['toplam_yayin']), '{ASIL}': f(s['asil_sayi']), '{MUK}': f(s['mukerrer']),
       '{OLUSTURMA}': trdate(s['olusturma_tarihi']), '{GORSEL}': f(gorsel), '{GUN_SAYISI}': f(gun), '{KAYNAK_TABLO}': rows,
       '{TAHMIN}': f(len(tah)), '{TAHMIN_2GUN}': f(two)}
val = dict(s.get('atif_dogrulama') or json.load(open(f'{SCR}/data/validation_stats.json')))
dag = s['tarih_kaynagi_dagilimi']
val['TBMM_COZ'] = dag.get('TBMM kanun/karar kaydı (Resmî Gazete tarih ve sayısı)', 0)
val['RG_COZ'] = dag.get('Resmî Gazete metinlerindeki tarih–sayı atfı', 0)
rep.update({'{' + k + '}': f(v) if isinstance(v, int) else str(v) for k, v in val.items()})
out = tpl
for k, v in rep.items(): out = out.replace(k, v)
left = re.findall(r'\{[A-Z_0-9]+\}', out)
assert not left, left
open(f'{REPO}/README.md', 'w', encoding='utf-8').write(out)
print('ok', two, gun)
