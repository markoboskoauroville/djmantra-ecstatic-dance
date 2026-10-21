"""The music decks' backgrounds (v47, 21.10.2026): one piece per element for each background the visitor can choose.

- choir, cave1, cave2: Marko's Suno songs (tools/toning/suno/takes, WAV from Suno, v6): "Toning A U I O" (take 2) and
  the two "Toning A U I O cura prox" covers of his own "cura prox" meditation. They were asked for in the order intro,
  A, U, I, O, A-U-I-O, AUM, outro, at 0, 30, 75, 120, 165, 210, 270, 315 of 355 s (the guide mix's plan), so each song
  is cut in the same proportions; Suno keeps no exact section edges, so the cuts are a first cut to check by ear.
- centering: one song per element from Marko's Centering collection (EXT_1TB).
Each piece is looped with 3 s crossfades to PIECE s, levelled to -20 LUFS and written as AAC (M4A, 160 kbps stereo),
with a 3-band waveform (25 fps). The list goes into assets/toning/toning.json under "bgs".

v48 (Marko, 21.10.2026): "new sound background for that part ... replacing the original mix of sounds with this one
original mantra song": "Toning A U I O DJ MANTRA WEB PAGE" is the only background now. Its WAV stays on the Mac
(~/Downloads); the Mac session sends it as AAC 256 kbps, tools/toning/suno/toning-auio-djmantra.m4a, and it is cut like
the Suno songs. Run from anywhere: python3 tools/toning/build_bg.py"""
import json, subprocess, numpy as np, os, tempfile
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
A = R + '/assets/toning'
IDS = ['intro', 'a', 'u', 'i', 'o', 'ov', 'om', 'si']
PLAN = [0, 30, 75, 120, 165, 210, 270, 315, 355]
PIECE, XF = 100, 3
SONGS = "/Volumes/EXT_1TB/MUSIC/MUSIC FOR EDITING/Centering [Marko]/"
CENTERING = ['11. Calm', '24. Breath of the Earth', '4. Riverbank', '13. Epilogue', '12. Closeness', '22. Zense', '20. Cradle of Stars', '23. Aether Window']
# v47: ('choir', 'Choir', 'suno/takes/toning-auio-take2.wav'), ('cave1', 'Cave I', 'suno/takes/cura-prox-take1.wav'),
#      ('cave2', 'Cave II', 'suno/takes/cura-prox-take2.wav'), ('centering', 'Centering', None)
OPTIONS = [('mantra', 'DJ Mantra', 'suno/toning-auio-djmantra.m4a')]

def dur(f):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f], capture_output=True, text=True).stdout)
def dec(f, af, sr):
    return np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-af', af, '-ac', '1', '-ar', str(sr), '-f', 'f32le', '-'], capture_output=True).stdout, np.float32)
def wave(f, out):
    sr = 8000; hop = sr // 25
    bands = [dec(f, a, sr) for a in ('lowpass=f=200,lowpass=f=200', 'highpass=f=200,lowpass=f=2500', 'highpass=f=2500', 'anull')]
    n = min(len(b) for b in bands) // hop; o = []
    for b in bands:
        pk = np.abs(b[:n*hop]).reshape(n, hop).max(1)
        o.append(np.clip(pk / (np.percentile(pk, 99.5) + 1e-9) * 255, 0, 255))
    np.stack(o, 1).astype(np.uint8).tofile(out)
def piece(src, s, L, out):
    """src from s for L seconds, looped with XF crossfades to PIECE seconds, -20 LUFS, AAC."""
    T = tempfile.mkdtemp(); seg = f'{T}/seg.wav'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(s), '-t', str(L), '-i', src, '-vn', '-ac', '2', '-ar', '48000', seg], check=True)
    n = 1; total = L
    while total < PIECE: n += 1; total += L - XF
    if n == 1:
        fc = '[0:a]anull[x]'
    else:
        fc, last = '', '[0:a]'
        for i in range(1, n): fc += f'{last}[{i}:a]acrossfade=d={XF}:c1=qsin:c2=qsin[x{i}];'; last = f'[x{i}]'
        fc = fc[:-len(f'[x{n-1}];')] + '[x]'
    fc += f';[x]atrim=0:{PIECE},loudnorm=I=-20:TP=-2:LRA=11,afade=t=in:d=1,afade=t=out:st={PIECE-3}:d=3[out]'
    subprocess.run(['ffmpeg', '-v', 'error', '-y'] + sum([['-i', seg] for _ in range(n)], []) +
                   ['-filter_complex', fc, '-map', '[out]', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', out], check=True)

J = json.load(open(f'{A}/toning.json'))
J['bgs'] = []
for oid, name, src in OPTIONS:
    os.makedirs(f'{A}/bg/{oid}', exist_ok=True); pieces = {}
    for i, k in enumerate(IDS):
        out = f'{A}/bg/{oid}/{k}.m4a'
        if src:
            f = f'{R}/tools/toning/{src}'; D = dur(f); s = PLAN[i]/PLAN[-1]*D; L = (PLAN[i+1] - PLAN[i])/PLAN[-1]*D
            piece(f, s, L, out); title = None
        else:
            f = SONGS + CENTERING[i] + '.mp4'; D = dur(f); s = max(0, min(D*.3, D - PIECE - 2))
            piece(f, s, PIECE, out); title = CENTERING[i].split('. ', 1)[1]
        wave(out, f'{A}/bg/{oid}/{k}.wave.bin')
        pieces[k] = {'src': f'assets/toning/bg/{oid}/{k}.m4a', 'wave': f'assets/toning/bg/{oid}/{k}.wave.bin', 'dur': PIECE, 'song': title}
    J['bgs'].append({'id': oid, 'name': name, 'pieces': pieces})
    print(name, 'done')
J.pop('bg', None); J['bgLufs'] = -20
json.dump(J, open(f'{A}/toning.json', 'w'), indent=1)
for k in IDS:
    for ext in ('.mp3', '.wave.bin'):
        if os.path.exists(f'{A}/bg/{k}{ext}'): os.remove(f'{A}/bg/{k}{ext}')
