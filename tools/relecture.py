"""Matériel de relecture d'un rendu, pour l'agent « relecteur » (.claude/agents/relecteur.md).

python tools/relecture.py <video_rendue.mp4> <edl.json> <dossier_sortie>

Produit dans <dossier_sortie> :
  - rendu.words.json   : transcription Whisper (par mot) de la vidéo RENDUE (ce que le spectateur entend)
  - controles.md       : contrôles automatiques
      * sous-titre affiché vs mots réellement entendus pendant son affichage (bug « pistaches »)
      * plans trop longs, plans trop courts, rythme de l'accroche
      * blancs audio (silence > 0,3 s dans le rendu)
  - planche_XX.jpg     : un plan = vignette au milieu du plan + temps + sous-titre affiché + mots entendus
"""
import os, sys, json, re, io, subprocess, unicodedata, difflib
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, CAP, COLS, ROWS = 180, 320, 104, 8, 5

NUM = {'0': 'zero', '1': 'un', '2': 'deux', '3': 'trois', '4': 'quatre', '5': 'cinq', '6': 'six', '7': 'sept', '8': 'huit',
       '9': 'neuf', '10': 'dix', '11': 'onze', '12': 'douze', '15': 'quinze', '20': 'vingt'}
def norm(s):
    s = unicodedata.normalize('NFD', s.lower().replace('-', ' ').replace("'", ' ').replace('’', ' '))
    s = re.sub(r'[^a-z0-9 ]', '', ''.join(c for c in s if unicodedata.category(c) != 'Mn'))
    return [NUM.get(t, t) for t in s.split()]

def transcribe(video, out):
    if os.path.exists(out): return json.load(open(out, encoding='utf-8'))
    from faster_whisper import WhisperModel
    pcm = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', video, '-f', 's16le', '-ac', '1', '-ar', '16000', '-'],
                                       capture_output=True).stdout, np.int16).astype(np.float32) / 32768
    m = WhisperModel('medium', device='cpu', compute_type='int8')
    segs, _ = m.transcribe(pcm, language='fr', word_timestamps=True, vad_filter=False)
    words = [{'w': w.word.strip(), 's': round(w.start, 2), 'e': round(w.end, 2)} for s in segs for w in s.words]
    json.dump(words, open(out, 'w', encoding='utf-8'), ensure_ascii=False)
    return words

def frame(video, t):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t:.3f}', '-i', video, '-frames:v', '1', '-vf', f'scale={W}:{H}',
                          '-f', 'image2pipe', '-vcodec', 'png', '-'], capture_output=True).stdout
    return Image.open(io.BytesIO(raw)).convert('RGB') if raw else Image.new('RGB', (W, H))

def wrap(t, n=26):
    out, line = [], ''
    for w in t.split():
        if len(line) + len(w) + 1 > n: out.append(line); line = w
        else: line = (line + ' ' + w).strip()
    return out + ([line] if line else [])

def silences(video):
    log = subprocess.run(['ffmpeg', '-hide_banner', '-i', video, '-af', 'silencedetect=n=-40dB:d=0.3', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', log)]
    du = [float(x) for x in re.findall(r'silence_duration: ([\d.]+)', log)]
    return list(zip(st, du))

if __name__ == '__main__':
    video, edl_path, out = sys.argv[1:4]
    os.makedirs(out, exist_ok=True)
    e = json.load(open(edl_path, encoding='utf-8'))
    words = transcribe(video, os.path.join(out, 'rendu.words.json'))
    heard = lambda a, b: [w for w in words if w['s'] < b and w['e'] > a]
    rep = ['# Contrôles automatiques', f'Vidéo : `{video}` ({e["duration"]} s)', '']

    # 1) sous-titres vs paroles entendues
    rep += ['## Sous-titres vs ce qu\'on entend', '| temps | sous-titre affiché | entendu (±0,4 s) | accord |', '|---|---|---|---|']
    bad = 0
    for s in e['subs']:
        shown = ' '.join(s['words'])
        h = ' '.join(w['w'] for w in heard(s['at'] - 0.4, s['end'] + 0.4))
        A, B = norm(shown), norm(h)
        found = sum(1 for a in A if any(difflib.SequenceMatcher(None, a, b).ratio() > 0.75 for b in B))
        score = found / max(1, len(A))
        if score < 0.7:
            bad += 1
            rep.append(f'| {s["at"]:.2f} | {shown} | {h or "(rien)"} | ⚠️ {score:.0%} |')
    rep.append(f'\n{bad} sous-titre(s) suspect(s) sur {len(e["subs"])} (Whisper se trompe aussi parfois : à vérifier en regardant).\n')

    # 2) rythme
    shots = sorted(e['video'], key=lambda v: v['at'])
    durs = [v['dur'] for v in shots]
    rep += ['## Rythme', f'- {len(shots)} plans, {e["duration"] / len(shots):.2f} s/plan (Harry : médiane 1,25)',
            f'- plans dans les 5 premières s : {sum(1 for v in shots if v["at"] < 5)} (Harry : 5–7)']
    longs = [v for v in shots if v['dur'] > 3.5]
    for v in longs: rep.append(f'- plan long : {v["at"]:.2f}s, {v["dur"]:.2f} s ({os.path.basename(v["src"])})')
    flash = [v for v in shots if v['dur'] < 0.3]
    for v in flash: rep.append(f'- plan flash : {v["at"]:.2f}s, {v["dur"]:.2f} s ({os.path.basename(v["src"])})')

    # 3) blancs audio
    sil = [(a, d) for a, d in silences(video) if a < e['duration'] - 0.5]
    rep += ['', '## Blancs audio (> 0,3 s sous -40 dB)'] + ([f'- {a:.2f} s : {d:.2f} s' for a, d in sil] or ['- aucun'])

    # 4) planches : un plan = vignette + sous-titre + entendu
    font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 12)
    bold = ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', 12)
    per = COLS * ROWS
    for p in range(0, len(shots), per):
        chunk = shots[p:p + per]
        sheet = Image.new('RGB', (COLS * W, ((len(chunk) + COLS - 1) // COLS) * (H + CAP)), 'white')
        d = ImageDraw.Draw(sheet)
        for k, v in enumerate(chunk):
            a, b = v['at'], v['at'] + v['dur']
            x, y = (k % COLS) * W, (k // COLS) * (H + CAP)
            sheet.paste(frame(video, (a + b) / 2), (x, y))
            sub = ' / '.join(' '.join(s['words']) for s in e['subs'] if s['at'] < b and s['end'] > a)
            h = ' '.join(w['w'] for w in heard(a, b))
            d.text((x + 3, y + H + 2), f'{p + k + 1}. {a:.1f}-{b:.1f}s ({b - a:.2f})', font=bold, fill='black')
            yy = y + H + 17
            for l in wrap('ST: ' + sub)[:3]: d.text((x + 3, yy), l, font=font, fill=(0, 90, 200)); yy += 14
            for l in wrap('ON: ' + h)[:3]: d.text((x + 3, yy), l, font=font, fill=(160, 40, 0)); yy += 14
        sheet.save(os.path.join(out, f'planche_{p // per + 1:02d}.jpg'), quality=82)
    open(os.path.join(out, 'controles.md'), 'w', encoding='utf-8').write('\n'.join(rep))
    print('\n'.join(rep[:3]), f'\n{bad} sous-titres suspects | planches dans {out}')
