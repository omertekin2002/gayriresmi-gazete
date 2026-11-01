#!/usr/bin/env python3
"""Robust masthead date candidate extraction for noisy OCR text of Resmi Gazete issues."""
import re, datetime, unicodedata

FOLD = str.maketrans({'ı':'i','İ':'i','I':'i','ş':'s','Ş':'s','ğ':'g','Ğ':'g','ü':'u','Ü':'u','ö':'o','Ö':'o','ç':'c','Ç':'c',
                      'â':'a','Â':'a','î':'i','Î':'i','û':'u','Û':'u','ý':'i','Ý':'i','þ':'s','Þ':'s','ð':'g','Ð':'g','ê':'e','é':'e','è':'e','ô':'o','à':'a','á':'a','í':'i','ì':'i','ú':'u','ù':'u','ó':'o','ò':'o','ä':'a','ë':'e'})

def fold(s):
    s = unicodedata.normalize('NFC', s)
    s = s.translate(FOLD).lower()
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(ch for ch in s if not unicodedata.combining(ch))
    return s

def collapse_spaced(s):
    # "m a y i s" -> "mayis" ; "e k i m" -> "ekim"
    return re.sub(r'\b(?:[a-z] ){2,}[a-z]\b', lambda m: m.group(0).replace(' ', ''), s)

MONTHS = [
    (1, ['ocak', 'kanunusani', 'kanunisani', 'kanunsani', 'ikincikanun', 'ikinci kanun', 'ikincikanunu']),
    (2, ['subat', 'şubat']),
    (3, ['mart']),
    (4, ['nisan']),
    (5, ['mayis', 'mayıs']),
    (6, ['haziran']),
    (7, ['temmuz']),
    (8, ['agustos']),
    (9, ['eylul']),
    (10, ['ekim', 'tesrinievvel', 'tesrinevvel', 'tesriniewel', 'birincitesrin', 'birinci tesrin', 'tesrini evvel', 'tesrinievel']),
    (11, ['kasim', 'tesrinisani', 'tesrinsani', 'ikincitesrin', 'ikinci tesrin', 'tesrini sani']),
    (12, ['aralik', 'kanunuevvel', 'kanunievvel', 'kanunevvel', 'kanunuevel', 'kanunievel', 'birincikanun', 'birinci kanun', 'kanunu evvel', 'kanuni evvel']),
]
MONTH_ALTS = []
for num, names in MONTHS:
    for n in names:
        MONTH_ALTS.append((fold(n), num))
MONTH_ALTS.sort(key=lambda x: -len(x[0]))
MONTH_RE = '|'.join(re.escape(a).replace(r'\ ', r'\s*') for a, _ in MONTH_ALTS)
MONTH_MAP = {a.replace(' ', ''): n for a, n in MONTH_ALTS}

WEEKDAYS = [('pazartesi', 0), ('cumartesi', 5), ('carsamba', 2), ('persembe', 3), ('pazar', 6), ('sali', 1), ('cuma', 4)]
WD_RE = re.compile(r'(?<![a-z])(pazartesi|cumartesi|carsamba|persembe|pazar|sali|cuma)(?![a-z])')

SEP = r'[\s\]\)\(\[.,\'"`’‘“”*|:;_\-–—/]{0,6}'
DATE_RE = re.compile(r'(?<!\d)(\d{1,2})' + SEP + r'(' + MONTH_RE + r')(?![a-z])', re.S)
DATE_RE3 = re.compile(r'(?<!\d)\d(\d{2})' + SEP + r'(' + MONTH_RE + r')(?![a-z])', re.S)
YEAR_RE = re.compile(r'(?<!\d)(1[39]\d\d|200\d)(?!\d)')

def to_greg_year(y):
    if 1330 <= y <= 1345:  # Rumi (Mali) year, Gregorian months since 1917
        return y + 584
    return y

def collapse_digits(s):
    # "1 5 kasim" -> "15 kasim" ; "1 9 5 8" -> "1958"
    return re.sub(r'(?<![0-9])(?:[0-9] ){1,3}[0-9](?![0-9])', lambda m: m.group(0).replace(' ', ''), s)

def norm_text(t):
    t = fold(t or '')
    t = t.replace('\r', '')
    t = collapse_spaced(t)
    t = collapse_digits(t)
    return t

def lev(a, b):
    if abs(len(a) - len(b)) > 2: return 9
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]

FUZZY_RE = re.compile(r'(?<!\d)(\d{1,2})[\s\]\)\(\[.,\'"`|:;_\-–—/]{0,6}([a-z]{4,14})(?![a-z])')
def fuzzy_month(w):
    best = None
    for a, n in MONTH_ALTS:
        a2 = a.replace(' ', '')
        d = lev(w, a2)
        lim = 1 if len(a2) <= 6 else 2
        if d <= lim and (best is None or d < best[0]): best = (d, n)
    return best[1] if best else None

def candidates(text, top=900):
    """Return list of (date, pos, kind) candidates and weekday list from masthead region."""
    t = norm_text(text)
    head = t[:top]
    cands = []
    ms = [(m, 0) for m in DATE_RE.finditer(head)] + [(m, 1) for m in DATE_RE3.finditer(head)]
    exact_pos = {m.start() for m, _ in ms}
    for m in FUZZY_RE.finditer(head):
        if m.start() in exact_pos or MONTH_MAP.get(m.group(2)): continue
        if fuzzy_month(m.group(2)): ms.append((m, 2))
    for m, noisy in ms:
        day = int(m.group(1)); mon = MONTH_MAP.get(re.sub(r'\s+', '', m.group(2))) or (fuzzy_month(m.group(2)) if noisy == 2 else None)
        if not mon or not (1 <= day <= 31):
            continue
        tail = head[m.end(): m.end() + 45]
        years = [int(y) for y in YEAR_RE.findall(tail)]
        # also years before (some layouts put year on previous line)
        before = head[max(0, m.start() - 25): m.start()]
        ys_before = [int(y) for y in YEAR_RE.findall(before)]
        for rank, y in enumerate(years[:3]):
            gy = to_greg_year(y)
            try:
                d = datetime.date(gy, mon, day)
            except ValueError:
                continue
            if d == datetime.date(1920, 10, 7):
                continue
            cands.append((d, m.start(), ('noisy%d' if noisy else 'after%d') % rank))
        for y in ys_before[-1:]:
            gy = to_greg_year(y)
            try:
                d = datetime.date(gy, mon, day)
            except ValueError:
                continue
            if d == datetime.date(1920, 10, 7):
                continue
            cands.append((d, m.start(), 'before'))
        # year-less candidate: keep (day, mon) for neighbor-based year inference
        cands.append(((None, mon, day), m.start(), 'noyear'))
    wds = [w for w in WD_RE.findall(head[:700])]
    wdnums = []
    for w in wds:
        for name, n in WEEKDAYS:
            if w == name:
                wdnums.append(n)
    sayi = None
    m = re.search(r's\s*a\s*y\s*[i1l]\s*[:;.]?\s*(\d[\d ]{0,6}\d|\d)', t[:1200])
    if m:
        sayi = int(m.group(1).replace(' ', ''))
    muk = bool(re.search(r'mukerrer', t[:900]))
    return cands, wdnums, sayi, muk

if __name__ == '__main__':
    import sys, json
    for line in open(sys.argv[1], encoding='utf-8'):
        r = json.loads(line)
        if r.get('status') != 'ok':
            continue
        c, w, s, mk = candidates((r.get('text1') or '') + '\n' + (r.get('text2') or ''))
        print(r['key'], s, mk, w, [(str(x[0]), x[2]) for x in c][:6])
