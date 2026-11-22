#!/usr/bin/env python3
"""Collect (law, Resmî Gazete date, number) citations from TBMM's legacy laws database.
kullanım: tbmm_citations.py <çıktı.jsonl> <LO> <HI> [v_anabaslik, varsayılan KANUNLAR]

İlk derleme (15 Kasım 2026) hattının betiği; ağa çıkar. LO–HI arasındaki her numara (q) için TBMM "Kanunlar ve Kararlar Erişim"
veritabanını sorgular ve dönen bütün kayıtları (aynı numaralı eski ve yeni dizi kanunları/kararları birlikte döner) bir satır
olarak yazar: {"q", "n_blocks", "recs": [{"law", "kabul", "rg_raw", "title"}]}. Çıktılar depoda:
  kanit/tbmm_kanunlar.jsonl.gz   q 1–7700 (7.700 satır); son 219 sorgu (7482–7700) hiç kayıt döndürmedi.
  kanit/tbmm_kararlar.jsonl.gz   q 1–1600 (1.600 satır); hepsi kayıt döndürdü, sonuncular 1948 kararları (1600: kabul
                                 28/04/1948, RG 04.05.1948 No: 6897). Dosyada 1600'den sonraki karar numaraları yok.
Kayıtlardaki en son Resmî Gazete bilgisi kanunlarda 28.07.2021, sayı 31551 (Kanun 7333 ve 7334), kararlarda 19.07.2021, sayı
31546; 7335 ve sonraki yeni dizi kanunların kayıtlarında RG tarihi ve sayısı yok («Kanun Metni»). Bu yüzden TBMM
karşılaştırması 31551'den sonraki sayıları kapsamaz."""
import sys, json, re, html, subprocess, time, os
from concurrent.futures import ThreadPoolExecutor
OUT = sys.argv[1]; LO, HI = int(sys.argv[2]), int(sys.argv[3]); KIND = sys.argv[4] if len(sys.argv) > 4 else 'KANUNLAR'
done = set()
if os.path.exists(OUT):
    for l in open(OUT):
        try: done.add(json.loads(l)['q'])
        except Exception: pass
URL = 'https://www5.tbmm.gov.tr/develop/owa/kanunlar_erisim.sorgula'
def get(n):
    for a in range(4):
        g = f'https://www5.tbmm.gov.tr/develop/owa/kanunlar_erisim.tutanak_hazirla?v_meclis=&v_donem=&v_yasama_yili=&v_cilt=&v_birlesim=&v_sayfa=&v_anabaslik={KIND}&v_altbaslik={n}&v_mv=&v_sb=&v_ozet=&v_kelime=&v_bastarih=&v_bittarih='
        p = subprocess.run(['curl', '-sS', '-L', '--max-time', '60', g], capture_output=True)
        if p.returncode == 0 and p.stdout: break
        time.sleep(2 ** a)
    t = p.stdout.decode('iso-8859-9', 'replace')
    t = re.sub(r'<script.*?</script>|<style.*?</style>', '', t, flags=re.S)
    t = html.unescape(re.sub(r'<[^>]+>', '\n', t))
    t = re.sub(r'[ \t\r]+', ' ', t); t = re.sub(r'\n\s*\n+', '\n', t)
    recs = []
    for blk in re.split(r'(?:KANUN|KARAR) NO:', t)[1:]:
        m = re.match(r'\s*(\d+)', blk)
        kab = re.search(r'Kabul Tarihi\s*:\s*\n?\s*([0-9./]+)', blk)
        rg = re.search(r'Resmi Gazete Tarihi ve No\s*:\s*\n?\s*([^\n]*)', blk)
        title = re.search(r'\n\s*:\s*([^\n]+)', blk)
        don = None
        recs.append({'law': int(m.group(1)) if m else None, 'kabul': kab.group(1) if kab else None,
                     'rg_raw': rg.group(1).strip() if rg else None, 'title': title.group(1).strip()[:200] if title else None})
    # attach term info
    terms = re.findall(r'TÜRKİYE BÜYÜK MİLLET MECLİSİ -- (\d+)\. Dönem|(MİLLİ BİRLİK KOMİTESİ|KURUCU MECLİS|DANIŞMA MECLİSİ|MİLLİ GÜVENLİK KONSEYİ|CUMHURİYET SENATOSU|MİLLET MECLİSİ)[^\n]*', t)
    return {'q': n, 'n_blocks': len(recs), 'recs': recs}
todo = [n for n in range(LO, HI + 1) if n not in done]
with ThreadPoolExecutor(max_workers=2) as ex, open(OUT, 'a') as f:
    for i, r in enumerate(ex.map(get, todo)):
        f.write(json.dumps(r, ensure_ascii=False) + '\n'); f.flush()
        if i % 250 == 0: print(i, r['q'], r['n_blocks'], (r['recs'][0]['rg_raw'] if r['recs'] else None), flush=True)
print('DONE', len(todo))
