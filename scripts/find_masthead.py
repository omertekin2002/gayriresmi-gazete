#!/usr/bin/env python3
"""Given a downloaded gazette PDF, render the top part of the first pages to PNGs for visual reading.
Usage: python3 -I find_masthead.py KEY /path/to/saved.pdf OUTDIR
Prints, per page (max 4), the PNG path and the first 200 chars of OCR text; deletes the PDF afterwards."""
import sys, os, subprocess, re
key, pdf, outdir = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(outdir, exist_ok=True)
safe = re.sub(r'[^0-9A-Za-z_]', '', key)
info = subprocess.run(['pdfinfo', pdf], capture_output=True).stdout.decode('utf-8', 'replace')
m = re.search(r'^Pages:\s+(\d+)', info, re.M); pages = int(m.group(1)) if m else 1
for p in range(1, min(pages, 4) + 1):
    base = os.path.join(outdir, f'{safe}_p{p}')
    subprocess.run(['pdftoppm', '-f', str(p), '-l', str(p), '-gray', '-png', '-singlefile', '-scale-to-x', '1100', '-scale-to-y', '-1', '-x', '0', '-y', '0', '-W', '1100', '-H', '760', pdf, base], capture_output=True)
    t = subprocess.run(['pdftotext', '-f', str(p), '-l', str(p), pdf, '-'], capture_output=True).stdout.decode('utf-8', 'replace')
    t = re.sub(r'\s+', ' ', t)[:200]
    print(f'PAGE {p}: {base}.png | {t}')
try: os.remove(pdf)
except Exception: pass
