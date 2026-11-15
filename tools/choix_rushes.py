"""Ce qui distingue le morceau de rush choisi par Harry du reste du rush (B-roll sans son direct).

Pour chaque plan B-roll de la séquence finale : profil du rush à 10 i/s (mouvement = différence entre images,
netteté = variance du laplacien, luminosité). On compare la fenêtre choisie à toutes les autres fenêtres de même
longueur dans le même rush -> rang percentile (0 = la plus calme/nette du rush, 1 = la plus agitée/floue).
python tools/choix_rushes.py <Guest-Lunch> <ep1,ep2,...> <sortie.csv>
"""
import os, sys, json, glob, csv, subprocess
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from analyse_timelines import final_seq, is_rush

FPS, W, H = 10, 144, 256

def profile(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-vf', f'fps={FPS},scale={W}:{H}', '-pix_fmt', 'gray',
                          '-f', 'rawvideo', '-'], capture_output=True).stdout
    v = np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(np.float32)
    if len(v) < 3: return None
    motion = np.r_[0, np.abs(np.diff(v, axis=0)).mean((1, 2))]
    lap = np.abs(v[:, 1:-1, 1:-1] * 4 - v[:, :-2, 1:-1] - v[:, 2:, 1:-1] - v[:, 1:-1, :-2] - v[:, 1:-1, 2:]).mean((1, 2))
    return motion, lap, v.mean((1, 2))

def rank(series, a, b):
    n = b - a
    if n < 1 or len(series) <= n: return None
    win = np.convolve(series, np.ones(n) / n, 'valid')
    chosen = series[a:b].mean()
    return float((win < chosen).mean())

if __name__ == '__main__':
    root, eps, out = sys.argv[1], sys.argv[2].split(','), sys.argv[3]
    rows = []
    for ep in eps:
        d = json.load(open(f'docs/montage_harry/timelines/{ep}.json', encoding='utf-8'))
        s = final_seq(d)
        syncf = {i['file'] for t in s['audio'] for i in t}
        cache = {}
        for i in [i for t in s['video'] for i in t if is_rush(i['file']) and i['file'] not in syncf and i['in'] is not None]:
            p = next(iter(glob.glob(os.path.join(root, ep, '02 RUSHES*', i['file']))), None)
            if p is None: continue
            if p not in cache: cache[p] = profile(p)
            pr = cache[p]
            if pr is None: continue
            mo, la, lu = pr
            a, b = int(i['in'] * FPS), int(i['out'] * FPS)
            if b > len(mo): continue
            rows.append({'episode': ep, 'file': i['file'], 'in': i['in'], 'len': round(i['out'] - i['in'], 2),
                         'rush_len': round(len(mo) / FPS, 1), 'rang_mouvement': rank(mo, a, b),
                         'rang_nettete': rank(la, a, b), 'rang_lumiere': rank(lu, a, b)})
        print(ep, len(rows), flush=True)
    with open(out, 'w', newline='', encoding='utf-8-sig') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]), delimiter=';'); w.writeheader(); w.writerows(rows)
    for k in ('rang_mouvement', 'rang_nettete', 'rang_lumiere'):
        v = [r[k] for r in rows if r[k] is not None]
        print(k, 'médiane', round(float(np.median(v)), 2), ' part < 0.5 :', round(float(np.mean(np.array(v) < 0.5)), 2))
