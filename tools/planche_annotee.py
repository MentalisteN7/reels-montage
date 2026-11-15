"""Planche « plan par plan » d'un montage d'Harry : vignette + temps + piste + rush + type de son + mots dits.

python tools/planche_annotee.py <timeline.json> <export.mp4> <words.json> <sortie.jpg> [encodage_words]
"""
import sys, json, subprocess, os, io
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(__file__))
from analyse_timelines import final_seq, is_vo, is_rush, dur

W, H, CAP, COLS = 180, 320, 118, 8
font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 12)
bold = ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', 12)

def frame(video, t):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t:.3f}', '-i', video, '-frames:v', '1',
                          '-vf', f'scale={W}:{H}', '-f', 'image2pipe', '-vcodec', 'png', '-'], capture_output=True).stdout
    return Image.open(io.BytesIO(raw)).convert('RGB') if raw else Image.new('RGB', (W, H))

def wrap(txt, n=27):
    out, line = [], ''
    for w in txt.split():
        if len(line) + len(w) + 1 > n: out.append(line); line = w
        else: line = (line + ' ' + w).strip()
    return out + ([line] if line else [])

if __name__ == '__main__':
    tl, video, wj, out = sys.argv[1:5]
    enc = sys.argv[5] if len(sys.argv) > 5 else 'utf-8'
    s = final_seq(json.load(open(tl, encoding='utf-8')))
    words = [w for seg in json.load(open(wj, encoding=enc)) for w in seg['words']]
    T = dur(s)
    cuts = sorted({round(x, 2) for t in s['video'] for i in t for x in (i['t0'], i['t1']) if x <= T})
    cuts = [c for k, c in enumerate(cuts) if k == 0 or c - cuts[k - 1] > 0.05]
    shots = list(zip(cuts, cuts[1:]))
    rows = (len(shots) + COLS - 1) // COLS
    sheet = Image.new('RGB', (COLS * W, rows * (H + CAP)), 'white')
    d = ImageDraw.Draw(sheet)
    for k, (a, b) in enumerate(shots):
        m = (a + b) / 2
        x, y = (k % COLS) * W, (k // COLS) * (H + CAP)
        sheet.paste(frame(video, m), (x, y))
        # piste visible = la plus haute qui a un clip à m
        vis, lay = None, 0
        for li, t in enumerate(s['video']):
            for i in t:
                if i['t0'] <= m < i['t1']: vis, lay = i, li + 1
        aud = [i for t in s['audio'] for i in t if i['t0'] <= m < i['t1']]
        kind = 'VO' if any(is_vo(i['file']) for i in aud) else 'SYNC' if any(is_rush(i['file']) for i in aud) else '-'
        if kind == 'SYNC' and vis and not any(i['file'] == vis['file'] for i in aud): kind = 'SYNC+broll'
        said = ' '.join(w['w'].strip() for w in words if w['s'] < b and w['e'] > a)
        name = (vis['file'][-10:-4] if vis and is_rush(vis['file']) else (vis['file'][:12] if vis else '?'))
        d.text((x + 3, y + H + 2), f'{k + 1}. {a:.1f}-{b:.1f}s ({b - a:.2f})', font=bold, fill='black')
        d.text((x + 3, y + H + 17), f'V{lay} {name} @{vis["in"] if vis else 0:.1f}  {kind}', font=font,
               fill=(0, 90, 200) if kind == 'VO' else (200, 60, 0))
        for li, l in enumerate(wrap(said)[:5]):
            d.text((x + 3, y + H + 33 + li * 15), l, font=font, fill=(40, 40, 40))
    sheet.save(out, quality=82)
    print(out, len(shots), 'plans')
