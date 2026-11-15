"""Mixage audio final d'un épisode, à l'échantillon près (remplace l'audio Remotion, calé à l'image).

Pourquoi : Remotion coupe l'audio sur la grille des images (1/30 s = 33 ms) -> coupes décalées, syllabes
hachées, petits artefacts. Ici on assemble tout en float 48 kHz depuis les fichiers ORIGINAUX (pas les proxies,
pas de loudnorm dynamique), avec :
  - micro-fondus enchaînés de XF ms à chaque coupe (pas de clic, pas de creux) ;
  - un gain FIXE par source (VO, chaque rush d'interview) pour que tout le monde parle au même niveau ;
  - un gain global vers TARGET_LUFS puis un limiteur (alimiter) qui empêche toute saturation.
Les sons d'origine déjà saturés au tournage (micro-cravate trop fort) ne sont pas réparés : on évite juste
d'en rajouter.
"""
import os, subprocess, re, tempfile
import numpy as np

SR = 48000
XF = 0.006          # demi-fondu à chaque coupe (6 ms de chaque côté)
SPEECH_RMS = -20.0  # niveau de parole visé par source (dBFS RMS sur les morceaux utilisés)
TARGET_LUFS = -14.0 # niveau final (Reels/TikTok)
LIMIT_DB = -1.0     # plafond du limiteur

_cache = {}
def load(path):
    if path not in _cache:
        raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-vn', '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'],
                             capture_output=True, check=True).stdout
        _cache[path] = np.frombuffer(raw, dtype=np.float32).astype(np.float64)
    return _cache[path]

def lufs(path):
    log = subprocess.run(['ffmpeg', '-hide_banner', '-i', path, '-af', 'ebur128', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', log)[-1])

def mixdown(pieces, sfx, duration, out_path, resolve):
    """pieces : [{'src','in','out','at','vol'}] ; sfx : [{'src','at','vol'}] ; resolve(src) -> chemin du fichier original."""
    n = int(round(duration * SR)) + SR
    mix = np.zeros(n)
    # 1) gain fixe par source = parole ramenée à SPEECH_RMS
    gains = {}
    for src in {p['src'] for p in pieces}:
        x = load(resolve(src))
        seg = np.concatenate([x[int(p['in'] * SR):int(p['out'] * SR)] for p in pieces if p['src'] == src])
        rms = 20 * np.log10(np.sqrt(np.mean(seg ** 2)) + 1e-12)
        gains[src] = 10 ** ((SPEECH_RMS - rms) / 20)
    # 2) morceaux posés à l'échantillon, fondus enchaînés
    xf = int(XF * SR)
    for p in pieces:
        x = load(resolve(p['src']))
        a, b = int(round(p['in'] * SR)) - xf, int(round(p['out'] * SR)) + xf
        at = int(round(p['at'] * SR)) - xf
        if a < 0: at -= a; a = 0
        if at < 0: a -= at; at = 0
        seg = x[a:b].copy() * gains[p['src']] * p.get('vol', 1.0)
        L = len(seg)
        if L <= 4 * xf: continue
        ramp = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, 2 * xf))
        seg[:2 * xf] *= ramp; seg[-2 * xf:] *= ramp[::-1]
        mix[at:at + L] += seg[:max(0, min(L, n - at))]
    voice_peak = np.abs(mix).max()
    # 3) bruitages
    for s in sfx:
        x = load(resolve(s['src']))
        at = int(round(s['at'] * SR))
        L = min(len(x), n - at)
        mix[at:at + L] += x[:L] * s.get('vol', 1.0) * 0.5
    mix = mix[:int(round(duration * SR))]
    # 4) gain global vers TARGET_LUFS puis limiteur (aucune saturation)
    tmp = os.path.join(tempfile.gettempdir(), 'mix_pre.wav')
    _write(tmp, mix / max(1.0, np.abs(mix).max()))
    g = 10 ** ((TARGET_LUFS - lufs(tmp)) / 20) * max(1.0, np.abs(mix).max())
    _write(tmp, mix * g / 8.0)          # marge : le WAV float accepte > 1, le limiteur gère
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-af',
                    f'volume=8.0,alimiter=limit={10 ** (LIMIT_DB / 20):.3f}:attack=3:release=60:level=disabled',
                    '-c:a', 'pcm_s24le', '-ar', str(SR), out_path], check=True)
    os.remove(tmp)
    return {k: round(20 * np.log10(v), 1) for k, v in gains.items()}, round(lufs(out_path), 1)

def _write(path, x):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-',
                    '-c:a', 'pcm_f32le', path], input=x.astype(np.float32).tobytes(), check=True)
