import subprocess, sys, os, json
S=sys.argv[1]; LANG=sys.argv[2]; OUT=sys.argv[3]
B=f"{S}/build"; W,H,FPS=1080,1920,30; X=0.3  # crossfade
TM=("zscale=tin=arib-std-b67:t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,"
    "tonemap=mobius:param=0.3:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,eq=saturation=1.03")
def dur(f): return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f]))
def run(c): subprocess.run(c,check=True)
lines=["H","B1","B2","B3","B4","C1","C2"]
gap={"H":0.35,"B1":0.2,"B2":0.2,"B3":0.2,"B4":0.4,"C1":0.2,"C2":1.4}
lead=0.35; t=lead; start={}; vd={}
for k in lines:
    vd[k]=dur(f"{S}/vo2/{LANG}_{k}.wav"); start[k]=t; t+=vd[k]+gap[k]
TOTAL=round(t,3)
# shot plan: (src, ss, weight, zoom, fx, fy)  ; photos: ss=None
plan={
 "H": [("src/IMG_3322.MOV",3.0,"fix1.5",1.0,.5,.5),("src/IMG_4675.MOV",0.3,1,1.0,.5,.5)],
 "B1":[("src/IMG_8438.MOV",1.0,1,2.0,.5,1.0),("src/IMG_6741.MOV",2.5,1,1.0,.5,.5)],
 "B2":[("src/IMG_7611.MOV",5.3,1,1.0,.5,.5),("src/IMG_6449.MOV",10.6,1,1.3,.4,.9)],
 "B3":[("src/IMG_2076.MOV",10.3,1.1,1.0,.5,.5),("img/D3013F40.jpg",None,1,1.0,.5,.5)],
 "B4":[("src/IMG_1160.MOV",0.2,1,1.0,.5,.5),("src/IMG_1759.MOV",0.5,0.9,1.0,.5,.5),("src/IMG_4656.MOV",0.0,1.2,1.0,.5,.5)],
 "C1":[("img/C0C949C1.jpg",None,1,1.0,.5,.55)],
 "C2":[(f"build/card_{LANG}.png",None,1,1.0,.5,.5)],
}
shots=[]
for i,k in enumerate(lines):
    seg_s=0 if i==0 else start[k]; seg_e=TOTAL if k=="C2" else start[lines[i+1]]
    L=seg_e-seg_s; items=plan[k]
    fixed=sum(float(w[3:]) for _,_,w,*_ in items if isinstance(w,str))
    ws=sum(w for _,_,w,*_ in items if not isinstance(w,str))
    for src,ss,w,z,fx,fy in items:
        d=float(w[3:]) if isinstance(w,str) else (L-fixed)*w/ws
        shots.append(dict(src=src,ss=ss,d=d,z=z,fx=fx,fy=fy,seg=k))
os.makedirs(f"{B}/shots_{LANG}",exist_ok=True)
files=[]
for n,sh in enumerate(shots):
    d=sh["d"]+(X if n<len(shots)-1 else 0); o=f"{B}/shots_{LANG}/{n:02d}.mp4"; src=f"{S}/{sh['src']}"
    z=sh["z"]; cw,ch=W,H
    if sh["ss"] is not None:
        sc=f"scale={int(W*z)}:{int(H*z)}:force_original_aspect_ratio=increase:flags=lanczos"
        cr=f"crop={W}:{H}:(iw-{W})*{sh['fx']}:(ih-{H})*{sh['fy']}"
        vf=f"{TM},fps={FPS},{sc},{cr},setsar=1"
        run(["ffmpeg","-v","error","-y","-ss",str(sh["ss"]),"-t",f"{d:.3f}","-i",src,"-vf",vf,"-an",
             "-c:v","libx264","-crf","16","-preset","medium","-pix_fmt","yuv420p",o])
    else:
        frames=int(round(d*FPS))+1
        zr="0.0006" if "card" not in src else "0.00025"
        vf=(f"scale={W*2}:{H*2}:force_original_aspect_ratio=increase:flags=lanczos,crop={W*2}:{H*2}:(iw-{W*2})*{sh['fx']}:(ih-{H*2})*{sh['fy']},"
            f"zoompan=z='1+{zr}*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={W}x{H}:fps={FPS},setsar=1,format=yuv420p")
        run(["ffmpeg","-v","error","-y","-loop","1","-i",src,"-vf",vf,"-frames:v",str(frames),"-t",f"{d:.3f}",
             "-c:v","libx264","-crf","16","-preset","medium","-pix_fmt","yuv420p",o])
    files.append(o)
# xfade chain
inp=[]; [inp.extend(["-i",f]) for f in files]
fc=[]; prev="[0:v]"; off=0
for n in range(1,len(files)):
    off+=shots[n-1]["d"]; lab=f"[v{n}]"
    fc.append(f"{prev}[{n}:v]xfade=transition=fade:duration={X}:offset={off-X/2 if False else off:.3f}{lab}")
    prev=lab
# offsets: each shot file n-1 has length d+X; xfade offset = cumulative d (start of overlap)
fc=[]; prev="[0:v]"; acc=0.0
for n in range(1,len(files)):
    acc+=shots[n-1]["d"]; lab=f"[v{n}]"
    fc.append(f"{prev}[{n}:v]xfade=transition=fade:duration={X}:offset={acc:.3f}{lab}"); prev=lab
run(["ffmpeg","-v","error","-y",*inp,"-filter_complex",";".join(fc),"-map",prev,"-t",f"{TOTAL:.3f}",
     "-c:v","libx264","-crf","17","-preset","medium","-pix_fmt","yuv420p","-r",str(FPS),f"{B}/video_{LANG}.mp4"])
# voice track
ainp=[]; parts=[]
for i,k in enumerate(lines):
    ainp+=["-i",f"{S}/vo2/{LANG}_{k}.wav"]
    parts.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=mono,adelay={int(start[k]*1000)}[a{i}]")
mix="".join(f"[a{i}]" for i in range(len(lines)))
fca=";".join(parts)+f";{mix}amix=inputs={len(lines)}:normalize=0,apad,atrim=0:{TOTAL},"\
    "highpass=f=80,acompressor=threshold=-20dB:ratio=2.5:attack=5:release=80,loudnorm=I=-16:TP=-1.5:LRA=7[v]"
run(["ffmpeg","-v","error","-y",*ainp,"-filter_complex",fca,"-map","[v]","-ac","1","-ar","48000",f"{B}/voice_{LANG}.wav"])
# music bed, ducked under voice, fade out
fcm=(f"[1:a]atrim=0:{TOTAL},asetpts=N/SR/TB,aresample=48000,volume=0.16,afade=t=out:st={TOTAL-2.2:.2f}:d=2.2[m];"
     f"[0:a]aresample=48000,aformat=channel_layouts=stereo,asplit=2[v1][v2];"
     f"[m][v2]sidechaincompress=threshold=0.03:ratio=4:attack=40:release=400[md];"
     f"[v1][md]amix=inputs=2:normalize=0,alimiter=limit=0.89[a]")
run(["ffmpeg","-v","error","-y","-i",f"{B}/voice_{LANG}.wav","-i",f"{B}/music.wav","-filter_complex",fcm,"-map","[a]","-ar","48000",f"{B}/mix_{LANG}.wav"])
run(["ffmpeg","-v","error","-y","-i",f"{B}/video_{LANG}.mp4","-i",f"{B}/mix_{LANG}.wav","-map","0:v","-map","1:a",
     "-c:v","copy","-c:a","aac","-b:a","192k","-movflags","+faststart","-shortest",OUT])
print(json.dumps(dict(total=TOTAL,start=start,shots=[(s["src"].split('/')[-1],round(s["d"],2)) for s in shots]),ensure_ascii=False))
