"""Mesure, sur les montages Premiere d'Harry, combien de silence il garde à chaque coupe audio.

Pour chaque morceau audio de la séquence finale (voix off ou son direct d'un rush) :
  lead = temps entre le point d'entrée et le début de la parole (0 = coupe dans la parole)
  tail = temps entre la fin de la parole et le point de sortie
  pause = tail(morceau précédent) + lead(morceau suivant) aux raccords VO->VO / sync->sync
python tools/cut_margins.py <Guest-Lunch> docs/montage_harry/timelines docs/montage_harry/marges.csv
"""
import os, sys, json, glob, csv, subprocess
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from analyse_timelines import final_seq, is_vo, is_rush

SR = 16000; HOP = 0.01; PAD = 0.6

def env(path, t0, t1):
    t0 = max(0, t0)
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t0:.3f}', '-t', f'{t1 - t0:.3f}', '-i', path,
                          '-vn', '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout
    x = np.frombuffer(raw, dtype=np.float32)
    h = int(HOP * SR); n = len(x) // h
    if n == 0: return None, t0
    e = 20 * np.log10(np.sqrt((x[:n * h].reshape(n, h) ** 2).mean(1)) + 1e-9)
    return e, t0

def find(root, ep, f):
    for sub in ('01 PROJET/Adobe Premiere Pro Captured and Generated/*', '02 RUSHES*', '03 MUSIQUE', '01 PROJET'):
        for d in glob.glob(os.path.join(root, ep, sub)):
            p = os.path.join(d, f)
            if os.path.exists(p): return p
    return None

def margins(path, a, b):
    e, t0 = env(path, a - PAD, b + PAD)
    if e is None: return None
    i0 = int(round((a - t0) / HOP)); i1 = int(round((b - t0) / HOP))
    clip = e[i0:i1]
    if len(clip) < 10: return None
    lvl = np.percentile(clip, 95); floor = np.percentile(e, 10)
    thr = max(lvl - 24, floor + 8)
    on = np.where(clip > thr)[0]
    if len(on) == 0: return None
    lead = on[0] * HOP; tail = (len(clip) - 1 - on[-1]) * HOP
    # la parole continuait-elle juste avant / après la coupe dans le rush ? (coupe dans un mot)
    before = e[max(0, i0 - 3):i0]; after = e[i1:i1 + 3]
    return lead, tail, bool(len(before) and before.max() > thr), bool(len(after) and after.max() > thr), lvl - floor

if __name__ == '__main__':
    root, tdir, out = sys.argv[1:4]
    rows = []
    for f in sorted(glob.glob(os.path.join(tdir, '*.json'))):
        d = json.load(open(f, encoding='utf-8')); s = final_seq(d)
        if s is None: continue
        prev = None
        for i in sorted([i for t in s['audio'] for i in t], key=lambda i: i['t0']):
            kind = 'vo' if is_vo(i['file']) else 'sync' if is_rush(i['file']) else None
            if kind is None or i['in'] is None: continue
            p = find(root, d['episode'], i['file'])
            if p is None: continue
            m = margins(p, i['in'], i['out'])
            if m is None: continue
            lead, tail, cut_in, cut_out, snr = m
            joint = prev is not None and abs(prev['t1'] - i['t0']) < 0.04 and prev['kind'] == kind
            rows.append({'episode': d['episode'], 'kind': kind, 'file': i['file'], 't0': i['t0'], 'len': round(i['t1'] - i['t0'], 2),
                         'lead': round(lead, 2), 'tail': round(tail, 2), 'coupe_dans_mot_debut': cut_in,
                         'coupe_dans_mot_fin': cut_out, 'snr_db': round(float(snr), 1),
                         'pause_raccord': round(prev['tail'] + lead, 2) if joint else ''})
            prev = {'t1': i['t1'], 'kind': kind, 'tail': tail}
        print(d['episode'], len(rows), flush=True)
    with open(out, 'w', newline='', encoding='utf-8-sig') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]), delimiter=';'); w.writeheader(); w.writerows(rows)
