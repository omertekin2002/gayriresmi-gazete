#!/usr/bin/env python3
"""Ingest Resmi Gazete PDFs downloaded by WebFetch.
Usage:
  python3 -I rg_ingest.py OUT.jsonl ITEM [ITEM ...]
ITEM forms (use quotes):
  "KEY|URL|/abs/path/to/saved.pdf"   -> downloaded PDF, extract text then DELETE the file
  "KEY|URL|404"                      -> server returned 404
  "KEY|URL|ERR:<short message>"      -> other failure
KEY examples: 7558  7558_1  7558_2  500T  500_1T
"""
import sys, json, os, subprocess, re

def run(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, timeout=120).stdout.decode('utf-8', 'replace')
    except Exception as e:
        return ''

def main():
    out = sys.argv[1]
    recs = []
    for item in sys.argv[2:]:
        parts = item.split('|', 2)
        if len(parts) != 3:
            print('BAD ITEM (need KEY|URL|PATH-or-404-or-ERR):', item); continue
        key, url, third = [p.strip() for p in parts]
        rec = {'key': key, 'url': url}
        if third == '404':
            rec['status'] = '404'
        elif third.startswith('ERR'):
            rec['status'] = 'error'; rec['error'] = third[4:][:300]
        else:
            path = third
            if not os.path.isfile(path):
                rec['status'] = 'error'; rec['error'] = 'saved file not found: ' + path
            else:
                rec['status'] = 'ok'
                rec['bytes'] = os.path.getsize(path)
                info = run(['pdfinfo', path])
                m = re.search(r'^Pages:\s+(\d+)', info, re.M); rec['pages'] = int(m.group(1)) if m else None
                m = re.search(r'^Producer:\s+(.*)$', info, re.M); rec['producer'] = m.group(1).strip() if m else None
                t1 = run(['pdftotext', '-f', '1', '-l', '1', path, '-'])
                rec['text1'] = t1[:3500]
                if len(t1.strip()) < 200:
                    rec['text2'] = run(['pdftotext', '-f', '2', '-l', '2', path, '-'])[:1500]
                try:
                    safe = re.sub(r'[^0-9A-Za-z_]', '', key) or 'unk'
                    p1dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(out))), 'p1')
                    os.makedirs(p1dir, exist_ok=True)
                    base = os.path.join(p1dir, safe)
                    subprocess.run(['pdftoppm', '-f', '1', '-l', '1', '-gray', '-png', '-singlefile', '-scale-to-x', '1100', '-scale-to-y', '-1', '-x', '0', '-y', '0', '-W', '1100', '-H', '760', path, base], capture_output=True, timeout=120)
                    if os.path.isfile(base + '.png'): rec['p1'] = base + '.png'
                except Exception:
                    pass
                try:
                    os.remove(path)
                except Exception:
                    pass
        recs.append(rec)
    with open(out, 'a', encoding='utf-8') as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    for r in recs:
        m = re.search(r'S\s*a\s*y\s*[ıiı]\s*[:;.]?\s*(\d[\d ]{0,6})', r.get('text1', '') or '', re.I)
        print(r['key'], r['status'], r.get('bytes', ''), r.get('pages', ''), ('Sayi~' + m.group(1).replace(' ', '')) if m else '')

if __name__ == '__main__':
    main()
