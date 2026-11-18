#!/usr/bin/env python3
"""README'deki "Bağımsız atıflarla doğrulama" istatistiklerini (data/dogrulama_raporu.json → atif_dogrulama)
yalnızca depodaki dosyalardan yeniden hesaplar. Yalnızca standart kitaplık; hiçbir dosyaya yazmaz, ağa çıkmaz.

kullanım:  python3 atif_dogrula.py <depo> [--detail] [--strict]

  <depo>     deponun kökü (data/ ve kanit/ dizinlerini içeren dizin)
  --detail   dokuz sayıya ek olarak "detay" anahtarı altında FARK / TYPO / IMKANSIZ listelerini,
             kapsam dışı kalan sayıları ve çapraz kontrolleri de yazar
  --strict   çapraz kontrollerden biri tutmazsa çıkış kodu 2

Girdiler
  data/resmi_gazete_sayilari.csv     liste (yalnızca mukerrer == 0 satırları karşılaştırılır)
  kanit/tbmm_kanunlar.jsonl.gz       TBMM ham kayıtları → (tarih, sayı) atıfları   [scripts/citations.py ile aynı ayrıştırma]
  kanit/tbmm_kararlar.jsonl.gz
  kanit/atiflar.json.gz              "cit_hf": Resmî Gazete metinlerinden çıkarılmış atıflar (HF derlemi depoda yok,
                                     bu yüzden tek kaynak bu); "citations": TBMM atıflarının derleme anındaki hâli (çapraz kontrol);
                                     "citation_decisions": derleme anındaki kararlar (çapraz kontrol)
  data/tbmm_rg_atiflari.csv          TBMM atıflarının tablo hâli (çapraz kontrol)

Tanımlar (scripts/adjudicate.py + özgün derlemedeki validation_stats.json'un yeniden kurulmuş hâli)
  Karşılaştırma kümesi: listede asıl sayı olarak bulunan ve tarihi ne tahmin ne de atıf olan sayılar. Yani
      tarih_kaynagi ∉ { "komşu sayılardan tahmin (kesin değil)", "TBMM kanun/karar kaydı (…)",
                        "Resmî Gazete metinlerindeki tarih–sayı atfı", "başka resmî metinlerde geçen tarih–sayı atfı" }.
      (Künye, günlük sayfa, mükerrer nüshanın künyesi, komşulardan kesin çıkarım ve elle künye düzeltmesi kümededir.)
  TBMM_SAYI      kümede olup en az bir TBMM atfı bulunan sayı numarası adedi
  TBMM_AYNI      atıf tarihlerinden biri listedeki tarihle birebir aynı
  TBMM_FARK      TBMM_SAYI − TBMM_AYNI
  TBMM_TYPO      FARK içinde (a) atıf tarihlerinden birinde yayımlanmış ve numarası n'den tek hane / komşu iki hanenin
                 yer değiştirmesi kadar farklı bir sayı var (TBMM kaydındaki SAYI hatası), ya da (b) bütün atıf tarihleri
                 listedeki tarihten (YYYYAAGG) tek hane / komşu yer değiştirme kadar farklı (TARİH hatası)
  TBMM_IMKANSIZ  FARK içinde typo ile açıklanamayan ve atıf tarihlerinin hiçbiri [önceki sayının tarihi, sonraki sayının
                 tarihi] aralığına düşmeyen (sayı sırasıyla bağdaşmayan) kayıtlar
  HF_SAYI/AYNI/FARK   aynı küme ve aynı "aynı" tanımı, atıflar kanit/atiflar.json.gz → cit_hf
  HF_IMKANSIZ    FARK içinde atıf tarihlerinin hiçbiri komşu sayıların aralığına düşmeyenler
  Komşu aralığı: n'den küçük/büyük en yakın, tarihi tahmin OLMAYAN asıl sayıların tarihleri (uçlar dahil);
  scripts/yerel_tamamla.py'deki komsu() ile aynı kural.
"""
import bisect
import collections
import csv
import datetime
import gzip
import json
import os
import re
import sys

ANAHTARLAR = ['TBMM_SAYI', 'TBMM_AYNI', 'TBMM_FARK', 'TBMM_TYPO', 'TBMM_IMKANSIZ', 'HF_SAYI', 'HF_AYNI', 'HF_FARK', 'HF_IMKANSIZ']

# scripts/merge.py TAG / scripts/yerel_tamamla.py ETIKET ile aynı etiketler
TAHMIN = 'komşu sayılardan tahmin (kesin değil)'
ATIF_ETIKETLERI = {
    'TBMM kanun/karar kaydı (Resmî Gazete tarih ve sayısı)',
    'Resmî Gazete metinlerindeki tarih–sayı atfı',
    'başka resmî metinlerde geçen tarih–sayı atfı',
}
BILINEN_ETIKETLER = ATIF_ETIKETLERI | {
    TAHMIN,
    'künyedeki haftanın günü + komşu sayılar (künyedeki gün rakamı hatalı/kırık)',
    'aynı sayının mükerrer nüshasının künyesi',
    'resmî site günlük sayfası',
    'arşiv PDF künyesi (OCR + haftanın günü kontrolü)',
    'arşiv PDF künyesi (görsel okuma)',
    'komşu sayılardan kesin çıkarım',
    'asıl sayının tarihi',
    'Lexpera günlük listesi',
}


def tahmin_mi(etiket):
    return 'tahmin' in etiket          # adjudicate.py / citations.py ile aynı ölçüt


def kapsam(etiket):
    """'tahmin' | 'atif' | None (None = karşılaştırma kümesinde)."""
    if tahmin_mi(etiket):
        return 'tahmin'
    if etiket in ATIF_ETIKETLERI:
        return 'atif'
    return None


# ----------------------------------------------------------------------------- TBMM atıfları (scripts/citations.py)
def norm_date(s):
    s = s.strip().replace('/', '.').replace('-', '.')
    m = re.match(r'(\d{1,2})\.(\d{1,2})\.(\d{4})$', s)
    if not m:
        return None
    d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
    if 1330 <= y <= 1345:              # Rumi (mali) yıl
        y += 584
    try:
        return datetime.date(y, mo, d).isoformat()
    except ValueError:
        return None


def mukerrer_isareti(ek):
    """TBMM kaydının sayı numarasından sonraki `ek` metnindeki mükerrer işareti: 'acik' («Mükerrer», «2. Mükerrer», «(mük.)» …),
    'kisaltma' («M.», «M», «2.M», «- 2.M» …) ya da None."""
    ek = ek.strip()
    if re.search(r'm[üu]k', ek, re.I):
        return 'acik'
    if re.fullmatch(r'-?\s*(\d\s*\.\s*)?M\.?', ek):
        return 'kisaltma'
    return None


def tbmm_ham(repo):
    """kanit/tbmm_*.jsonl.gz → ({n: [{'date','src','ref','muk'}]}, sayaçlar); dosyalar yoksa (None, None)."""
    cit = collections.defaultdict(list)
    say = collections.Counter()
    yollar = ((os.path.join(repo, 'kanit', 'tbmm_kanunlar.jsonl.gz'), 'Kanun'),
              (os.path.join(repo, 'kanit', 'tbmm_kararlar.jsonl.gz'), 'TBMM Kararı'))
    if not all(os.path.exists(p) for p, _ in yollar):
        return None, None
    for p, kind in yollar:
        with gzip.open(p, 'rt', encoding='utf-8') as f:
            for l in f:
                r = json.loads(l)
                for x in r['recs']:
                    say['kayit'] += 1
                    raw = x.get('rg_raw') or ''
                    m = re.match(r'\s*([0-9./-]+)\s*No\s*:\s*(\d+)\s*(.*)$', raw)
                    if not m:
                        say['rg_bilgisi_yok'] += 1
                        continue
                    iso = norm_date(m.group(1))
                    n = int(m.group(2))
                    if not iso:
                        say['tarih_ayristirilamadi'] += 1
                        continue
                    isaret = mukerrer_isareti(m.group(3))
                    cit[n].append({'date': iso, 'src': 'tbmm', 'ref': f"{kind} {x['law']} (kabul {x['kabul']})", 'muk': isaret == 'acik',
                                   'muk_isareti': isaret})
                    say['atif'] += 1
    return dict(cit), dict(say)


def tbmm_tablo(repo):
    """data/tbmm_rg_atiflari.csv → {n: Counter(tarih)} (yalnızca çapraz kontrol için)."""
    p = os.path.join(repo, 'data', 'tbmm_rg_atiflari.csv')
    if not os.path.exists(p):
        return None
    out = collections.defaultdict(collections.Counter)
    with open(p, encoding='utf-8', newline='') as f:
        for r in csv.DictReader(f):
            iso = norm_date(r['rg_tarihi_kayitta'])
            if iso and r['rg_sayisi_kayitta'].isdigit():
                out[int(r['rg_sayisi_kayitta'])][iso] += 1
    return out


# ----------------------------------------------------------------------------- karşılaştırma (scripts/adjudicate.py)
def one_edit(a, b):
    """Aynı uzunlukta iki rakam dizisi tek hane ya da komşu iki hanenin yer değiştirmesi kadar mı farklı?"""
    a, b = str(a), str(b)
    if len(a) != len(b):
        return False
    diff = [i for i in range(len(a)) if a[i] != b[i]]
    if len(diff) == 1:
        return True
    if len(diff) == 2 and diff[1] == diff[0] + 1 and a[diff[0]] == b[diff[1]] and a[diff[1]] == b[diff[0]]:
        return True
    return False


def hesapla(repo):
    """→ (istatistikler: dict, detay: dict, uyarilar: list[str])"""
    uyari = []
    with open(os.path.join(repo, 'data', 'resmi_gazete_sayilari.csv'), encoding='utf-8', newline='') as f:
        rows = list(csv.DictReader(f))
    ours = {int(r['sayi']): r for r in rows if r['mukerrer'] == '0'}
    bilinmeyen = sorted({r['tarih_kaynagi'] for r in ours.values()} - BILINEN_ETIKETLER)
    if bilinmeyen:
        uyari.append(f'listede tanınmayan tarih_kaynagi etiketi (karşılaştırma kümesine alındı): {bilinmeyen}')
    by_date = collections.defaultdict(list)
    for n, r in ours.items():
        by_date[r['tarih']].append(n)
    kesin = sorted(n for n, r in ours.items() if not tahmin_mi(r['tarih_kaynagi']))

    def aralik(n):
        """Sayı sırasının n için izin verdiği [en erken, en geç] tarih; uç yoksa None."""
        i = bisect.bisect_left(kesin, n)
        j = bisect.bisect_right(kesin, n)
        return (ours[kesin[i - 1]]['tarih'] if i > 0 else None, ours[kesin[j]]['tarih'] if j < len(kesin) else None)

    def sigar(n, d):
        lo, hi = aralik(n)
        return (lo is None or lo <= d) and (hi is None or d <= hi)

    with gzip.open(os.path.join(repo, 'kanit', 'atiflar.json.gz'), 'rt', encoding='utf-8') as f:
        atiflar = json.load(f)

    # ---- TBMM
    ham, ham_say = tbmm_ham(repo)
    saklanan = {int(k): v for k, v in (atiflar.get('citations') or {}).items()}
    if ham is None:
        uyari.append('kanit/tbmm_kanunlar.jsonl.gz / tbmm_kararlar.jsonl.gz yok; TBMM atıfları kanit/atiflar.json.gz → citations\'tan alındı')
        cit, tbmm_kaynak = saklanan, 'kanit/atiflar.json.gz:citations'
    else:
        cit, tbmm_kaynak = ham, 'kanit/tbmm_kanunlar.jsonl.gz + kanit/tbmm_kararlar.jsonl.gz'
    ozet = lambda c: {n: collections.Counter(x['date'] for x in lst) for n, lst in c.items()}
    capraz = {'tbmm_kaynak': tbmm_kaynak, 'ham_kayit_sayaclari': ham_say,
              'atif_bulunan_sayi_numarasi': len(cit), 'atif_adedi': sum(len(v) for v in cit.values())}
    if ham is not None and saklanan:
        capraz['ham_kayitlar_eq_atiflar_citations'] = ozet(ham) == ozet(saklanan)
        if not capraz['ham_kayitlar_eq_atiflar_citations']:
            uyari.append('TBMM ham kayıtlarından çıkan atıflar kanit/atiflar.json.gz → citations ile aynı değil')
    tablo = tbmm_tablo(repo)
    if tablo is not None:
        capraz['tbmm_rg_atiflari_csv_eq'] = dict(tablo) == ozet(cit)
        if not capraz['tbmm_rg_atiflari_csv_eq']:
            uyari.append('data/tbmm_rg_atiflari.csv, TBMM atıflarıyla aynı (sayı → tarih) eşlemesini vermiyor')

    t = {'ayni': [], 'sayi_typo': [], 'tarih_typo': [], 'imkansiz': [], 'diger': []}
    t_disi = {'listede_yok': [], 'tahmin': [], 'atif': []}
    for n, lst in sorted(cit.items()):
        r = ours.get(n)
        if not r:
            t_disi['listede_yok'].append(n)
            continue
        dates = collections.Counter(c['date'] for c in lst)
        ourd = r['tarih']
        k = kapsam(r['tarih_kaynagi'])
        if k:
            t_disi[k].append({'sayi': n, 'bizim': ourd, 'kaynak': r['tarih_kaynagi'], 'atif': dict(dates), 'ayni': ourd in dates})
            continue
        if ourd in dates:
            t['ayni'].append(n)
            continue
        lo, hi = aralik(n)
        kayit = {'sayi': n, 'bizim': ourd, 'kaynak': r['tarih_kaynagi'], 'atif': dict(dates), 'aralik': [lo, hi],
                 'siraya_sigar': any(sigar(n, d) for d in dates), 'refs': [c['ref'] for c in lst][:3]}
        expl = None
        for d in dates:
            others = by_date.get(d, [])
            if any(one_edit(n, m) for m in others):
                expl = sorted(m for m in others if one_edit(n, m))
        if expl:
            kayit['sinif'] = 'sayi_typo'; kayit['atif_tarihindeki_benzer_sayi'] = expl
        elif all(one_edit(ourd.replace('-', ''), d.replace('-', '')) for d in dates):
            kayit['sinif'] = 'tarih_typo'
        elif not kayit['siraya_sigar']:
            kayit['sinif'] = 'imkansiz'
        else:
            kayit['sinif'] = 'diger'      # typo değil ama sıraya sığıyor: künyeye yeniden bakılmalı
        t[kayit['sinif']].append(kayit)
    t_fark = t['sayi_typo'] + t['tarih_typo'] + t['imkansiz'] + t['diger']

    # ---- Resmî Gazete metinlerindeki atıflar (HF derlemi)
    def metin_atiflari(blok):
        s = {'sayi': 0, 'ayni': 0, 'fark': [], 'listede_yok': [], 'tahmin': [], 'atif': []}
        for n, lst in sorted((int(k), v) for k, v in (atiflar.get(blok) or {}).items()):
            r = ours.get(n)
            if not r:
                s['listede_yok'].append(n)
                continue
            dates = {x['date']: x['count'] for x in lst}
            ourd = r['tarih']
            k = kapsam(r['tarih_kaynagi'])
            if k:
                s[k].append({'sayi': n, 'bizim': ourd, 'kaynak': r['tarih_kaynagi'], 'atif': dates, 'ayni': ourd in dates})
                continue
            s['sayi'] += 1
            if ourd in dates:
                s['ayni'] += 1
                continue
            lo, hi = aralik(n)
            fit = any(sigar(n, d) for d in dates)
            s['fark'].append({'sayi': n, 'bizim': ourd, 'kaynak': r['tarih_kaynagi'], 'atif': dates, 'aralik': [lo, hi],
                              'siraya_sigar': fit, 'sinif': 'siraya_sigan' if fit else 'imkansiz',
                              'refs': [ref for x in lst for ref in x.get('refs', [])][:3]})
        return s
    if 'cit_hf' not in atiflar:
        uyari.append('kanit/atiflar.json.gz içinde cit_hf yok; HF_* sıfır')
    hf = metin_atiflari('cit_hf')
    e1 = metin_atiflari('cit_era1')

    st = {
        'TBMM_SAYI': len(t['ayni']) + len(t_fark),
        'TBMM_AYNI': len(t['ayni']),
        'TBMM_FARK': len(t_fark),
        'TBMM_TYPO': len(t['sayi_typo']) + len(t['tarih_typo']),
        'TBMM_IMKANSIZ': len(t['imkansiz']),
        'HF_SAYI': hf['sayi'],
        'HF_AYNI': hf['ayni'],
        'HF_FARK': len(hf['fark']),
        'HF_IMKANSIZ': sum(1 for x in hf['fark'] if x['sinif'] == 'imkansiz'),
    }

    # derleme anındaki kararlarla (kanit/atiflar.json.gz → citation_decisions) karşılaştırma: bilgi amaçlı,
    # liste değiştikçe (tahmin/atıf kaynaklı sayılar künyeden tarihlendikçe) farklılaşması beklenir
    dec = atiflar.get('citation_decisions') or {}
    if dec:
        eski = {'sayi_typo': {x['n'] for x in dec.get('tbmm_number_typo', [])}, 'tarih_typo': {x['n'] for x in dec.get('tbmm_date_typo', [])},
                'recheck': {x['n'] for x in dec.get('recheck', [])}}
        yeni = {'sayi_typo': {x['sayi'] for x in t['sayi_typo']}, 'tarih_typo': {x['sayi'] for x in t['tarih_typo']},
                'recheck': {x['sayi'] for x in t['imkansiz'] + t['diger']}}
        capraz['derleme_anindaki_kararlar'] = {
            'agree': dec.get('agree'), 'tbmm_number_typo': len(eski['sayi_typo']), 'tbmm_date_typo': len(eski['tarih_typo']),
            'recheck': len(eski['recheck']), 'est_fixed': len(dec.get('est_fixed', {})), 'est_conflict': [x['n'] for x in dec.get('est_conflict', [])],
            'ayni_mi': dict({k: eski[k] == yeni[k] for k in eski}, agree=dec.get('agree') == st['TBMM_AYNI']),
            'yalnizca_eskide': {k: sorted(eski[k] - yeni[k]) for k in eski}, 'yalnizca_yenide': {k: sorted(yeni[k] - eski[k]) for k in eski}}

    # EKSIKLER.md 2. bölümdeki dolaylı mükerrer kontrolü: mükerrer işareti taşıyan TBMM kayıtlarının sayısının listede mükerreri var mı?
    muk_liste = collections.Counter(int(r['sayi']) for r in rows if r['mukerrer'] != '0')
    isaretli = [(n, c) for n, lst in sorted(cit.items()) for c in lst if c.get('muk_isareti')]
    muk_kontrol = {'ISARETLI': len(isaretli), 'ACIK': sum(1 for _, c in isaretli if c['muk_isareti'] == 'acik'),
                   'KISALTMA': sum(1 for _, c in isaretli if c['muk_isareti'] == 'kisaltma'),
                   'LISTEDE_MUKERRERI_VAR': sum(1 for n, _ in isaretli if muk_liste.get(n)),
                   'KARSILIKSIZ': [{'sayi': n, 'tarih': c['date'], 'ref': c['ref']} for n, c in isaretli if not muk_liste.get(n)]}

    detay = {
        'TBMM_MUKERRER_ISARETI': muk_kontrol,
        'TBMM_FARK': t_fark,
        'TBMM_TYPO': {'sayi': [x['sayi'] for x in t['sayi_typo']], 'tarih': [x['sayi'] for x in t['tarih_typo']]},
        'TBMM_IMKANSIZ': [x['sayi'] for x in t['imkansiz']],
        'TBMM_DIGER': [x['sayi'] for x in t['diger']],                 # FARK − TYPO − IMKANSIZ (HEAD'de boş)
        'TBMM_SIRAYA_SIGAN': [x['sayi'] for x in t_fark if x['siraya_sigar']],   # README'deki "Sıraya sığan 9 vaka"
        'TBMM_KAPSAM_DISI': t_disi,
        'HF_FARK': hf['fark'],
        'HF_IMKANSIZ': [x['sayi'] for x in hf['fark'] if x['sinif'] == 'imkansiz'],
        'HF_SIRAYA_SIGAN': [x['sayi'] for x in hf['fark'] if x['siraya_sigar']],  # README'deki "biri ise …"
        'HF_KAPSAM_DISI': {k: hf[k] for k in ('listede_yok', 'tahmin', 'atif')},
        # README sayılarına girmez: arşiv PDF'lerinin ilk sayfalarından çıkarılan atıflar (cit_era1), aynı yöntemle
        'ARSIV_ILK_SAYFA_ATIFLARI': {'SAYI': e1['sayi'], 'AYNI': e1['ayni'], 'FARK': len(e1['fark']),
                                     'IMKANSIZ': sum(1 for x in e1['fark'] if x['sinif'] == 'imkansiz'), 'fark': e1['fark']},
        'capraz_kontrol': capraz,
        'uyarilar': uyari,
    }
    return st, detay, uyari


def main(argv):
    args = [a for a in argv[1:] if not a.startswith('--')]
    bayrak = {a for a in argv[1:] if a.startswith('--')}
    if len(args) != 1 or bayrak - {'--detail', '--detay', '--strict'}:
        sys.stderr.write(__doc__)
        return 64
    st, detay, uyari = hesapla(args[0])
    for u in uyari:
        sys.stderr.write('UYARI: ' + u + '\n')
    out = {k: st[k] for k in ANAHTARLAR}
    if bayrak & {'--detail', '--detay'}:
        out['detay'] = detay
        print(json.dumps(out, ensure_ascii=False, indent=1))
    else:
        print(json.dumps(out, ensure_ascii=False))
    return 2 if ('--strict' in bayrak and uyari) else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
