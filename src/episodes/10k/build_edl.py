"""Annonce soirée 10K — liste de montage (EDL) -> edl.json lu par la composition Remotion.
Secondes partout. Rushes = proxies 30 fps (public/rushes/10k/), son direct (micro-cravate) de Harry face cam.
Pas de voix off séparée : chaque phrase est un rush face cam ; on coupe les blancs entre les phrases.
Musique épique libre de droits (Mixkit « I Won't Surrender ») : forte sur l'intro et le récap, basse sous la parole.
Usage : python src/episodes/10k/build_edl.py
"""
import json, os, re, sys, unicodedata, difflib, subprocess
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'tools'))

FPS = 30
SRC_DIR = r'D:\Harrison\Influencer\Guest-Lunch\10k_annonce'
MUSIC = os.path.join(SRC_DIR, '03 MUSIQUE', 'mixkit_846.mp3')   # Mixkit « I Won't Surrender » (Michael Ramir C.), licence Mixkit

def R(i): return f'rushes/10k/20261121_{i}.mp4'
def FL(n): return f'rushes/10k/flash/{n}.mp4'          # extraits des Reels finis d'Harry (sans son)

def words_of(i):
    w = []
    for s in json.load(open(os.path.join(HERE, 'words', f'20261121_{i}.words.json'), encoding='utf-8')):
        w += [{'w': x['w'].strip(), 's': x['s'], 'e': x['e']} for x in s['words']]
    return w

T = 0.0
audio, video, subs, overlays, sfx, cuts = [], [], [], [], [], []
SPEECH = []      # zones de parole sur la timeline (pour baisser la musique)

def norm(s):
    s = unicodedata.normalize('NFD', s.lower())
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return re.sub(r"[^a-z0-9]", '', s)

def to_tl(table, t):
    for a, b, at in table:
        if t < a: return at
        if t <= b: return at + (t - a)
    a, b, at = table[-1]
    return at + (b - a)

def add_subs(spec, wlist, t0, t1, table):
    """spec : « *Jeudi* 10 décembre | soirée ... » — timing = mots Whisper alignés (difflib), interpolés sinon."""
    chunks = [c.strip() for c in spec.split('|') if c.strip()]
    toks, owner = [], []
    for ci, c in enumerate(chunks):
        for t in c.split():
            toks.append(t); owner.append(ci)
    ws = [w for w in wlist if t0 - 0.05 <= w['s'] <= t1 + 0.05]
    A = [norm(t.replace('*', '')) for t in toks]
    B = [norm(w['w']) for w in ws]
    times = [None] * len(toks)
    for blk in difflib.SequenceMatcher(None, A, B, autojunk=False).get_matching_blocks():
        for k in range(blk.size):
            times[blk.a + k] = ws[blk.b + k]['s']
    known = [(i, t) for i, t in enumerate(times) if t is not None]
    for i in range(len(times)):
        if times[i] is None:
            prev = max((k for k in known if k[0] < i), key=lambda k: k[0], default=(-1, t0))
            nxt = min((k for k in known if k[0] > i), key=lambda k: k[0], default=(len(times), t1))
            times[i] = prev[1] + (nxt[1] - prev[1]) * (i - prev[0]) / max(1, nxt[0] - prev[0])
    end_tl = to_tl(table, t1)
    starts = [to_tl(table, times[owner.index(ci)]) for ci in range(len(chunks))]
    starts[0] = min(starts[0], to_tl(table, t0))
    for ci, c in enumerate(chunks):
        body = c.split()
        hl, inside = [], False
        for k, t in enumerate(body):
            if t.startswith('*'): inside = True
            if inside: hl.append(k)
            if t.rstrip('!?.,').endswith('*'): inside = False
        body = [t.replace('*', '') for t in body]
        body[0] = body[0][:1].upper() + body[0][1:]      # Harry v8 : chaque sous-titre commence par une majuscule
        at = starts[ci]
        end = starts[ci + 1] if ci + 1 < len(chunks) else end_tl
        subs.append({'words': body, 'hl': hl, 'emoji': '', 'at': round(at, 3), 'end': round(max(end, at + 0.15), 3)})
    return [(norm(toks[i].replace('*', '')), to_tl(table, times[i])) for i in range(len(toks))]

def word_at(timed, w, after=-1.0):
    k = norm(w)
    r = [t for x, t in timed if k[:6] in x and t > after]
    if not r: print('  ! ancre introuvable :', w)
    return r[0] if r else after

def subtract(segs, holes):
    """segs [(a, b, src, in)] moins les intervalles holes [(a, b)] (B-roll par-dessus)."""
    out = []
    for a, b, src, sin in segs:
        parts = [(a, b)]
        for ha, hb in holes:
            nxt = []
            for x, y in parts:
                if hb <= x or ha >= y: nxt.append((x, y)); continue
                if ha > x: nxt.append((x, ha))
                if hb < y: nxt.append((hb, y))
            parts = nxt
        for x, y in parts:
            if y - x > 0.02: out.append((x, y, src, sin + (x - a)))
    return out

def say(rush, ranges, spec, broll=(), vol=1.0, vshift=None):
    """Une phrase face cam : morceaux [t0, t1] du rush posés bout à bout (blancs entre morceaux supprimés),
    image synchrone, puis B-roll par-dessus : broll = [(mot, src, in, durée)] (le plan démarre ~sur le mot).
    vshift = (décalage, jusqu'à t_source) : Harry (v4) « on me voit attendre le signal pour démarrer » -> tant qu'il est
    loin (lèvres illisibles), l'image est prise PLUS LOIN dans le rush (quand il marche déjà) ; la synchro reprend après t_source."""
    global T
    wl = words_of(rush)
    seg0 = T
    table, base = [], []
    for k, (a, b) in enumerate(ranges):
        audio.append({'src': R(rush), 'in': round(a, 3), 'out': round(b, 3), 'at': round(T, 3), 'vol': vol})
        table.append((a, b, T))
        if vshift and a < vshift[1]:
            m = min(b, vshift[1])
            base.append((T, T + m - a, R(rush), a + vshift[0]))
            if b > m: base.append((T + m - a, T + b - a, R(rush), m))
        else:
            base.append((T, T + b - a, R(rush), a))
        if k: cuts.append(T)
        T += b - a
    SPEECH.append((seg0, T))
    timed = add_subs(spec, wl, ranges[0][0], ranges[-1][1], table)
    holes, placed = [], []
    for w, src, sin, dur in broll:
        a = max(seg0, word_at(timed, w) - 0.05) if isinstance(w, str) else seg0 + w
        b = min(T, a + dur)
        placed.append([a, b, src, sin])
    placed.sort()
    for p, q in zip(placed, placed[1:]):          # pas de chevauchement, pas de micro-plan (< 0,4 s) entre deux B-rolls
        if q[0] - p[1] < 0.4: p[1] = q[0]
    if placed and T - placed[-1][1] < 0.4: placed[-1][1] = T
    holes = [(a, b) for a, b, _, _ in placed]
    for a, b, src, sin in subtract(base, holes) + placed:
        video.append({'src': src, 'in': round(sin, 3), 'at': round(a, 3), 'dur': round(b - a, 3)})
    return seg0, T, timed

POP = 'sfx/pop_harry.wav'
MONEY = 'sfx/kaching.wav'       # Harry v10 : Pixabay « Cashier ka-ching » (u_byub5wd934, n°129698), blanc de début retiré
def drop_sub(text):
    """Harry v7 : quand une popup en haut affiche l'info, pas de sous-titre qui la répète."""
    n = len(subs)
    subs[:] = [x for x in subs if ' '.join(x['words']) != text]
    if len(subs) == n: print('  ! sous-titre à retirer introuvable :', text)
def card(at, dur, lines, kind='info', pop=True, **kw):
    overlays.append({'type': 'card', 'kind': kind, 'at': round(at, 3), 'dur': round(dur, 3), 'lines': lines, **kw})
    if pop: sfx.append({'src': POP, 'at': round(at, 3), 'vol': 1.0})

# ================================================================ MONTAGE
# Harry (v2) : les rushes dans l'ORDRE DE TOURNAGE (date -> présentation -> lieu -> tirage -> agenda).
# 2 versions : A ouvre sur « Jeudi 10 décembre, soirée exceptionnelle », B sur « Moi c'est Harry, l'influenceur en carton ».
VERSION = 'B' if '--B' in sys.argv else 'A'
PAPER = 'sfx/paper.mp3'

def scene_date():
    """Face cam devant la place ; « lieu exceptionnel » = la place qui se révèle (le téléphone se relève)."""
    s0, s1, tm = say('153142', [(3.15, 6.42)],
        "*Jeudi 10 décembre* | soirée *exceptionnelle* | dans un lieu | *exceptionnel*")   # Harry v4 : pas de plan qui se relève
    card(s0 + 0.1, word_at(tm, 'lieu') - s0 - 0.15, ['Jeudi 10 décembre', '19h30'], kind='date', bg='blanc')   # Harry v8 : celle-ci en blanc plein
    drop_sub('Jeudi 10 décembre')

def scene_harry():
    """Harry marche vers la caméra ; sur « une soirée pour fêter mes 10 000 abonnés » : la page Insta,
    le compteur monte et touche 10 000 sur le mot « 10 000 » (Harry v2 : pas de flash de Reels ici)."""
    s0, s1, tm = say('153558', [(1.0, 6.1)],
        "Moi c'est *Harry* | *l'influenceur* en *carton* | et j'organise | *officiellement* | une *soirée* | pour fêter | mes *10 000 abonnés*",
        vshift=(0.33, 6.1))      # il part à 1,33 s ; loin, lèvres illisibles ; la page Insta couvre la fin
    nk = word_at(tm, 'influenceur') - 0.05
    overlays.append({'type': 'nickname', 'at': round(nk, 3), 'dur': round(min(2.0, word_at(tm, 'organise') - 0.15 - nk), 3), 'lines': ["L'influenceur", 'en carton'], 'in': 'slide', 'out': 'rise'})
    i0 = word_at(tm, 'organise') - 0.15          # Harry v7 : un vélo entre dans le cadre sur « officiellement » -> compteur plus tôt
    hit = word_at(tm, '10')
    overlays.append({'type': 'insta', 'at': round(i0, 3), 'dur': round(s1 - i0, 3), 'hit': round(hit - i0, 3)})
    sfx.append({'src': 'sfx/ding.mp3', 'at': round(hit, 3), 'vol': 1.0})

def scene_lieu():
    """Plan large devant l'Annexe, façade, terrasse, Harry qui boit ; « 10 € » tamponné."""
    s0, s1, tm = say('154131', [(3.3, 8.3)],
        "*L'Annexe Saint-Georges* | nous ouvre ses portes | il y aura *tapas* | *boissons maison* | et tout ça | pour *10 €*",
        broll=[('ses', FL('annexe_st_georges'), 4.0, 0.75), ('aura', FL('annexe_st_georges'), 5.0, 0.8),
               ('boissons', FL('harry_boisson'), 0.0, 1.0)])     # Harry v2 : pas Antho -> Harry qui boit (Annexe, avril 2025)
    # Harry v7 : on garde les popups en haut (lieu, tapas, 10 €) et on RETIRE les sous-titres qui disent la même chose
    card(s0 + 0.1, word_at(tm, 'aura') - s0 - 0.2, ["L'Annexe", 'Saint-Georges'], kind='place')   # reste jusqu'à la popup tapas (plus de sous-titre)
    card(word_at(tm, 'aura') - 0.05, word_at(tm, 'tout') - word_at(tm, 'aura'), ['Tapas', '+ boissons maison'], pop=False)
    card(word_at(tm, 'pour') - 0.05, s1 - word_at(tm, 'pour') + 0.1, ['10 €'], kind='price', pop=False)
    sfx.append({'src': MONEY, 'at': round(word_at(tm, 'pour') - 0.05, 3), 'vol': 0.9})   # Harry v8 : bruit d'argent au lieu du pop
    # Harry v8 : sous-titres remis partout (seul « Jeudi 10 décembre » reste retiré)

def scene_tirage():
    s0, s1, tm = say('154822', [(11.70, 15.66)],
        "Un *tirage au sort* | aura également lieu | pour gagner | des *restos gratuits* | et plein | de *lots différents*",
        broll=[('restos', FL('nachos_balma'), 0.0, 0.8)])
    card(s0 + 0.1, word_at(tm, 'restos') - s0 - 0.15, ['Jeu concours', 'lien en bio'], kind='info', pop=False)

def scene_agenda():
    """« Tu peux venir seul… » ; sur « note vite ça dans ton agenda » : calendrier, le jeudi 10 se fait entourer."""
    s0, s1, tm = say('155426', [(0.72, 4.36), (4.70, 7.2)],
        "Tu peux venir *seul* | en *couple* | ou entre *amis* | t'es le *bienvenu* | mon *copaign* ! | Alors *note vite ça* | dans ton *agenda* | et on se dit | à *très vite* !",
        # relecture v4 : lèvres lisibles dès ~18,1 s -> B-roll dès « seul » (homme seul + assiette), « couple » (duo sur la place), « amis » (2 amies)
        # Harry v5 : le gars à la casquette = Antho, et le duo n'est pas un couple -> « seul » = la fille qui mange seule,
        # « couple » = plan large neutre de la place, « amis » = 2 amies attablées
        broll=[(0.74, FL('annexe_st_georges_2'), 0.92, 0.72), ('couple', FL('annexe_st_georges_2'), 6.5, 0.65),
               ('amis', FL('annexe_st_georges_2'), 5.05, 0.8)],
        vshift=(1.48, 1.46))     # orthographe voulue « copaign » (comme « toulousaign »)
    c0 = word_at(tm, 'note') - 0.1
    ca = word_at(tm, 'agenda') - c0
    # relecture v3 : le calendrier sort juste après le cercle (sinon il finit sur les yeux d'Harry qui avance)
    overlays.append({'type': 'calendar', 'at': round(c0, 3), 'dur': round(ca + 0.8, 3), 'circle': round(ca, 3)})
    sfx.append({'src': PAPER, 'at': round(c0, 3), 'vol': 1.0})

LEAD = 0.15          # le récap arrive sur « à très vite » (fin du rush 155426 = visage qui sort du cadre)
ORDER = [scene_date, scene_harry] if VERSION == 'A' else [scene_harry, scene_date]
for sc in ORDER + [scene_lieu, scene_tirage, scene_agenda]:
    sc()
INTRO = 0.0
RECAP = 3.4
overlays.append({'type': 'recap', 'at': round(T - LEAD, 3), 'dur': RECAP + LEAD})
sfx.append({'src': POP, 'at': round(T - LEAD, 3), 'vol': 1.0})
T += RECAP

# ------------------------------------------------------------------ musique : forte (intro, récap), basse sous la parole
def music_bed(duration, out):
    SR = 48000
    x = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', MUSIC, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'],
                                     capture_output=True, check=True).stdout, np.float32).astype(np.float64)
    n = int(duration * SR); x = x[:n]
    t = np.arange(n) / SR
    HI, LO, RAMP = 1.5, 0.42, 0.25
    env = np.full(n, HI)
    for a, b in SPEECH:
        env[(t >= a) & (t < b)] = LO
    k = int(RAMP * SR)                                   # rampes douces entre les niveaux
    env = np.convolve(env, np.ones(k) / k, mode='same')
    fade = int(0.8 * SR); env[-fade:] *= np.linspace(1, 0, fade)
    y = (x * env).astype(np.float32)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', out],
                   input=y.tobytes(), check=True)

# ------------------------------------------------------------------ contrôles
MIN_SUB = 0.32
subs.sort(key=lambda x: x['at'])
for x, y in zip(subs, subs[1:]):
    if y['at'] - x['at'] < MIN_SUB and y['end'] - (x['at'] + MIN_SUB) >= MIN_SUB:
        y['at'] = round(x['at'] + MIN_SUB, 3)
    x['end'] = min(x['end'], y['at'])
video.sort(key=lambda v: v['at'])
au = sorted(audio, key=lambda a: a['at'])
gaps = [(round(x['at'], 2), round(y['at'] - x['at'] - x['out'] + x['in'], 3)) for x, y in zip(au, au[1:])
        if y['at'] - (x['at'] + x['out'] - x['in']) > 0.02]
holes = [(round(x['at'] + x['dur'], 2), round(y['at'] - x['at'] - x['dur'], 3)) for x, y in zip(video, video[1:])
         if abs(y['at'] - x['at'] - x['dur']) > 0.02]
long_sub = [' '.join(s['words']) for s in subs if len(s['words']) > 4]
os.makedirs(os.path.join(ROOT, 'public', 'sfx'), exist_ok=True)
music_bed(T, os.path.join(ROOT, 'public', 'sfx', f'music_10k_bed_{VERSION}.wav'))
sfx.insert(0, {'src': f'sfx/music_10k_bed_{VERSION}.wav', 'at': 0, 'vol': 1.0})
edl = {'fps': FPS, 'duration': round(T, 3), 'audio': audio, 'video': video, 'subs': subs, 'overlays': overlays, 'sfx': sfx}
from mixdown import mixdown
# Harry (v2) : « je n'articule pas si bien » -> voix clarifiée (on ne change pas l'articulation, mais la parole est plus nette) :
# coupe des graves, réduction de bruit légère, creux à 200 Hz, présence +4 dB à 3,2 kHz, compression douce. --brut = son d'origine
CLARITY = 'highpass=f=90,afftdn=nr=8:nf=-32,equalizer=f=200:t=q:w=1:g=-2,equalizer=f=3200:t=q:w=1.4:g=4,equalizer=f=6500:t=q:w=1:g=1.5,acompressor=threshold=-22dB:ratio=2.5:attack=5:release=90:makeup=2'
ENH = os.path.join(ROOT, 'public', 'vo', '10k_clair')
def enhanced(orig):
    os.makedirs(ENH, exist_ok=True)
    out = os.path.join(ENH, os.path.basename(orig).replace('.mp4', '.wav'))
    if not os.path.exists(out):
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', orig, '-vn', '-ac', '1', '-ar', '48000', '-af', CLARITY, out], check=True)
    return out
def resolve(src):
    o = os.path.join(SRC_DIR, '02 RUSHES', os.path.basename(src))      # rush original (pas le proxy)
    if src.startswith('rushes/10k/2026') and os.path.exists(o):
        return o if '--brut' in sys.argv else enhanced(o)
    return os.path.join(ROOT, 'public', src)
if '--no-mix' not in sys.argv:
    g, L = mixdown(audio, sfx, T, os.path.join(ROOT, 'public', 'mix', f'10k_{VERSION}.wav'), resolve)
    print('mix :', L, 'LUFS | gains par source (dB) :', g)
edl['mix'] = f'mix/10k_{VERSION}.wav'
json.dump(edl, open(os.path.join(HERE, f'edl_{VERSION}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
nv = len([v for v in video])
print(f'{T:.1f} s | {nv} plans | {(T - INTRO) / nv:.2f} s/plan (hors intro) | {len(subs)} sous-titres | {len(audio)} morceaux audio')
print('blancs audio > 20 ms (hors intro) :', gaps or 'aucun')
print('trous/chevauchements video :', holes or 'aucun')
print('sous-titres > 4 mots :', long_sub or 'aucun')
for v in video: print(f"  {v['at']:6.2f} +{v['dur']:.2f}  {v['src'].split('/')[-1]} @{v['in']}")
