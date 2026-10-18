import json, subprocess, numpy as np, sys, os
sys.path.insert(0, '.')
import djay_metadata as dm
F = json.load(open('files.json'))
def decode(f, sr, af=None):
    cmd = ['ffmpeg', '-v', 'error', '-i', f] + (['-af', af] if af else []) + ['-ac', '1', '-ar', str(sr), '-f', 'f32le', '-']
    return np.frombuffer(subprocess.run(cmd, capture_output=True).stdout, np.float32)
out = {}
for k, v in F.items():
    d = dm.read(v['meta']); B = np.array(d['beat']['beats']); fd = d['beat']['firstDownBeatIndex']
    full = decode(v['file'], 4000); low = decode(v['file'], 2000, 'lowpass=f=150,lowpass=f=150')
    fr = 20; e = np.sqrt(np.add.reduceat(low[:len(low)//fr*fr]**2, np.arange(0, len(low)//fr*fr, fr))/fr)
    on = np.maximum(np.diff(e, prepend=e[0]), 0)            # 100 fps kick onsets
    D = B[fd::4]
    bars = []
    for i in range(len(D) - 1):
        a, b = D[i], D[i+1]
        bb = B[(B >= a - 1e-3) & (B < b - 1e-3)]
        kick = np.mean([on[int(t*100):int(t*100)+4].max() for t in bb]) if len(bb) else 0
        seg = full[int(a*4000):int(b*4000)]; lseg = low[int(a*2000):int(b*2000)]
        bars.append([float(a), float(b), float(20*np.log10(np.sqrt((seg.astype(np.float64)**2).mean())+1e-9)),
                     float(20*np.log10(np.sqrt((lseg.astype(np.float64)**2).mean())+1e-9)), float(20*np.log10(kick+1e-6))])
    pre = float(D[0])                                        # beats before the first downbeat: the pickup
    out[k] = {'bpm': d['beat']['bpm'], 'first_down': pre, 'bars': bars, 'beats': [float(x) for x in B], 'fd': fd}
    kk = np.array([x[4] for x in bars]); ref = np.percentile(kk, 70)
    strip = ''.join('#' if x >= ref - 9 else '.' for x in kk)
    print(f"{k:8s} {d['beat']['bpm']:6.1f} BPM {len(bars):3d} bars  " + ' '.join(strip[i:i+8] for i in range(0, len(strip), 8)))
json.dump(out, open('bars.json', 'w'))
