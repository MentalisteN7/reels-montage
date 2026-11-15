"""Statistiques de montage d'Harry à partir des timelines Premiere extraites (tools/batch_prproj.py).

python tools/analyse_timelines.py docs/montage_harry/timelines docs/montage_harry/stats.csv
"""
import os, sys, json, glob, csv, statistics as st

def is_rush(f): return f.lower().endswith(('.mp4', '.mov')) and not f.lower().startswith(('pop', 'pov', 'click'))
def is_vo(f): return f.lower().endswith('.wav') and ('audio' in f.lower() or 'voix' in f.lower() or '_1.wav' in f)
def is_img(f): return f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')) or f == 'Image'

def final_seq(d):
    c = [s for s in d['sequences'] if 'rush' not in s['name'].lower() and 'derush' not in s['name'].lower()
         and 'copier' not in s['name'].lower()]
    c = [s for s in c if 15 < dur(s) < 200]
    return max(c, key=lambda s: sum(len(t) for t in s['video']), default=None)

def dur(s): return max([i['t1'] for t in s['video'] + s['audio'] for i in t] or [0])

def visible_shots(s):
    """Plans visibles = intervalles entre tous les points de coupe de toutes les pistes vidéo (piste haute visible)."""
    T = dur(s)
    cuts = sorted({round(x, 2) for t in s['video'] for i in t for x in (i['t0'], i['t1']) if x <= T})
    cuts = [c for k, c in enumerate(cuts) if k == 0 or c - cuts[k - 1] > 0.05]
    return [b - a for a, b in zip(cuts, cuts[1:])]

def analyse(d):
    s = final_seq(d)
    if s is None: return None
    T = dur(s)
    shots = visible_shots(s)
    v1 = s['video'][0] if s['video'] else []
    upper = [i for t in s['video'][1:] for i in t]
    aud = [i for t in s['audio'] for i in t]
    vo = [i for i in aud if is_vo(i['file'])]
    sync = [i for i in aud if is_rush(i['file'])]
    # VO : longueur des morceaux, blanc retiré entre deux morceaux consécutifs du même fichier
    vo = sorted(vo, key=lambda i: i['t0'])
    gaps = [b['in'] - a['out'] for a, b in zip(vo, vo[1:]) if a['file'] == b['file'] and 0 <= b['in'] - a['out'] < 3]
    # son direct (interviews / Harry face cam) : longueur des prises
    sync_len = [i['t1'] - i['t0'] for i in sync]
    # B-roll posé au-dessus du son direct (V2+) pendant que le son direct continue
    broll_over = [i['t1'] - i['t0'] for i in upper if is_rush(i['file'])
                  and any(a['t0'] - 0.05 <= i['t0'] and i['t1'] <= a['t1'] + 0.05 for a in sync)]
    sync_time = sum(sync_len) or 0
    covered = sum(broll_over)
    # prises V1 en son direct : durée totale visible de la même prise (sync)
    vids = [i for i in v1 if is_rush(i['file'])]
    inpos = [i['in'] for i in vids if i['in'] is not None]
    # coupes vidéo alignées sur les coupes VO
    vo_cuts = {round(x, 1) for i in vo for x in (i['t0'], i['t1'])}
    vcuts = [i['t0'] for i in v1][1:]
    aligned = sum(1 for c in vcuts if any(abs(c - x) < 0.07 for x in vo_cuts)) / max(1, len(vcuts))
    hook = sum(1 for k in range(len(shots)) if sum(shots[:k]) < 3)
    imgs = [i for t in s['video'] for i in t if is_img(i['file'])]
    files = {i['file'] for i in vids}
    return {
        'episode': d['episode'], 'seq': s['name'], 'duree': round(T, 1), 'plans': len(shots),
        's_par_plan': round(T / max(1, len(shots)), 2), 'mediane_plan': round(st.median(shots), 2) if shots else 0,
        'plans_3s': hook, 'nb_rushes_utilises': len(files),
        'vo_morceaux': len(vo), 'vo_moy': round(st.mean([i['t1'] - i['t0'] for i in vo]), 2) if vo else 0,
        'vo_blanc_retire_med': round(st.median(gaps), 2) if gaps else '',
        'vo_part': round(sum(i['t1'] - i['t0'] for i in vo) / T, 2),
        'sync_prises': len(sync), 'sync_moy': round(st.mean(sync_len), 2) if sync_len else 0,
        'sync_part': round(sync_time / T, 2),
        'broll_sur_sync_nb': len(broll_over), 'broll_sur_sync_moy': round(st.mean(broll_over), 2) if broll_over else 0,
        'sync_couvert_par_broll': round(covered / sync_time, 2) if sync_time else 0,
        'in_point_med': round(st.median(inpos), 2) if inpos else 0,
        'coupes_alignees_vo': round(aligned, 2), 'images': len(imgs),
        'vitesse_modifiee': sum(1 for t in s['video'] for i in t if abs(i['speed'] - 1) > 0.01),
        'pistes_video': len([t for t in s['video'] if t]),
    }

if __name__ == '__main__':
    rows = [r for f in sorted(glob.glob(os.path.join(sys.argv[1], '*.json')))
            if (r := analyse(json.load(open(f, encoding='utf-8'))))]
    with open(sys.argv[2], 'w', newline='', encoding='utf-8-sig') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]), delimiter=';'); w.writeheader(); w.writerows(rows)
    keys = [k for k in rows[0] if k not in ('episode', 'seq')]
    print(len(rows), 'épisodes')
    for k in keys:
        v = [r[k] for r in rows if r[k] != '']
        print(f'{k:24s} médiane {st.median(v):7.2f}   min {min(v):7.2f}   max {max(v):7.2f}')
