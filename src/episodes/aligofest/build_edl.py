"""Aligofest — liste de montage (EDL) -> edl.json lu par la composition Remotion.
Secondes partout. Rushes = proxies 30 fps à vitesse réelle (temps source = temps du rush).

Règles de dynamisme (DA §8) appliquées automatiquement :
  - zones de parole détectées à l'énergie (tools/speech_regions.py) ; tout silence entre deux zones est COUPÉ
  - zones sans aucun mot reconnu par Whisper (« euh », souffle) = supprimées
  - chaque fin de zone (= fin de phrase / groupe) raccourcie de TRIM (≈ 1,5 image)
  - interviews : chaque coupe interne est cachée par un B-roll (plat, bouchée)
Sous-titres (DA §6bis) : découpe MANUELLE avec « | » (≤ 4 mots, 1 ligne, cohérente), *mot* = jaune, {emoji} = ligne à part
Usage : python src/episodes/aligofest/build_edl.py
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
VO = 'vo/aligofest_vo.wav'

def R(i):
    return f'rushes/aligofest/{i}.mp4' if i.startswith('VID') else f'rushes/aligofest/20261114_{i}.mp4'

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


# ------------------------------------------------------------------ helpers Aligofest
VO_WORDS = words_of('vo')

NICK_DUR = 2.7
NICK_ANIMS = [('slide', 'slide'), ('rise', 'rise'), ('type', 'blur'), ('wipe', 'drop'), ('zoom', 'shrink')]
def nickname(at, lines, until=None):
    k = sum(1 for o in overlays if o['type'] == 'nickname')
    a_in, a_out = NICK_ANIMS[k % len(NICK_ANIMS)]
    overlays.append({'type': 'nickname', 'at': round(at, 3), 'dur': round(min(NICK_DUR, (until or 1e9) - at), 3), 'lines': lines, 'in': a_in, 'out': a_out})

def vo(t0, t1, spec, shots=None):
    """Une phrase de VO (prise [t0, t1]), silences internes coupés, enchaînée sans blanc. Retourne (début, fin, mots datés)."""
    seg0 = T
    last = max((w['e'] for w in VO_WORDS if t0 - 0.05 <= w['s'] <= t1), default=t1)
    nxt = min((w['s'] for w in VO_WORDS if w['s'] > last - 0.01), default=1e9)
    t1 = max(t1, min(last + 0.08, nxt - 0.03))
    table = place(VO, pieces(VO, -40, VO_WORDS, t0, t1, trim=-0.04, keep_all=True, merge=0.06, pad_in=0.03))   # les prises ratées sont déjà exclues par [t0, t1]
    timed = add_subs(spec, VO_WORDS, t0, t1, table)
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

# ================================================================ MONTAGE
# 1. ACCROCHE — aligot géant tiré de la nacelle (vidéo ajoutée par Harry), puis 4 plans courts ; carton titre sur « Toulouse »
s0, s1, tm = vo(1.65, 4.72, "On accueille | le plus *grand* | événement d'*aligot* | du *monde* | à *Toulouse* {🧀}",
   shots=[(0, '133530', 6.6), (0.78, '124838', 5.0), (0.78, 'VID_20261115_083120_852', 1.4)])   # v3 : 3 plans réguliers, la bouchée de saucisse
ambiance(s0, s1, 0.30)
t_title = word_at(tm, 'toulouse') - 0.05
overlays.append({'type': 'title', 'at': round(t_title, 3), 'dur': 1.3})
sfx.append({'src': POP, 'at': round(t_title, 3), 'vol': 2.0})

vo(5.2, 9.15, "*4 tonnes* | ont été servies | *aligot saucisse* | à *volonté* | pour tout le monde",
   shots=[(0, '124552', 1.4), ('volonte', '125955', 1.2), ('pour', '134340', 2.0)])

# 2. HARRY — jump cuts du même rush d'aligot qui file + surnom
s0, s1, tm = vo(10.5, 15.6, "Sinon moi c'est *Harry* | *l'influenceur* en *carton* | et je vous partage | les *bons plans* | à *Toulouse*",
   shots=[(0, '130053', 3.9), ('influenceur', '134420', 3.6), ('bons', '130137', 12.2)])   # v3 : jamais 2 plans du même rush à la suite
nickname(word_at(tm, 'harry'), ["L'influenceur", 'en carton'], until=s1)

# 3. LE DÉFI : 5 ASSIETTES — la pile la plus haute, on envoie les assiettes dessus
vo(16.7, 21.98, "Et surtout | on avait pour *objectif* | avec les *copains* | de manger *5 assiettes*",
   shots=[(0, '124734', 0.3), ('copains', '124719', 6.2), ('manger', '140403', 1.0)])

# 4. L'ÉVÉNEMENT — foule, ambiance (son direct très bas), compteur de kg
s0, s1, _ = vo(23.3, 31.65, "L'événement a réuni | *3000 personnes* | avec une *ambiance* | de *folie* | et a servi | plus de *4 tonnes* | d'*aligot* | ce qui est | un *record du monde*",
   shots=[(0, '133615', 1.2), ('personnes', '131843', 0.8), ('ambiance', '132133', 3.6), ('folie', '132022', 1.6),
          ('servi', '132226', 1.3), ('plus', '125245', 4.4), ('qui', '131922', 4.0), ('record', '133615', 2.6)])
ambiance(s0, s1, 0.25)

# 5. FIER D'ÊTRE TOULOUSAIGN — Harry croque la saucisse
vo(32.68, 33.58, "Fier d'être | *toulousaign*", shots=[(0, '124838', 6.0)])

# 6. ACTIVITÉS
s0, s1, _ = vo(34.75, 38.05, "Il y avait | un *beer pong* | plein d'*activités* | et des *cookies* | à l'*aligot*",
   shots=[(0, '142646', 0.0), ('plein', '141228', 1.0), (0.45, '141701', 4.5),
          ('cookies', '142829', 1.0), (0.75, '125837', 0.3)])
ambiance(s0, s1, 0.20)

# 7. LA COMPÈTE — assiettes pleines + Gouz qui fronce les sourcils ; le compteur apparaît
s0, s1, tm = vo(39.45, 42.25, "*Bref* | on démarre | la *compète* | prêt à *attaquer*", shots=[(0, '124719', 2.4)])
vo(43.0, 44.98, "On a été servis | *direct* | *0 seconde* | d'attente", shots=[(0, '124552', 2.8), ('seconde', '125955', 1.0)])
vo(47.75, 50.45, "La *saucisse* | était bonne | et l'*aligot* | passait très bien",
   shots=[(0, '124838', 8.9), ('aligot', '124818', 8.3)])
s0, _ = direct('125554', [(2.15, 3.65)], ["Et *d'une* !"]); count(s0 + 0.2, 1)

# 8. 2e ASSIETTE
vo(54.45, 57.35, "On enchaîne direct | avec la *deuxième* | *assiette* | pour *20 secondes* | d'attente",
   shots=[(0, '125749', 0.6), ('deuxieme', '125618', 0.3), ('20', '125749', 1.9)])
vo(60.2, 61.45, "ça a laissé | le temps de *digérer*", shots=[(0, '124740', 0.0)])
vo(63.45, 66.0, "*L'astuce* avec l'aligot | c'est de le manger | tant que | c'est *chaud*",
   shots=[(0, '130137', 2.0), (1.0, '134420', 9.0)])
s0, _ = direct('130732', [(3.9, 5.15)], ["Et de *deux* !"]); count(s0 + 0.2, 2)

# 9. 3e ASSIETTE (le double, 1 kg)
vo(67.05, 69.1, "La *troisième assiette* | ils ont voulu | nous *achever*", shots=[(0, '130743', 0.4), ('voulu', '124719', 6.2)])
vo(69.7, 74.58, "Il y avait | le *double* | l'assiette pesait | *1 kg* | mais c'était | *super filant* | un vrai *délice*",
   shots=[(0, '131116', 1.6), ('super', '130053', 6.4), ('delice', '130137', 19.3)])
s0, _ = direct('132443', [(12.25, 13.25)], ["Et de *trois* !"]); count(s0 + 0.2, 3)

# 10. MARIE ABANDONNE — l'échange face cam, puis la VO en chute
direct('132507', [(0.2, 2.3), (3.85, 6.45), (7.1, 8.2)],
       ["Alors *Marie* | comment ça | se passe là ?", "C'est un peu | *compliqué* là | je trouve, non ?", "Allez *Marie* !"])
vo(78.95, 80.72, "On a *malheureusement* | perdu *Marie* | sur le chemin", shots=[(0, '133006', 0.6)])

# 11. 4e ASSIETTE (+ 1 saucisse)
vo(81.95, 83.78, "La *quatrième assiette* | était encore | plus *gourmande*", shots=[(0, '134340', 0.9), ('gourmande', '134401', 0.1)])
vo(85.1, 86.45, "et j'ai *négocié* | une *saucisse* de plus", shots=[(0, '134340', 2.3), ('saucisse', '134420', 6.0)])
# Harry qui souffle, la 4e assiette est dure (son direct, pause de VO)
s0 = T; audio.append({'src': R('135928'), 'in': 14.2, 'out': 16.0, 'at': round(T, 3), 'vol': 1.0})
video.append({'src': R('135928'), 'in': 14.2, 'at': round(T, 3), 'dur': 1.8}); cuts.append(T); T += 1.8
s0, _ = direct('140327', [(3.6, 5.0)], ["Et de *quatre* !"]); count(s0 + 0.4, 4, after=1.0)

# 12. PEÑA BAIONA — 1 s de fanfare seule, puis sous la VO
LEAD = 1.0
audio.append({'src': R('142535'), 'in': 2.0, 'out': 2.0 + LEAD, 'at': round(T, 3), 'vol': 0.9})
video.append({'src': R('142535'), 'in': 2.0, 'at': round(T, 3), 'dur': LEAD})
T += LEAD
s0, _, _ = vo(93.65, 95.6, "J'ai voulu | faire une pause | avec la *peña baiona*", shots=[(0, '132133', 3.4), ('pena', '142603', 0.5)])
_, s1, _ = vo(96.1, 99.2, "mais avec | *4 assiettes* d'aligot | dans le *gosier* | j'étais pas *serein*",
   shots=[(0, '140403', 1.0), ('gosier', '135928', 9.3)])
BEDS.append({'src': R('142535'), 'in': 2.0 + LEAD, 'out': round(2.0 + LEAD + (s1 - s0), 3), 'at': round(s0, 3), 'vol': 0.30})

# 13. FIN — retour en boitant, scores, on finit sur la VO
s0, s1, _ = vo(100.58, 104.5, "La *lutte* | a été dure | mais nous rentrons | *victorieux* | prêts à revenir | l'*année prochaine*",
   shots=[(0, '143338', 8.6)])
SC = [['Marie', '2 assiettes'], ['Gouz', '3 assiettes'], ['Harry', '4 assiettes', '+ 5 saucisses']]
STEP = 0.6
overlays.append({'type': 'scores', 'at': round(s0 + 0.5, 3), 'dur': round(s1 - s0 - 0.5, 3), 'rows': SC, 'step': STEP})
for k in range(len(SC)):
    sfx.append({'src': POP, 'at': round(s0 + 0.5 + k * STEP, 3), 'vol': 0.8})

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
edl = {'fps': FPS, 'duration': round(T, 3), 'audio': audio + BEDS, 'video': video, 'subs': subs,
       'overlays': overlays, 'sfx': sfx}
# ------------------------------------------------------------------ mixage audio à l'échantillon (tools/mixdown.py)
from mixdown import mixdown
SRC = r'D:\Harrison\Influencer\Guest-Lunch\aligofest'
ORIG = {VO: os.path.join(SRC, '01 PROJET', 'Adobe Premiere Pro Captured and Generated', 'aligofest', 'Audio 2_1.wav')}
def resolve(src):
    if src in ORIG: return ORIG[src]
    o = os.path.join(SRC, '02 RUSHES', os.path.basename(src))     # rush original (pas le proxy)
    return o if os.path.exists(o) else os.path.join(ROOT, 'public', src)
if '--no-mix' not in sys.argv:
    g, L = mixdown(audio + BEDS, sfx, T, os.path.join(ROOT, 'public', 'mix', 'aligofest.wav'), resolve)
    print('mix :', L, 'LUFS | gains par source (dB) :', g)
edl['mix'] = 'mix/aligofest.wav'
json.dump(edl, open(os.path.join(HERE, 'edl.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'{T:.1f} s | {len(video)} plans | {T / len(video):.2f} s/plan | '
      f'{sum(1 for v in video if v["at"] < 3)} plans < 3 s | {len(subs)} sous-titres | {len(audio)} morceaux audio')
print('blancs audio > 20 ms :', gaps or 'aucun')
print('trous/chevauchements video :', holes or 'aucun')
print('sous-titres > 4 mots :', long_sub or 'aucun')
