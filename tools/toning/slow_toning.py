"""The toning voices, slow and meditative (v48, 21.10.2026).

Marko, 21.10.2026: "the voice opens the channels ... it's too fast. It needs to be very slow and meditative." Only
Orion's reading (tools/toning/readings/<who>/, as the providers gave them in v47) are not generated again: each rung is
stretched to TEMPO with rubberband (pitch and formants kept, so the voice stays deep), then its pauses are opened:
the longest pauses of a rung, one per sentence of its text, become SENTENCE seconds of silence, the other phrase
pauses PHRASE seconds, and the rung ends on TAIL seconds (the silence rung on a longer one, to sit in it). Then, as
build_toning.py did, the rungs are joined, levelled to -16 LUFS, and the chapters and the 3-band waveform written into
assets/toning/toning.json (only the voices; the backgrounds of build_bg.py stay as they are).

Run from anywhere: python3 tools/toning/slow_toning.py"""
import json, os, re, subprocess, numpy as np
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
A = R + '/assets/toning'
READ = R + '/tools/toning/readings'
VOICES = ['orion']               # Marko, 21.10.2026: "use only Orion voice, that is all"
SR = 48000
TEMPO = 0.8                       # 80 % of the speed the voice was given
SENTENCE, PHRASE = 3.0, 1.2       # seconds of silence after a sentence, after a phrase
TAIL, TAIL_SI = 6.0, 14.0         # after a rung; after Silence, the last one
LEAD = 0.4                        # silence before the first word of a rung
GATE_DB, MIN_PAUSE = -40, 0.12    # what counts as a pause
FADE = 0.015

def dec(f, af='anull'):
    return np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-af', af, '-ac', '1', '-ar', str(SR),
                                         '-f', 'f32le', '-'], capture_output=True, check=True).stdout, np.float32).copy()

def pauses(x):
    """[start, end) sample ranges quieter than GATE_DB for at least MIN_PAUSE, in 10 ms frames."""
    hop = SR // 100; n = len(x) // hop
    db = 20 * np.log10(np.abs(x[:n * hop]).reshape(n, hop).max(1) + 1e-9)
    q = db < GATE_DB; out = []; i = 0
    while i < n:
        if q[i]:
            j = i
            while j < n and q[j]: j += 1
            if (j - i) * hop >= MIN_PAUSE * SR or i == 0 or j == n: out.append([i * hop, min(j * hop, len(x))])
            i = j
        else: i += 1
    return out

def sentences(text):
    return len([s for s in re.split(r'[.:;?!]+', text) if s.strip()])

def slow(f, text, tail):
    x = dec(f, f'rubberband=tempo={TEMPO}:pitch=1:formant=preserved:transients=smooth:detector=soft:window=long')
    ps = pauses(x)
    lead = ps.pop(0)[1] if ps and ps[0][0] == 0 else 0
    end = ps.pop()[0] if ps and ps[-1][1] >= len(x) else len(x)
    inner = sorted(range(len(ps)), key=lambda k: ps[k][1] - ps[k][0], reverse=True)
    long = set(inner[:max(0, sentences(text) - 1)])
    fd = int(FADE * SR); ramp = np.linspace(0, 1, fd, dtype=np.float32)
    def piece(a, b):
        s = x[a:b].copy()
        if len(s) > 2 * fd: s[:fd] *= ramp; s[-fd:] *= ramp[::-1]
        return s
    sil = lambda t: np.zeros(int(t * SR), np.float32)
    out, at = [sil(LEAD)], lead
    for k, (a, b) in enumerate(ps):
        # keep the edges of the pause (breath, decay) and put the new silence in its middle
        keep = int(0.06 * SR)
        out += [piece(at, a + keep), sil(SENTENCE if k in long else PHRASE)]
        at = b - keep
    out += [piece(at, end), sil(tail)]
    return np.concatenate(out)

J = json.load(open(A + '/toning.json'))
J['voices'] = [v for v in J['voices'] if v['id'] in VOICES]
for v in J['voices']:
    who = v['id']
    meta = json.load(open(f'{READ}/{who}/readings.json'))
    parts, ch, t = [], [], 0.0
    for m in meta:
        rid = m['id'].split('-', 1)[1]
        y = slow(f'{READ}/{who}/{m["id"]}.mp3', m['text'], TAIL_SI if rid == 'si' else TAIL)
        d = len(y) / SR; ch.append({'id': rid, 't': round(t, 3), 'dur': round(d, 3)}); t += d; parts.append(y)
    raw = f'{A}/{who}.f32'; np.concatenate(parts).tofile(raw)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', raw,
                    '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11', '-ac', '1', '-ar', '44100', '-b:a', '96k', f'{A}/{who}.mp3'], check=True)
    os.remove(raw)
    # the waveform as build_toning.py draws it: low, mid, high, full; 25 fps; uint8
    sr, hop = 8000, 320
    bands = [np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', f'{A}/{who}.mp3', '-af', af, '-ac', '1', '-ar', str(sr), '-f', 'f32le', '-'],
                                          capture_output=True).stdout, np.float32)
             for af in ('lowpass=f=200,lowpass=f=200', 'highpass=f=200,lowpass=f=2500', 'highpass=f=2500', 'anull')]
    n = min(len(b) for b in bands) // hop; o = []
    for b in bands:
        pk = np.abs(b[:n * hop]).reshape(n, hop).max(1)
        o.append(np.clip(pk / (np.percentile(pk, 99.5) + 1e-9) * 255, 0, 255))
    np.stack(o, 1).astype(np.uint8).tofile(f'{A}/{who}.wave.bin')
    print(f'{v["name"]}: {v["dur"]:.0f} s -> {t:.0f} s')
    v['dur'] = round(t, 3); v['chapters'] = ch
json.dump(J, open(A + '/toning.json', 'w'), indent=1)
