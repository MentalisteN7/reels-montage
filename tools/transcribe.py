import sys,json
from faster_whisper import WhisperModel
m=WhisperModel(sys.argv[2] if len(sys.argv)>2 else "medium",device="cpu",compute_type="int8")
import subprocess,numpy as np
pcm=np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",sys.argv[1],"-f","s16le","-ac","1","-ar","16000","-"],capture_output=True).stdout,np.int16).astype(np.float32)/32768
segs,_=m.transcribe(pcm,language="fr",word_timestamps=True,vad_filter=False)
out=[]
for s in segs:
    print(f"[{s.start:6.2f}-{s.end:6.2f}] {s.text.strip()}",flush=True)
    out.append({"start":s.start,"end":s.end,"text":s.text,"words":[{"w":w.word,"s":w.start,"e":w.end} for w in s.words]})
json.dump(out,open(sys.argv[1].rsplit('.',1)[0]+'.words.json','w'),ensure_ascii=False)
