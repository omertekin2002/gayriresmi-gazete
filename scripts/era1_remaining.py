"""İlk derlemenin (15 Kasım 2026) arşiv taramasında (era 1: resmigazete.gov.tr/arsiv/…pdf) henüz bitmemiş sayı numaralarını
bulur ve kalan işi paralel indirme iş akışlarına böler. Yalnızca iş planlamasına yarar; listeyi etkilemez.
kullanım: era1_remaining.py <D> <LO> <HI> <CHUNK> <NWF>

<D>/era1/*.jsonl'deki indirme kayıtlarına bakar: bir sayı numarası, asıl dosyası (1053'e kadar önce <n>T.pdf) okunmuş, 404
dönmüş ya da 10 MB sınırını aşmışsa ve mükerrer dosyaları (<n>_1.pdf, <n>_2.pdf …) ilk 404'e kadar hatasız denenmişse bitmiştir.
LO–HI arasında kalanları en çok CHUNK numaralık aralıklara ayırıp NWF gruba dağıtır ve <D>/era1_groups.json'a yazar (özet
stderr'e). <D> depoda yok; indirme kayıtlarının son hâli kanit/arsiv_pdf_ilk_sayfa.jsonl.gz'dedir."""
import json, glob, os, re, sys
DATA = sys.argv[1]; LO, HI = int(sys.argv[2]), int(sys.argv[3]); CHUNK = int(sys.argv[4]); NWF = int(sys.argv[5])
st = {}
for f in glob.glob(os.path.join(DATA, 'era1', '*.jsonl')):
    for l in open(f, encoding='utf-8'):
        try: r = json.loads(l)
        except Exception: continue
        k = r['key']; s = r['status']
        if s == 'error' and 'maxContentLength' in (r.get('error') or ''): s = 'big'
        prev = st.get(k)
        if prev in ('ok', 'big'): continue
        if prev == '404' and s == 'error': continue
        st[k] = s
def covered(n):
    if n <= 1053:
        t = st.get(f'{n}T')
        if t in ('ok', 'big'): main = True
        elif t == '404': main = st.get(f'{n}') in ('ok', '404', 'big')
        else: main = False
    else:
        main = st.get(f'{n}') in ('ok', '404', 'big')
    if not main: return False
    k = 1
    while True:
        s = st.get(f'{n}_{k}')
        if s is None or s == 'error': return False
        if s == '404': return True
        k += 1
rem = [n for n in range(LO, HI + 1) if not covered(n)]
# intervals
iv = []
for n in rem:
    if iv and iv[-1][1] == n - 1: iv[-1][1] = n
    else: iv.append([n, n])
chunks = []
for a, b in iv:
    x = a
    while x <= b:
        y = min(b, x + CHUNK - 1); chunks.append([x, y]); x = y + 1
print(json.dumps({'covered': HI - LO + 1 - len(rem), 'remaining': len(rem), 'nchunks': len(chunks)}), file=sys.stderr)
per = (len(chunks) + NWF - 1) // NWF
groups = [chunks[i*per:(i+1)*per] for i in range(NWF)]
json.dump(groups, open(os.path.join(DATA, 'era1_groups.json'), 'w'))
for g in groups: print(len(g), g[0] if g else None, g[-1] if g else None, file=sys.stderr)
