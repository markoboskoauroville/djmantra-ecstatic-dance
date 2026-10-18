import json, numpy as np
P=0.021
g=json.load(open('grid.json')); B=np.array([x[0] for x in g['beats']])-P; N=np.array([x[1] for x in g['beats']])
def rms_track(path, sr, hop):
    x=np.memmap(path,dtype=np.float32,mode='r'); n=len(x)//hop
    return np.sqrt((np.asarray(x[:n*hop]).reshape(n,hop).astype(np.float64)**2).mean(1)+1e-12), sr/hop
full,ff=rms_track('full.raw',6000,300); mid,fm=rms_track('mid.raw',6000,300); hi,fh=rms_track('hi.raw',12000,600)
low=np.fromfile('low.raw',np.float32); lo,fl=np.sqrt((low[:len(low)//100*100].reshape(-1,100).astype(np.float64)**2).mean(1)+1e-12), 20.0
kick=np.load('kick.npy')  # 100 fps low onset
def db(a): return 20*np.log10(a+1e-9)
def seg(arr,fps,t0,t1): a=arr[int(t0*fps):max(int(t0*fps)+1,int(t1*fps))]; return a.mean() if len(a) else 1e-9
# bars: every downbeat to the next
D=B[N==1]
bars=[]
for i in range(len(D)-1):
    t0,t1=D[i],D[i+1]
    if t1-t0>6: continue
    bb=B[(B>=t0-1e-3)&(B<t1-1e-3)]
    on=np.mean([kick[int(t*100):int(t*100)+4].max() for t in bb])
    offp=[(bb[j]+bb[j+1])/2 for j in range(len(bb)-1)]+[(bb[-1]+t1)/2]
    off=np.mean([kick[int(t*100):int(t*100)+4].max() for t in offp])
    bars.append([t0,t1,db(seg(full,ff,t0,t1)),db(seg(lo,fl,t0,t1)),db(seg(mid,fm,t0,t1)),db(seg(hi,fh,t0,t1)),on,off])
json.dump([[float(v) for v in r] for r in bars],open('bars.json','w'))
print(len(bars),'bars')
