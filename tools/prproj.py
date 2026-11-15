"""Lit un projet Adobe Premiere (.prproj = XML gzippé) et en extrait le montage réel d'Harry.

Usage : python tools/prproj.py <fichier.prproj> [sortie.json]
Sortie : pour chaque séquence -> pistes vidéo/audio -> plans {file, t0, t1 (timeline, s), in, out (rush, s), speed}
+ les textes Premiere (Texte source) décodés quand c'est possible.
Temps Premiere : 254 016 000 000 ticks par seconde.
"""
import gzip, json, re, sys, base64
import xml.etree.ElementTree as ET

TICKS = 254016000000

def load(path):
    raw = open(path, 'rb').read()
    try: raw = gzip.decompress(raw)
    except OSError: pass
    return ET.fromstring(raw)

def parse(path):
    root = load(path)
    by_id, by_uid = {}, {}
    for el in root:
        if 'ObjectID' in el.attrib: by_id[el.attrib['ObjectID']] = el
        if 'ObjectUID' in el.attrib: by_uid[el.attrib['ObjectUID']] = el

    def ref(el):
        if el is None: return None
        if 'ObjectRef' in el.attrib: return by_id.get(el.attrib['ObjectRef'])
        if 'ObjectURef' in el.attrib: return by_uid.get(el.attrib['ObjectURef'])
        return None

    def num(el, path, default=None):
        n = el.find(path)
        return int(n.text) if n is not None and n.text and n.text.strip().lstrip('-').isdigit() else default

    def clip_item(it):
        """VideoClipTrackItem / AudioClipTrackItem -> dict"""
        ti = it.find('ClipTrackItem/TrackItem')
        t0, t1 = num(ti, 'Start', 0), num(ti, 'End', 0)
        sub = ref(it.find('ClipTrackItem/SubClip'))
        name, cin, cout, speed = None, None, None, 1.0
        if sub is not None:
            name = (sub.findtext('Name') or '').strip()
            clip = ref(sub.find('Clip'))
            if clip is not None:
                c = clip.find('Clip')
                cin, cout = num(c, 'InPoint'), num(c, 'OutPoint')
                sp = c.findtext('PlaybackSpeed')
                if sp: speed = float(sp)
        return {'file': name, 't0': round(t0 / TICKS, 3), 't1': round(t1 / TICKS, 3),
                'in': None if cin is None else round(cin / TICKS, 3),
                'out': None if cout is None else round(cout / TICKS, 3), 'speed': speed}

    seqs = []
    for seq in root.iter('Sequence'):
        if 'ObjectUID' not in seq.attrib: continue
        name = seq.findtext('Name') or ''
        out = {'name': name, 'video': [], 'audio': []}
        for tg in seq.findall('TrackGroups/TrackGroup'):
            grp = ref(tg.find('Second'))
            if grp is None: continue
            kind = 'video' if grp.tag.startswith('Video') else 'audio'
            for tr in grp.findall('TrackGroup/Tracks/Track'):
                track = ref(tr)
                if track is None: continue
                items = []
                for r in track.iter('TrackItem'):
                    it = ref(r)
                    if it is not None and it.tag.endswith('ClipTrackItem'):
                        items.append(clip_item(it))
                items.sort(key=lambda d: d['t0'])
                out[kind].append(items)
        if any(out['video']) or any(out['audio']):
            seqs.append(out)
    return seqs

def texts(path):
    """Textes Premiere (Essential Graphics) : chaînes lisibles dans les blobs base64."""
    raw = open(path, 'rb').read()
    try: raw = gzip.decompress(raw)
    except OSError: pass
    x = raw.decode('utf-8', 'replace')
    res = []
    for m in re.finditer(r'<StartKeyframeValue Encoding="base64"[^>]*>([^<]+)</StartKeyframeValue>', x):
        b = base64.b64decode(m.group(1))
        s = [t.decode('utf-8', 'replace') for t in re.findall(rb'[\x20-\x7e\xc0-\xff]{3,}', b)]
        s = [t for t in s if re.search(r'[A-Za-z]{2}', t)]
        if s: res.append(s)
    return res

if __name__ == '__main__':
    seqs = parse(sys.argv[1])
    data = {'sequences': seqs, 'texts': texts(sys.argv[1])}
    if len(sys.argv) > 2:
        json.dump(data, open(sys.argv[2], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for s in seqs:
        nv = [len(t) for t in s['video']]; na = [len(t) for t in s['audio']]
        end = max([i['t1'] for t in s['video'] + s['audio'] for i in t] or [0])
        print(f"{s['name']!r}: {end:.1f} s, pistes vidéo {nv}, audio {na}")
