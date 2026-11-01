#!/usr/bin/env python3
"""Mine "DD/MM/YYYY tarihli ve NNNNN sayılı Resmî Gazete" citations from text corpora.
Usage: mine_citations.py OUT.json corpus_kind path [corpus_kind path ...]
 corpus kinds: era1 (dir of era1 jsonl with text1), hf (HF jsonl with text)"""
import sys, json, re, glob, os, datetime, collections
OUT = sys.argv[1]; args = sys.argv[2:]
AY = {'ocak': 1, 'subat': 2, 'mart': 3, 'nisan': 4, 'mayis': 5, 'haziran': 6, 'temmuz': 7, 'agustos': 8, 'eylul': 9, 'ekim': 10, 'kasim': 11, 'aralik': 12}
FOLD = str.maketrans('ıİşŞğĞüÜöÖçÇâÂîÎûÛ', 'iissgguuoocCaaiiuu')
D1 = r'(\d{1,2})\s*[./-]\s*(\d{1,2})\s*[./-]\s*(\d{4})'
D2 = r'(\d{1,2})\s+(ocak|subat|mart|nisan|mayis|haziran|temmuz|agustos|eylul|ekim|kasim|aralik)\s+(\d{4})'
PAT = re.compile(r'(?:' + D1 + r'|' + D2 + r')\s*(?:gun ve |gunlu ve |tarih(?:li)?\s*(?:ve|,)?\s*)(\d{3,5})\s*(?:sayi|nolu|no\.?lu|numarali)[a-z]*\s*(?:\(\s*\d*\.?\s*mukerrer\s*\)\s*)?resm[iı]\s*gazete', re.I)
PAT2 = re.compile(r'r\.\s*g\.?\s*[:\-]?\s*' + D1 + r'\s*[-/,]\s*(?:sayi\s*:?\s*)?(\d{3,5})(?!\d)', re.I)
def iso(d, m, y):
    try:
        y = int(y); m = int(m); d = int(d)
        if 1330 <= y <= 1345: y += 584
        return datetime.date(y, m, d).isoformat()
    except Exception: return None
cit = collections.defaultdict(collections.Counter)
src = collections.defaultdict(set)
def scan(text, ref):
    t = text.translate(FOLD).lower()
    t = re.sub(r'\s+', ' ', t)
    for m in PAT.finditer(t):
        g = m.groups()
        if g[0]: dt = iso(g[0], g[1], g[2])
        else: dt = iso(g[3], AY[g[4]], g[5])
        n = int(g[6])
        if dt: cit[n][dt] += 1; len(src[(n, dt)]) < 3 and src[(n, dt)].add(ref)
    for m in PAT2.finditer(t):
        dt = iso(m.group(1), m.group(2), m.group(3)); n = int(m.group(4))
        if dt: cit[n][dt] += 1; len(src[(n, dt)]) < 3 and src[(n, dt)].add(ref)
for kind, path in zip(args[0::2], args[1::2]):
    if kind == 'era1':
        for f in glob.glob(os.path.join(path, '*.jsonl')):
            for l in open(f, encoding='utf-8'):
                try: r = json.loads(l)
                except Exception: continue
                if r.get('text1'): scan(r['text1'] + ' ' + (r.get('text2') or ''), 'arsiv/' + r['key'] + '.pdf (1. sayfa)')
    elif kind == 'hf':
        with open(path, encoding='utf-8', errors='replace') as fh:
            for l in fh:
                try: r = json.loads(l)
                except Exception: continue
                scan(r.get('text') or '', r.get('url') or r.get('id'))
json.dump({str(n): [{'date': d, 'count': c, 'refs': sorted(src[(n, d)])} for d, c in cnt.most_common()] for n, cnt in cit.items()}, open(OUT, 'w'), ensure_ascii=False)
print('issue numbers cited', len(cit), 'citations', sum(sum(c.values()) for c in cit.values()))
