#!/usr/bin/env python3
import sys, json, re, html, subprocess, datetime, time, os
from concurrent.futures import ThreadPoolExecutor
start = datetime.date.fromisoformat(sys.argv[1]); end = datetime.date.fromisoformat(sys.argv[2]); out = sys.argv[3]
done = set()
if os.path.exists(out):
    for l in open(out, encoding='utf-8'):
        try:
            r = json.loads(l)
            if r.get('http') == 200: done.add(r['date'])
        except Exception: pass
days = []
d = start
while d <= end:
    if d.isoformat() not in done: days.append(d)
    d += datetime.timedelta(days=1)
HDR = re.compile(r'^T\.C\. Resmi Gazete (\d\d\.\d\d\.\d{4})/(\d+)(?:\s+(\d+)\.\s*Mükerrer)?\s*$')
def fetch(d):
    url = 'https://www.lexpera.com.tr/resmi-gazete/yayintarihi/' + d.strftime('%d-%m-%Y')
    for attempt in range(4):
        p = subprocess.run(['curl', '-sS', '--max-time', '60', '-L', '-w', '\n__HTTP__%{http_code}', url], capture_output=True)
        body = p.stdout.decode('utf-8', 'replace')
        m = re.search(r'\n__HTTP__(\d+)$', body)
        code = int(m.group(1)) if m else 0
        body = body[:m.start()] if m else body
        if code == 200: break
        time.sleep(2 ** attempt)
    t = re.sub(r'<script.*?</script>|<style.*?</style>', '', body, flags=re.S)
    t = re.sub(r'<[^>]+>', '\n', t); t = html.unescape(t)
    lines = [l.strip() for l in t.split('\n') if l.strip()]
    title = lines[0] if lines else ''
    issues, pseudo, raw = [], [], []
    for i, l in enumerate(lines):
        if l.startswith('T.C. Resmi Gazete'):
            raw.append(l)
            mm = HDR.match(l)
            if mm:
                num = mm.group(2); muk = int(mm.group(3)) if mm.group(3) else 0
                # count items until next header
                n_items = 0
                for l2 in lines[i+1:]:
                    if l2.startswith('T.C. Resmi Gazete') or re.match(r'^\d\d\.\d\d\.\d{4} - Resmi Gazete dışındaki kaynak', l2) or l2 == 'FİLTRELER': break
                    n_items += 1
                rec = {'hdr_date': mm.group(1), 'num': num, 'mukerrer': muk, 'n_lines': n_items}
                (pseudo if len(num) == 8 else issues).append(rec)
    return {'date': d.isoformat(), 'http': code, 'title': title, 'issues': issues, 'pseudo': pseudo, 'raw_headers': raw}
with ThreadPoolExecutor(max_workers=4) as ex, open(out, 'a', encoding='utf-8') as f:
    for i, r in enumerate(ex.map(fetch, days)):
        f.write(json.dumps(r, ensure_ascii=False) + '\n'); f.flush()
        if i % 200 == 0: print(i, r['date'], r['http'], [x['num'] for x in r['issues']], flush=True)
print('DONE', len(days))
