"""Analyse d'une vidéo de référence : plans (détection de coupes), planche contact, transcription.
Usage: python3 tools/analyze.py video.mp4 outdir"""
import sys, subprocess, json, os, re
src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
dur = float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',src],capture_output=True,text=True).stdout)
log = subprocess.run(['ffmpeg','-hide_banner','-i',src,'-vf',"scale=320:-2,select='gt(scene,0.3)',showinfo",'-vsync','vfr','-f','null','-'],capture_output=True,text=True).stderr
cuts = [0.0]+[float(x) for x in re.findall(r'pts_time:([\d.]+)',log)]+[dur]
shots = [(cuts[i],cuts[i+1]) for i in range(len(cuts)-1) if cuts[i+1]-cuts[i]>0.05]
fr = os.path.join(out,'f'); os.makedirs(fr,exist_ok=True)
for i,(a,b) in enumerate(shots):
    subprocess.run(['ffmpeg','-v','error','-ss',f'{(a+b)/2:.3f}','-i',src,'-frames:v','1','-vf',f"scale=200:-2,drawtext=text='{i} {a:.1f}s':fontsize=18:fontcolor=yellow:box=1:boxcolor=black@0.6",os.path.join(fr,f'{i:03d}.jpg'),'-y'])
n=len(shots); cols=8
for k in range(0,n,32):
    fs=[os.path.join(fr,f'{i:03d}.jpg') for i in range(k,min(n,k+32))]
    args=sum([['-i',f] for f in fs],[])
    lay='|'.join(f'{"+".join(["w0"]*(i%cols)) or 0}_{"+".join(["h0"]*(i//cols)) or 0}' for i in range(len(fs)))
    subprocess.run(['ffmpeg','-v','error',*args,'-filter_complex',f'xstack=inputs={len(fs)}:layout={lay}:fill=black' if len(fs)>1 else 'null',os.path.join(out,f'sheet{k//32}.jpg'),'-y'])
json.dump({'duration':dur,'shots':shots},open(os.path.join(out,'shots.json'),'w'))
print(f'{dur:.1f}s {n} plans, moy {dur/max(n,1):.2f}s, 3 premières s: {sum(1 for a,b in shots if a<3)} plans')
