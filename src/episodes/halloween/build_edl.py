"""Halloween au Mercure Compans (Buricot) — liste de montage (EDL) -> edl.json lu par la composition Remotion.
Secondes partout. Rushes = proxies 30 fps à vitesse réelle (temps source = temps du rush).

Règles de dynamisme (DA §8) appliquées automatiquement :
  - zones de parole détectées à l'énergie (tools/speech_regions.py) ; tout silence entre deux zones est COUPÉ
  - zones sans aucun mot reconnu par Whisper (« euh », souffle) = supprimées
  - chaque fin de zone (= fin de phrase / groupe) raccourcie de TRIM (≈ 1,5 image)
  - interviews : chaque coupe interne est cachée par un B-roll (plat, bouchée)
Sous-titres (DA §6bis) : découpe MANUELLE avec « | » (≤ 4 mots, 1 ligne, cohérente), *mot* = jaune, {emoji} = ligne à part
Usage : python src/episodes/halloween/build_edl.py
"""
import json, os, re, sys, unicodedata, difflib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from speech_regions import speech_regions

FPS = 30
TRIM = 0.07          # fin de phrase raccourcie (~2 images) — v3 : plus serré (0,09 mangeait « neuf », « dix »)
PAD_IN = 0.0         # attaque prise au ras (v3) ; négatif = mange les « Et » d'attaque
IV_DMIN = 0.15       # interviews : on ne coupe que les pauses >= 0,2 s (en dessous = respiration naturelle)
EMOJI_UNTIL = 5.0
VO = 'vo/halloween_vo.wav'

def R(i):
    return f'rushes/halloween/20261030_{i}.mp4'

_cache = {}
def regions(src, noise, dmin=0.12):
    k = (src, noise, dmin)
    if k not in _cache: _cache[k] = speech_regions(os.path.join(ROOT, 'public', src), noise, dmin)
    return _cache[k]

def words_of(name):
    w = []
    for s in json.load(open(os.path.join(HERE, 'words', name + '.words.json'), encoding='utf-8')):
        w += [{'w': x['w'].strip(), 's': x['s'], 'e': x['e']} for x in s['words']]
    return w

T = 0.0
audio, video, subs, overlays, sfx, cuts = [], [], [], [], [], []

# ------------------------------------------------------------------ découpe audio
def pieces(src, noise, wlist, t0, t1, dmin=0.12, trim=None, keep_all=False, merge=0.04, pad_in=PAD_IN):
    """Morceaux de parole utiles dans [t0, t1] : zones d'énergie contenant au moins un mot ; silences et « euh » retirés."""
    ws = [w for w in wlist if t0 - 0.05 <= w['s'] <= t1]
    out = []
    for a, b in regions(src, noise, dmin):
        a2, b2 = max(a, t0), min(b, t1)
        if b2 - a2 < 0.06: continue
        if not keep_all and not any(a2 - 0.10 <= w['s'] <= b2 for w in ws): continue   # aucun mot -> « euh » / bruit
        a2 = max(t0, a2 - pad_in) if a2 > t0 else t0
        b2 = b2 - (TRIM if trim is None else trim) if b2 < t1 else t1
        b2 = min(b2, t1)
        if out and a2 - out[-1][1] < merge: out[-1][1] = max(out[-1][1], b2)
        else: out.append([a2, b2])
    return out

def place(src, ps, vol=1.0):
    """Pose les morceaux bout à bout à partir de T (aucun blanc). Retourne la table source->timeline."""
    global T
    table = []
    for k, (a, b) in enumerate(ps):
        audio.append({'src': src, 'in': round(a, 3), 'out': round(b, 3), 'at': round(T, 3), 'vol': vol})
        table.append((a, b, T))
        if k: cuts.append(T)
        T += b - a
    return table

def to_tl(table, t):
    """Temps source -> timeline (un temps tombé dans une coupe est ramené au morceau suivant)."""
    for a, b, at in table:
        if t < a: return at
        if t <= b: return at + (t - a)
    a, b, at = table[-1]
    return at + (b - a)

# ------------------------------------------------------------------ sous-titres
def norm(s):
    s = unicodedata.normalize('NFD', s.lower())
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return re.sub(r"[^a-z0-9]", '', s)

def add_subs(spec, wlist, t0, t1, table):
    """spec : « Les meilleures *pizzas* | de *Toulouse* {🍕} | ... ». Timing = mots Whisper alignés (difflib)."""
    chunks = [c.strip() for c in spec.split('|') if c.strip()]
    toks, owner = [], []
    for ci, c in enumerate(chunks):
        for t in re.sub(r'\{[^}]*\}', '', c).split():
            toks.append(t); owner.append(ci)
    ws = [w for w in wlist if t0 - 0.05 <= w['s'] <= t1 + 0.05]
    A = [norm(t.replace('*', '')) for t in toks]
    B = [norm(w['w']) for w in ws]
    times = [None] * len(toks)
    for blk in difflib.SequenceMatcher(None, A, B, autojunk=False).get_matching_blocks():
        for k in range(blk.size):
            times[blk.a + k] = ws[blk.b + k]['s']
    known = [(i, t) for i, t in enumerate(times) if t is not None]
    for i in range(len(times)):          # interpolation des mots non retrouvés
        if times[i] is None:
            prev = max((k for k in known if k[0] < i), key=lambda k: k[0], default=(-1, t0))
            nxt = min((k for k in known if k[0] > i), key=lambda k: k[0], default=(len(times), t1))
            times[i] = prev[1] + (nxt[1] - prev[1]) * (i - prev[0]) / max(1, nxt[0] - prev[0])
    end_tl = to_tl(table, t1)
    starts = [to_tl(table, times[owner.index(ci)]) for ci in range(len(chunks))]
    starts[0] = min(starts[0], to_tl(table, t0) + 0.0)
    for ci, c in enumerate(chunks):
        emo = ''.join(re.findall(r'\{([^}]*)\}', c))
        body = re.sub(r'\{[^}]*\}', '', c).split()
        hl, inside = [], False                     # *un mot* ou *plusieurs mots* = jaune
        for k, t in enumerate(body):
            if t.startswith('*'): inside = True
            if inside: hl.append(k)
            if t.rstrip('!?.,').endswith('*'): inside = False
        body = [t.replace('*', '') for t in body]
        at = starts[ci]
        end = starts[ci + 1] if ci + 1 < len(chunks) else end_tl
        if end - at < 0.15: end = at + 0.15
        subs.append({'words': body, 'hl': hl, 'emoji': emo if at < EMOJI_UNTIL else '',
                     'at': round(at, 3), 'end': round(end, 3)})
    return [(norm(toks[i].replace('*', '')), to_tl(table, times[i])) for i in range(len(toks))]


# ------------------------------------------------------------------ helpers
VO_WORDS = words_of('vo')

NICK_DUR = 2.7
NICK_ANIMS = [('slide', 'slide'), ('rise', 'rise'), ('type', 'blur'), ('wipe', 'drop'), ('zoom', 'shrink')]
def nickname(at, lines, until=None):
    k = sum(1 for o in overlays if o['type'] == 'nickname')
    a_in, a_out = NICK_ANIMS[k % len(NICK_ANIMS)]
    overlays.append({'type': 'nickname', 'at': round(at, 3), 'dur': round(min(NICK_DUR, (until or 1e9) - at), 3), 'lines': lines, 'in': a_in, 'out': a_out})

VO2 = 'vo/halloween_vo2.wav'       # v4 : réenregistrement « le vampire en carton » (Audio 1_1.wav)
VO2_WORDS = words_of('vo2')

def vo(t0, t1, spec, shots=None, src=None):
    """Une phrase de VO (prise [t0, t1]), silences internes coupés, enchaînée sans blanc. Retourne (début, fin, mots datés)."""
    src = src or VO
    W = VO2_WORDS if src == VO2 else VO_WORDS
    for a, b in regions(src, -40):     # v6 : t0 (début Whisper) tombe 50–110 ms après l'attaque -> recaler sur le vrai début de parole
        if a < t0 <= b and t0 - a < 0.2: t0 = max(0.0, a - 0.02); break
    seg0 = T
    last = max((w['e'] for w in W if t0 - 0.05 <= w['s'] <= t1), default=t1)
    nxt = min((w['s'] for w in W if w['s'] > last - 0.01), default=1e9)
    t1 = max(t1, min(last + 0.08, nxt - 0.03))
    table = place(src, pieces(src, -40, W, t0, t1, trim=-0.04, keep_all=True, merge=0.06, pad_in=0.03))   # les prises ratées sont déjà exclues par [t0, t1]
    timed = add_subs(spec, W, t0, t1, table)
    if shots: anchored(seg0, T, timed, shots)
    return seg0, T, timed

def word_at(timed, w, after=-1.0):
    k = norm(w)
    r = [t for x, t in timed if k[:6] in x and t > after]
    if not r: print('  ! ancre introuvable / dépassée :', w)
    return r[0] if r else after

def anchored(seg0, seg1, timed, items):
    """items = [(ancre, rush, in)] : ancre = mot (le plan démarre sur ce mot) ou nombre (s après le début du plan précédent)."""
    starts, prev = [], seg0
    for k, (anc, rush, src_in) in enumerate(items):
        if k == 0: t = seg0
        elif isinstance(anc, str): t = max(prev + 0.35, word_at(timed, anc, prev) - 0.05)
        else: t = prev + anc
        starts.append(min(t, seg1)); prev = t
    MIN_SHOT = 0.4     # pas de plan flash : un plan trop court est absorbé par le précédent
    keep = list(range(len(items)))
    changed = True
    while changed:
        changed = False
        for j, k in enumerate(keep[1:], 1):
            nxt = starts[keep[j + 1]] if j + 1 < len(keep) else seg1
            if nxt - starts[k] < MIN_SHOT:
                keep.pop(j); changed = True; break
    items = [items[k] for k in keep]; starts = [starts[k] for k in keep]
    for k, (anc, rush, src_in) in enumerate(items):
        a = starts[k]; b = starts[k + 1] if k + 1 < len(items) else seg1
        if b - a > 0.05:
            video.append({'src': R(rush), 'in': round(src_in, 3), 'at': round(a, 3), 'dur': round(b - a, 3)})

def direct(rush, ranges, specs, vol=1.0):
    """Son direct face cam (« Et d'une ! ») : morceaux bruts [t0, t1], image synchrone."""
    wl = words_of(f'20261114_{rush}')
    seg0 = T
    for (t0, t1), spec in zip(ranges, specs):
        if T > seg0: cuts.append(T)
        tb = place(R(rush), [[t0, t1]], vol)
        add_subs(spec, wl, t0, t1, tb)
        video.append({'src': R(rush), 'in': round(t0, 3), 'at': round(tb[0][2], 3), 'dur': round(t1 - t0, 3)})
    return seg0, T

BEDS = []
def ambiance(seg0, seg1, vol=0.22):
    """Son d'ambiance synchrone : sous la VO, le son direct des plans affichés (foule, fanfare), très bas."""
    for v in video:
        a, b = max(seg0, v['at']), min(seg1, v['at'] + v['dur'])
        if b - a < 0.1: continue
        src_in = v['in'] + (a - v['at'])
        BEDS.append({'src': v['src'], 'in': round(src_in, 3), 'out': round(src_in + b - a, 3), 'at': round(a, 3), 'vol': vol})

POP = 'sfx/pop_harry.wav'
counter = []
def count(t, n, after=1.6):
    """Compteur affiché brièvement autour de chaque « Et de N » (Harry v2 : pas tout le temps) : n-1 puis n avec un pop."""
    a = t - 0.45
    overlays.append({'type': 'counter', 'at': round(a, 3), 'dur': round(t + after - a, 3), 'steps': [[0, n - 1], [round(t - a, 3), n]]})
    sfx.append({'src': POP, 'at': round(t, 3), 'vol': 1.2})

# ================================================================ MONTAGE (100 % voix off, test solo : DA §7 de COMMENT_HARRY_MONTE)
POP = 'sfx/pop_harry.wav'
MIME_IN = 5.75   # v6 : finit ~7,73 s, juste après le oui, AVANT qu'il quitte le personnage (7,85 s)
# 1. ACCROCHE — bouchée d'Harry d'abord, puis plans réguliers ~0,8 s
# v2 : 2 prises de la phrase (1,9 s et 6,0 s) -> la dernière seulement
vo(6.0, 8.56, "Cette année | j'ai vécu | un *Halloween* | pas comme | les *autres* {🎃}",
   shots=[(0, '223654', 0.1), (0.75, '191832', 0.3), (0.75, '214334', 26.8)])
vo(8.92, 11.40, "*Buffet* à *volonté* | avec des plats | *horrifiants* {💀}",
   shots=[(0, '191824', 0.3), ('horrifiants', '191607', 0.6)])
vo(11.92, 14.36, "un *escape game* | digne d'un | *film d'horreur*",
   shots=[(0, '195604', 0.3), ('film', '203500', 11.0)])
vo(14.82, 16.60, "et un *lieu* | totalement *atypique*",
   shots=[(0, '190930', 2.6), ('atypique', '191501', 0.3)])

# 2. HARRY — v4 : nouvelle VO « le vampire en carton », grimace (223640) puis une bouchée (221207)
# v6 : la VO2 contient 2 prises (3,3 s ratée « Bref moi c'est… » / 5,17 s complète) -> la 2e seulement
s0, s1, tm = vo(5.05, 7.5, "Bref | moi c'est *Harry* | le *vampire* en *carton*", src=VO2,
   shots=[(0, '223640', 2.2)])
nickname(word_at(tm, 'harry'), ['Le vampire', 'en carton'], until=s1 + 0.6)
vo(21.0, 23.56, "et je vous trouve | les bonnes *activités* | à faire à *Toulouse*",
   shots=[(0, '221207', 8.9), ('activites', '215136', 4.6)])

# 3. LE LIEU — enseigne Mercure, carton titre sur « Mercure » (prise 2, la dernière)
s0, s1, tm = vo(33.52, 35.76, "On se retrouve | à l'hôtel *Mercure* | de *Compans*", shots=[(0, '190920', 1.75)])
t_title = word_at(tm, 'mercure') - 0.05
overlays.append({'type': 'title', 'at': round(t_title, 3), 'dur': 1.3})
sfx.append({'src': POP, 'at': round(t_title, 3), 'vol': 2.0})
# v4 : plus de plans, des plats sanglants (Harry : « tu restes trop longtemps sur la même séquence »)
vo(36.46, 41.68, "Ils ont *métamorphosé* | l'hôtel | pour *Halloween* | et franchement | c'est *impressionnant* | l'effort mis | derrière tout ça",
   shots=[(0, '190938', 1.0), ('halloween', '191537', 2.0), ('franchement', '191607', 4.6),
          ('impressionnant', '191851', 2.4), ('effort', '191804', 5.0), ('derriere', '191832', 2.6)])

# 4. ESCAPE GAME
s0, s1, tm = vo(44.40, 49.68, "La soirée a démarré | avec un *escape game* | on a rencontré | plein de *personnes* | c'était trop *chouette*",
   shots=[(0, '201129', 0.2), ('escape', '195604', 1.0), ('rencontre', '203500', 5.98)])
# v6 : son direct de la poupée (yeux rouges qui s'allument) sous la VO puis seul ~1 s (Harry : « mets le son »)
ambiance(s0, s1, vol=0.35)
BEDS[:] = [b for b in BEDS if '203500' in b['src']]   # seulement la poupée (les autres = bavardages)
cuts.append(T)
tb = place(R('203500'), [[8.3, 8.5]], 0.45)                          # rampe (pas de marche de +9 dB)
place(R('203500'), [[8.5, 9.5]], 0.65)                                # seule, au niveau de la VO
video.append({'src': R('203500'), 'in': 8.3, 'at': round(tb[0][2], 3), 'dur': 1.2})

# 5. BUFFET
vo(51.14, 55.28, "Ensuite | on est passé | à la partie | qui m'intéresse | le plus | le *buffet*",
   shots=[(0, '191519', 0.3), ('partie', '191824', 1.1), ('buffet', '191607', 7.2)])
vo(56.78, 61.16, "Je réitère | mais regardez | ces *plats d'Halloween* | ça donne vraiment | *pas envie*",
   shots=[(0, '191537', 6.4), ('plats', '191804', 10.4), ('donne', '191607', 1.4), ('envie', '191851', 3.3)])
# v4 : Harry mime qu'il se régale et finit par un oui de la tête (223654)
s0, s1, tm = vo(62.96, 65.42, "*Bravo* au chef | car malgré tout | c'était vraiment | *excellent*",
   shots=[(0, '221117', 0.5), ('chef', '223654', MIME_IN)])

# 6. CE QU'HARRY A MANGÉ — le bon plat sur son mot
vo(66.86, 76.42, "J'ai dû manger | *5 gyozas verts* | ils étaient | trop *bons* | *10 sushis* | juste parce que | j'*adore* ça | et les *frites* | *patates douces* | étaient *succulentes*",
   shots=[(0, '212150', 0.4), ('gyozas', '214250', 6.8), ('trop', '212219', 29.6), ('sushis', '212219', 45.8),
          ('frites', '214250', 0.4), ('patates', '214334', 3.85)])
vo(77.16, 82.66, "J'ai été *moins fan* | de la *mozza* | avec la *sauce Halloween* | mais la | *côte de bœuf* | était *magnifique*",
   shots=[(0, '215136', 39.4), ('mozza', '215114', 2.6), ('sauce', '215136', 41.4), ('cote', '221117', 7.4), ('magnifique', '221207', 7.0)])

# 7. DESSERTS — v4 : vue d'ensemble du buffet de desserts (191832, milieu du rush) sur « horribles »
vo(83.54, 87.20, "Pour les *desserts* | j'avais plus faim | mais ils étaient | visuellement | *horribles*",
   shots=[(0, '223513', 0.3), ('mais', '191832', 4.4)])

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
# v6 : un plan qui dépasse la fin de son rush = ARRÊT SUR IMAGE (Harry, V5 : 0:23 et 0:26) -> on refuse
import subprocess
_dur = {}
def rush_dur(src):
    if src not in _dur:
        _dur[src] = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0',
                                          os.path.join(ROOT, 'public', src)], capture_output=True, text=True).stdout)
    return _dur[src]
frozen = [f"{v['at']:.2f}s {os.path.basename(v['src'])} (in {v['in']} + {v['dur']} > {rush_dur(v['src']):.2f})"
          for v in video if v['in'] + v['dur'] > rush_dur(v['src']) - 0.04]

edl = {'fps': FPS, 'duration': round(T, 3), 'audio': audio + BEDS, 'video': video, 'subs': subs,
       'overlays': overlays, 'sfx': sfx}
# ------------------------------------------------------------------ mixage audio à l'échantillon (tools/mixdown.py)
from mixdown import mixdown
SRC = r'D:\Harrison\Influencer\Guest-Lunch\buricot_halloween'
_VD = os.path.join(SRC, '01 PROJET', 'Adobe Premiere Pro Captured and Generated', 'hallowen_burricot')
ORIG = {VO: os.path.join(_VD, 'Audio 1.wav'), VO2: os.path.join(_VD, 'Audio 1_1.wav')}
def resolve(src):
    if src in ORIG: return ORIG[src]
    o = os.path.join(SRC, '02 RUSHES', os.path.basename(src))     # rush original (pas le proxy)
    return o if os.path.exists(o) else os.path.join(ROOT, 'public', src)
if '--no-mix' not in sys.argv:
    g, L = mixdown(audio + BEDS, sfx, T, os.path.join(ROOT, 'public', 'mix', 'halloween.wav'), resolve)
    print('mix :', L, 'LUFS | gains par source (dB) :', g)
edl['mix'] = 'mix/halloween.wav'
json.dump(edl, open(os.path.join(HERE, 'edl.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'{T:.1f} s | {len(video)} plans | {T / len(video):.2f} s/plan | '
      f'{sum(1 for v in video if v["at"] < 3)} plans < 3 s | {len(subs)} sous-titres | {len(audio)} morceaux audio')
print('blancs audio > 20 ms :', gaps or 'aucun')
print('trous/chevauchements video :', holes or 'aucun')
print('sous-titres > 4 mots :', long_sub or 'aucun')
print('ARRÊTS SUR IMAGE (plan > rush) :', frozen or 'aucun')
if frozen: sys.exit('⛔ plan plus long que son rush -> corriger avant de rendre')
