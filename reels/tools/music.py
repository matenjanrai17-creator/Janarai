# Original light instrumental bed: soft e-piano arpeggios + warm pad + gentle bass, 92 bpm, C major.
import numpy as np, wave, sys
sr=44100; bpm=92; beat=60/bpm; dur=float(sys.argv[2]) if len(sys.argv)>2 else 45
N=int(sr*dur); L=np.zeros(N); R=np.zeros(N)
def mtof(m): return 440*2**((m-69)/12)
def add(sig,start,pan=0.0,gain=1.0):
    i=int(start*sr); j=min(N,i+len(sig))
    if i>=N: return
    s=sig[:j-i]*gain; L[i:j]+=s*(1-pan)/1.0; R[i:j]+=s*(1+pan)/1.0
def epiano(m,length=1.6):
    t=np.arange(int(sr*length))/sr; f=mtof(m)
    env=np.exp(-t*3.2)*(1-np.exp(-t*400))
    s=np.sin(2*np.pi*f*t+0.6*np.exp(-t*5)*np.sin(2*np.pi*f*2*t))+0.18*np.sin(2*np.pi*f*3*t)*np.exp(-t*6)
    return s*env
def pad(ms,length):
    t=np.arange(int(sr*length))/sr; s=np.zeros_like(t)
    for m in ms:
        for d in (-0.08,0.08):
            f=mtof(m)*2**(d/12); s+=np.sin(2*np.pi*f*t)+0.3*np.sin(2*np.pi*2*f*t)
    a=np.minimum(1,t/0.8); r=np.minimum(1,(length-t)/0.8); return s*a*r/len(ms)
def bass(m,length):
    t=np.arange(int(sr*length))/sr; f=mtof(m)
    return (np.sin(2*np.pi*f*t)+0.2*np.sin(2*np.pi*2*f*t))*np.exp(-t*1.5)*(1-np.exp(-t*200))
def shaker(length=0.08):
    t=np.arange(int(sr*length))/sr; n=np.random.randn(len(t)); n=np.diff(n,prepend=0)
    return n*np.exp(-t*60)
# C - G - Am - F  (I V vi IV), 1 bar each (4 beats)
prog=[(48,[60,64,67,72]),(43,[59,62,67,71]),(45,[60,64,69,72]),(41,[60,65,69,72])]
pattern=[0,2,1,3,2,1,3,2]  # arpeggio indices per eighth
bar=4*beat; t0=0.0; k=0; np.random.seed(1)
while t0<dur:
    root,ch=prog[k%4]
    add(pad([m-12 for m in ch[:3]],bar+0.8),t0,0,0.10)
    add(bass(root,bar),t0,0,0.22); add(bass(root,bar/2),t0+2*beat,0,0.12)
    for e,idx in enumerate(pattern):
        add(epiano(ch[idx]+12 if e in (3,7) else ch[idx]),t0+e*beat/2,(-0.35 if e%2 else 0.35),0.16)
    if k>=2:
        for e in range(8): add(shaker(),t0+e*beat/2+0.01,0.2,0.035 if e%2 else 0.02)
    t0+=bar; k+=1
st=np.stack([L,R],1)
# gentle lowpass-ish smoothing + normalize
st=np.apply_along_axis(lambda x: np.convolve(x,np.ones(4)/4,mode='same'),0,st)
fade=int(sr*2.5); st[-fade:]*=np.linspace(1,0,fade)[:,None]; st[:int(sr*0.5)]*=np.linspace(0,1,int(sr*0.5))[:,None]
st=st/np.max(np.abs(st))*0.8
w=wave.open(sys.argv[1],'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
w.writeframes((st*32767).astype(np.int16).tobytes()); w.close()
