import json, glob, sys, os
W = sys.argv[1]; OUT = sys.argv[2]
res = {}
for j in glob.glob(os.path.join(W, '*', 'journal.jsonl')):
    for l in open(j, encoding='utf-8'):
        try: r = json.loads(l)
        except Exception: continue
        if r.get('type') != 'result': continue
        v = r.get('result')
        if isinstance(v, dict) and 'results' in v:
            for e in v['results']:
                d = e.get('date')
                if not d: continue
                old = res.get(d)
                if old is None or (old.get('main_status') != 'ok' and e.get('main_status') == 'ok'):
                    res[d] = e
json.dump(res, open(OUT, 'w'), ensure_ascii=False)
print('dates', len(res))
