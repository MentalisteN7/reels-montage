"""Marcello — liste de montage (EDL) -> edl.json lu par la composition Remotion.
Secondes partout. Rushes = proxies 30 fps à vitesse réelle (temps source = temps du rush).

Règles de dynamisme (DA §8) appliquées automatiquement :
  - zones de parole détectées à l'énergie (tools/speech_regions.py) ; tout silence entre deux zones est COUPÉ
  - zones sans aucun mot reconnu par Whisper (« euh », souffle) = supprimées
  - chaque fin de zone (= fin de phrase / groupe) raccourcie de TRIM (≈ 1,5 image)
  - interviews : chaque coupe interne est cachée par un B-roll (plat, bouchée)
Sous-titres (DA §6bis) : découpe MANUELLE avec « | » (≤ 4 mots, 1 ligne, cohérente), *mot* = jaune, {emoji} = ligne à part
Usage : python src/episodes/marcello/build_edl.py
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
VO = 'vo/marcello_vo.wav'

def R(i):
    day = '20260131' if i.startswith('175') else '20260109'
    return f'rushes/marcello/{day}_{i}.mp4'

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
def pieces(src, noise, wlist, t0, t1, dmin=0.12, trim=None):
    """Morceaux de parole utiles dans [t0, t1] : zones d'énergie contenant au moins un mot ; silences et « euh » retirés."""
    ws = [w for w in wlist if t0 - 0.05 <= w['s'] <= t1]
    out = []
    for a, b in regions(src, noise, dmin):
        a2, b2 = max(a, t0), min(b, t1)
        if b2 - a2 < 0.06: continue
        if not any(a2 - 0.10 <= w['s'] <= b2 for w in ws): continue   # aucun mot -> « euh » / bruit
        a2 = max(t0, a2 - PAD_IN) if a2 > t0 else t0
        b2 = b2 - (TRIM if trim is None else trim) if b2 < t1 else t1
        if out and a2 - out[-1][1] < 0.04: out[-1][1] = b2
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

# ------------------------------------------------------------------ vidéo
def lay_shots(t0, t1, shots):
    t = t0
    for k, (rush, src_in, dur) in enumerate(shots):
        if k == len(shots) - 1 or t + dur > t1: dur = t1 - t
        if dur <= 0.05: break
        video.append({'src': R(rush), 'in': round(src_in, 3), 'at': round(t, 3), 'dur': round(dur, 3)})
        t += dur

VO_WORDS = words_of('vo')

def vo(t0, t1, spec, shots):
    """Une phrase de VO : prise [t0, t1] de la voix off, silences internes coupés, enchaînée sans blanc."""
    seg0 = T
    table = place(VO, pieces(VO, -35, VO_WORDS, t0, t1))
    timed = add_subs(spec, VO_WORDS, t0, t1, table)
    lay_shots(seg0, T, shots)
    return seg0, timed

HIDE_CUTS = False  # v6 (mesuré sur 84 projets Premiere) : 76 % des coupes internes d'interview restent visibles ;
                   # le B-roll ne couvre que ~23 % du temps d'interview -> seulement les plats nommés
FACE_MIN = 0.6   # on voit au moins 0,6 s le visage de l'invité avant le 1er plat

NICK_DUR = 2.7     # ~80 images comme la réf. Kebab
# 5 entrées et 5 sorties toutes différentes (Harry : « un truc différent à chaque fois »)
NICK_ANIMS = [('slide', 'slide'), ('rise', 'rise'), ('type', 'blur'), ('wipe', 'drop'), ('zoom', 'shrink')]
def nickname(at, lines, until=None):
    """Surnom (DA §6) : démarre dès que la personne est annoncée ; chaque surnom a une entrée/sortie différente."""
    k = sum(1 for o in overlays if o['type'] == 'nickname')
    a_in, a_out = NICK_ANIMS[k % len(NICK_ANIMS)]
    overlays.append({'type': 'nickname', 'at': round(at, 3), 'dur': round(min(NICK_DUR, (until or 1e9) - at), 3), 'lines': lines, 'in': a_in, 'out': a_out})

def word_at(timed, w):
    return next(t for x, t in timed if x.startswith(norm(w)[:6]))

def iv(rush, ranges, inserts=(), pool=(), sync_head=2.0, title=None):
    """Interview face cam. ranges = [(t0, t1, spec_sous_titres)].
    inserts = [(mot_ancre, rush_broll, in, durée)] posés sur le mot ; pool = B-roll de secours pour les coupes restantes."""
    wl = words_of(f'20260109_{rush}')
    seg0 = T; timed = []; tables = []; n_cuts = len(cuts)
    for k, (t0, t1, spec) in enumerate(ranges):
        if k: cuts.append(T)
        tb = place(R(rush), pieces(R(rush), -30, wl, t0, t1, IV_DMIN))
        tables.append(tb)
        timed += add_subs(spec, wl, t0, t1, tb)
    seg1 = T
    my_cuts = sorted(c for c in cuts[n_cuts:] if seg0 + 0.05 < c < seg1 - 0.05)
    # 1) B-roll ancrés sur les mots (le plat qu'il nomme)
    ins, used = [], seg0 + FACE_MIN             # v3 : le plat apparaît dès qu'il est nommé (« j'ai pris une *tartufata* »)
    for word, br, src_in, dur in inserts:
        cand = [t for w, t in timed if w.startswith(norm(word)[:6]) and t >= used - 0.8]
        if not cand: continue
        a = max(used, cand[0] - 0.10)
        b = min(seg1, a + dur)
        if b - a > 0.3: ins.append([a, b, br, src_in]); used = b
    # 2) coupes encore visibles -> B-roll de secours centré sur la coupe
    pool = list(pool); pi = 0
    for c in my_cuts:
        if any(a + 0.10 <= c <= b - 0.10 for a, b, _, _ in ins): continue
        if c < seg0 + sync_head: continue      # on garde le visage sous le titre (coupe sèche tolérée)
        nxt = [x for x in ins if c < x[0] <= c + 0.6]   # un plat ancré démarre juste après -> on l'avance sur la coupe
        if nxt:
            x = nxt[0]; new = max(c - 0.3, max([y[1] for y in ins if y[1] <= x[0]], default=seg0))
            x[3] = round(max(0.0, x[3] - (x[0] - new)), 3); x[0] = new; continue
        prv = [x for x in ins if c - 0.6 <= x[1] < c]   # un plat ancré finit juste avant -> on le prolonge
        if prv:
            prv[-1][1] = min(seg1, c + 0.3); continue
        if not HIDE_CUTS: continue             # v6 : Harry laisse ~76 % des coupes d'interview en jump cut visible
        a, b = max(seg0 + sync_head, c - 0.45), min(seg1, c + 0.6)
        br, src_in = pool[pi % len(pool)]; pi += 1
        ins.append([a, b, br, src_in])
    ins.sort()
    for x, y in zip(ins, ins[1:]):            # pas de chevauchement
        if y[0] < x[1]: y[0] = x[1]
    ins = [x for x in ins if x[1] - x[0] > 0.25]
    # 3) entre les B-roll : face cam synchrone ; un bout de face cam < 0,5 s est absorbé par le B-roll précédent
    full = []
    def sync(a, b):
        for tb in tables:
            for sa, sb, at in tb:
                lo, hi = max(a, at), min(b, at + sb - sa)
                if hi - lo > 0.02:
                    full.append({'src': R(rush), 'in': round(sa + lo - at, 3), 'at': round(lo, 3), 'dur': round(hi - lo, 3)})
    def gap_fill(a, b):
        if b - a < 0.5 and full and full[-1]['src'] != R(rush):
            full[-1]['dur'] = round(b - full[-1]['at'], 3)
        else:
            sync(a, b)
    t = seg0
    for a, b, br, src_in in ins:
        if a > t: gap_fill(t, a)
        full.append({'src': R(br), 'in': src_in, 'at': round(a, 3), 'dur': round(b - a, 3)})
        t = b
    if seg1 > t: gap_fill(t, seg1)
    video.extend(full)
    if title:   # pas d'annonce en VO -> le surnom démarre avec l'interview
        nickname(seg0, title)
    return seg0, seg1

def card(rush, t0, t1, spec, split=False):
    """Moment du carton : face cam synchrone (coupe sèche autorisée, on veut voir la note)."""
    wl = words_of(f'20260109_{rush}')
    seg0 = T
    # la note : un seul morceau continu (v4 : la détection de silence coupait dans « dix », « neuf ») ;
    # split=True seulement s'il y a une vraie pause entre deux phrases
    tb = place(R(rush), pieces(R(rush), -30, wl, t0, t1, 0.5, trim=0.02) if split else [[t0, t1]])
    add_subs(spec, wl, t0, t1, tb)
    for sa, sb, at in tb:
        video.append({'src': R(rush), 'in': round(sa, 3), 'at': round(at, 3), 'dur': round(sb - sa, 3)})
    return seg0

# ================================================================ MONTAGE
# 1. HOOK — 5 plans dans les 3 premières secondes, nourriture dès la 1re image
vo(5.0, 11.95,
   "Les meilleures *pizzas* | de *Toulouse* | se trouvent | à *Toulouse* {🍕} | Je suis *ouvert* | au *débat* | mais mon *cœur* | reste *fermé*",
   shots=[('211845', 1.7, 0.55),   # fourchette dans la burrata
          ('215116', 1.0, 0.55),   # plongée table pleine
          ('201924', 1.4, 0.55),   # pelle qui tournoie
          ('215534', 2.2, 0.60),   # bouchée de Meg
          ('201120', 1.0, 0.55),   # flamme du four
          ('215201', 0.6, 0.85),   # burrata sur la tartufata
          ('225411', 0.9, 0.75),   # v6 : teaser carton de note (Beg brandit son 10), comme Jeez / Le Roll
          ('215741', 10.6, 1.20)]) # Harry croque

# 2. MARCELLO — carton titre sur le mot « Marcello »
s0, timed = vo(20.9, 29.75,
   "On se retrouve | chez *Marcello* | où les *cuisines* | sont tenues | par des *Italiens* | qui façonnent | les *pizzas* | de manière *traditionnelle*",
   shots=[('175400', 3.6, 1.60), ('201408', 9.0, 1.10), ('201427', 1.0, 1.00), ('201437', 4.4, 1.00), ('201101', 0.8, 1.00)])
t_title = next(t for w, t in timed if w.startswith('marcello'))
overlays.append({'type': 'title', 'at': round(t_title - 0.1, 3), 'dur': 1.2})          # 36 images comme la réf.
POP = 'sfx/pop_harry.wav'   # v7 : le pop d'Harry (sound_effects/pop.mp4), posé au début du carton comme dans ses projets
sfx.append({'src': POP, 'at': round(t_title - 0.1, 3), 'vol': 2.0})   # mixdown applique x0,5 -> niveau d'origine

# 3. CUISINES OUVERTES
vo(31.2, 36.95, "Les *cuisines* | sont *ouvertes* | ce qui permet | de voir les *chefs* | en *action*",
   shots=[('201208', 1.0, 0.80), ('201330', 13.0, 0.80), ('201532', 7.0, 0.80), ('201848', 10.0, 0.90)])

# 4. SIGNATURE — Harry à l'image + titre « L'influenceur en carton »
s0, timed = vo(37.6, 42.1, "Salut, moi c'est *Harry* | et je vous partage | mes bonnes *adresses*",
   shots=[('215741', 9.0, 0.80), ('215741', 10.3, 0.80), ('215741', 11.3, 0.75), ('215741', 12.1, 2.00)])   # v6 : jump cuts du même rush (comme Les Thermes)
nickname(word_at(timed, 'harry'), ["L'influenceur", 'en carton'], until=T)   # s'arrête avant la carte Maps

# 5. 3 RESTOS — carte Google Maps (nom + note)
s0, _ = vo(49.4, 57.85,
   "Ils ont d'ailleurs | *trois* restaurants | à *Saint-Georges* | à *Saint-Pierre* | et à *Saint-Aubin* | *impossible* de les louper",
   shots=[('175325', 0.4, 2.40), ('175346', 0.3, 1.20), ('201021', 0.5, 1.00), ('200941', 4.0, 1.00)])
overlays.append({'type': 'maps', 'at': round(s0 + 0.25, 3), 'dur': 2.6})
sfx.append({'src': POP, 'at': round(s0 + 0.25, 3), 'vol': 2.0})

# 6. PRIX
vo(67.45, 69.7, "Les *pizzas* sont | à partir de *12€*", shots=[('201940', 8.0, 0.90), ('215019', 0.4, 1.20)])

# 7. INVITÉS / ENTRÉE
vo(89.95, 97.1,
   "Cette semaine | on accueille | une *véritable Italienne* | qui vient | donner son *avis* | mais d'abord *l'entrée*",
   shots=[('211823', 6.8, 1.20), ('211647', 3.0, 1.10), ('211713', 0.5, 1.00), ('211731', 0.3, 1.00)])

# 8. BEG — entrées
iv('225314', [
    (6.80, 10.62, "On a pris également | *burrata* et *polpette*"),
    (11.70, 14.12, "Et la *burrata* | genre, c'était | *incroyable*"),
    (30.75, 34.48, "Il y avait aussi | des *olives*, du *parmesan* | c'était *incroyable* | *incroyable*, *incroyable* !"),
], inserts=[('burrata', '211845', 1.7, 1.2), ('polpette', '211731', 0.3, 1.1),       # v6 : 2-3 inserts par invité (Harry : ~23 % du temps)
            ('olives', '211731', 3.2, 1.2)],
   pool=[('212006', 1.6), ('211713', 9.5)], title=['Beg', 'La reine des entrées'])
card('225411', 0.40, 2.75, "*10* ! | C'était *trop bon* !", split=True)

# 9. GUIGUI — pizza tartufata
_, timed = vo(98.75, 100.2, "On enchaîne | avec *Guigui*", shots=[('215546', 0.1, 1.40)])
nickname(word_at(timed, 'guigui'), ['Le grand', 'Guigui'])
iv('225828', [
    (2.82, 5.32, "Moi, j'ai pris | une pizza *tartufata*"),
    (6.90, 10.52, "Avec de vraies | belles *truffes* | une grosse *burrata* | comme on aime"),
    (10.80, 11.92, "Trop bon | franchement *incroyable*"),
], inserts=[('tartufata', '215201', 0.3, 1.3), ('truffes', '215042', 4.2, 1.2), ('trop', '215546', 0.0, 1.2)],
   pool=[('215201', 1.4), ('215546', 0.6)])
card('225855', 2.04, 4.56, "Pour moi ce serait | un *9* | rien n'est *parfait* | mais franchement | *très très bon*")

# 10. MEG — pizzas
_, timed = vo(101.7, 104.75, "C'est finalement | au tour de *Meg* | *l'Italienne* | pour les *pizzas*",
   shots=[('215534', 3.8, 1.40), ('215042', 1.6, 1.40)])
nickname(word_at(timed, 'meg'), ['La vraie', 'Italienne'])
iv('225637', [
    (0.0, 1.70, "*Ciao* Meg ! | *Ciao* !"),
    (27.98, 33.10, "Les pizzas sont | de vraies pizzas | *napolitaines* | *énormes*, *géantes* | qui *dépassent* | de l'assiette"),
    (35.24, 39.72, "Dans la *Marcello* | on retrouve | un petit peu | tous les *goûts* | qui viennent d'*Italie* | donc la *burrata*"),
    (40.70, 44.85, "les *pistaches* | vraiment c'était | très *gourmand* | très *bon*"),   # Whisper avait mal placé « pistaches » (v3)
], inserts=[('napolitaines', '215127', 1.0, 1.2), ('enormes', '215019', 4.3, 1.4), ('burrata', '215156', 0.3, 1.2),
            ('pistaches', '215139', 3.5, 1.2)],
   pool=[('215534', 3.0), ('215127', 2.5)])
card('225808', 1.05, 3.32, "Du coup | je mettrais un *10*")

# 11. ANTHO — desserts
_, timed = vo(115.45, 120.75, "Et enfin *Antho* | mon *ami d'enfance* | depuis *un an* | pour les *desserts*",
   shots=[('222812', 4.4, 1.40), ('222649', 0.5, 1.10), ('222702', 2.9, 1.20)])
nickname(word_at(timed, 'antho'), ["L'ami d'enfance", '(depuis 1 an)'])
iv('225552', [
    (6.05, 10.28, "La *panna cotta* | a été vraiment | *onctueuse* | et *consistante* | franchement un *délice*"),
    (13.80, 17.38, "Et surtout | ce que j'ai *aimé* | c'est qu'on avait | de bonnes *quantités* | pour les *gourmands*"),
], inserts=[('panna', '223029', 2.0, 1.3), ('onctueuse', '223343', 5.6, 1.2), ('quantites', '222649', 4.5, 1.2)],
   pool=[('223343', 2.5), ('222812', 1.0)])
card('225552', 2.00, 3.40, "Je mettrais un *9*")

# 12. CARTON RÉSULTAT (sans voix off)
t_res = T
NOTES = [('Beg', '10'), ('Guigui', '9'), ('Meg', '10'), ('Antho', '9')]
overlays.append({'type': 'result', 'at': round(t_res, 3), 'dur': 3.3, 'notes': NOTES, 'avg': '9,5'})
for k in range(len(NOTES)):
    sfx.append({'src': 'sfx/ding.mp3', 'at': round(t_res + 0.35 + k * 0.45, 3), 'vol': 0.35})
sfx.append({'src': 'sfx/bell.mp3', 'at': round(t_res + 0.35 + 4 * 0.45 + 0.1, 3), 'vol': 0.45})
sfx.append({'src': 'sfx/paper.mp3', 'at': round(t_res, 3), 'vol': 0.5})
lay_shots(t_res, t_res + 3.3, [('222745', 0.3, 3.3)])
T = t_res + 3.3

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
edl = {'fps': FPS, 'duration': round(T, 3), 'audio': audio, 'video': video, 'subs': subs,
       'overlays': overlays, 'sfx': sfx}
# ------------------------------------------------------------------ mixage audio à l'échantillon (tools/mixdown.py)
from mixdown import mixdown
ORIG = {'vo/marcello_vo.wav': os.path.join(ROOT, 'marcello', '03 MUSIQUE', 'Audio 2_1.wav')}
def resolve(src):
    if src in ORIG: return ORIG[src]
    o = os.path.join(ROOT, 'marcello', '02 RUSHES', os.path.basename(src))     # rush original (pas le proxy)
    return o if os.path.exists(o) else os.path.join(ROOT, 'public', src)
if '--no-mix' not in sys.argv:
    g, L = mixdown(audio, sfx, T, os.path.join(ROOT, 'public', 'mix', 'marcello.wav'), resolve)
    print('mix :', L, 'LUFS | gains par source (dB) :', g)
edl['mix'] = 'mix/marcello.wav'
json.dump(edl, open(os.path.join(HERE, 'edl.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'{T:.1f} s | {len(video)} plans | {T / len(video):.2f} s/plan | '
      f'{sum(1 for v in video if v["at"] < 3)} plans < 3 s | {len(subs)} sous-titres | {len(audio)} morceaux audio')
print('blancs audio > 20 ms :', gaps or 'aucun')
print('trous/chevauchements video :', holes or 'aucun')
print('sous-titres > 4 mots :', long_sub or 'aucun')
