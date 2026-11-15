"""Proxies de montage : 1080x1920, 30 fps CFR (vitesse réelle, pas de ralenti), H.264 avec keyframes
fréquentes (seek rapide dans Remotion), audio AAC 48 kHz normalisé (-16 LUFS).
Usage: python tools/make_proxies.py <dossier_rushes> <dossier_sortie>"""
import sys, os, glob, subprocess
from concurrent.futures import ThreadPoolExecutor
src_dir, out_dir = sys.argv[1], sys.argv[2]
os.makedirs(out_dir, exist_ok=True)

def proxy(f):
    o = os.path.join(out_dir, os.path.basename(f))
    if os.path.exists(o) and os.path.getsize(o) > 0:
        return f'skip {o}'
    r = subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f,
                        '-vf', 'scale=1080:1920:flags=lanczos,fps=30,format=yuv420p',
                        '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-g', '15',
                        '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11', '-ar', '48000', '-c:a', 'aac', '-b:a', '192k',
                        '-movflags', '+faststart', o + '.part.mp4'], capture_output=True, text=True)
    if r.returncode:
        return f'ERREUR {f}: {r.stderr[-300:]}'
    os.replace(o + '.part.mp4', o)
    return f'ok {o}'

with ThreadPoolExecutor(3) as ex:
    for msg in ex.map(proxy, sorted(glob.glob(os.path.join(src_dir, '*.mp4')))):
        print(msg, flush=True)
