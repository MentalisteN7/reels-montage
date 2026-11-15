"""Extrait la timeline de tous les projets Premiere d'Harry -> docs/montage_harry/timelines/<ep>.json"""
import os, sys, json, glob
sys.path.insert(0, os.path.dirname(__file__))
from prproj import parse, texts
ROOT = sys.argv[1]; OUT = sys.argv[2]
for d in sorted(os.listdir(ROOT)):
    if d == 'marcello': continue          # épisode test monté à l'aveugle : on ne regarde pas
    ps = glob.glob(os.path.join(ROOT, d, '01 PROJET', '*.prproj'))
    if not ps: continue
    p = max(ps, key=os.path.getmtime)
    try:
        seqs = parse(p); tx = texts(p)
    except Exception as e:
        print(d, 'ERREUR', e); continue
    json.dump({'episode': d, 'project': os.path.basename(p), 'sequences': seqs, 'texts': tx},
              open(os.path.join(OUT, d + '.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    desc = '; '.join(f"{s['name']}={max([i['t1'] for t in s['video'] for i in t] or [0]):.0f}s" for s in seqs)
    print(d, '|', desc)
