"""Zones de parole d'un fichier audio/vidéo (détection d'énergie ffmpeg silencedetect).
Usage : python tools/speech_regions.py <fichier> [seuil_dB=-35] [silence_min_s=0.12]
Sortie JSON : [[début, fin], ...] en secondes."""
import sys, subprocess, re, json

def speech_regions(path, noise=-35, dmin=0.12):
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path],
                               capture_output=True, text=True).stdout)
    log = subprocess.run(['ffmpeg', '-hide_banner', '-i', path, '-vn', '-af',
                          f'highpass=f=90,lowpass=f=7000,silencedetect=noise={noise}dB:d={dmin}', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    starts = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', log)]
    ends = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', log)]
    sil = list(zip(starts, ends + [dur] * (len(starts) - len(ends))))
    regs, t = [], 0.0
    for a, b in sil:
        if a > t + 0.02: regs.append([round(t, 3), round(a, 3)])
        t = b
    if t < dur - 0.02: regs.append([round(t, 3), round(dur, 3)])
    return regs

if __name__ == '__main__':
    p = sys.argv[1]
    print(json.dumps(speech_regions(p, float(sys.argv[2]) if len(sys.argv) > 2 else -35,
                                    float(sys.argv[3]) if len(sys.argv) > 3 else 0.12)))
