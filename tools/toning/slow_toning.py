"""The toning voice, meditative: Orion's own pace with long pauses, the music first (v51, 21.10.2026).

Marko, 21.10.2026: "the voice opens the channels ... it's too fast. It needs to be very slow and meditative", then,
after v48-v50 stretched the voice to 80 %: "the voice is very much distorted ... Don't time stretch anything. Just
leave original pace, please. Or regenerate the audio itself, never stretch" (MANTRA_MANIFEST
modules/never-time-stretch.md). So nothing here changes the voice: each rung of tools/toning/readings/<who>/ is cut at
its pauses only; the longest pauses of a rung, one per sentence of its text, become SENTENCE seconds of silence, the
other phrase pauses PHRASE seconds, and the rung ends on TAIL seconds (the silence rung on a longer one, to sit in
it). Before the first word the music plays alone for MUSIC_FIRST seconds ("first start the music, then the voice").
A slower reading comes from the TTS itself (its rate setting), put into tools/toning/readings/<who>/ and run again.
Then the rungs are joined, levelled to -16 LUFS, and the chapters and the 3-band waveform written into
assets/toning/toning.json (only the voices; the background of build_bg.py stays as it is).

Run from anywhere: python3 tools/toning/slow_toning.py"""
import json, os, re, subprocess, numpy as np
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
A = R + '/assets/toning'
READ = R + '/tools/toning/readings'
# the page's one voice: (folder in tools/toning/readings, the name the page shows). v48-v51: Orion (Gemini, Alnilam);
# v52: Hume's Female Meditation Guide, read in Hume's playground at speed 1 (Marko: "already in slow speed")
VOICES = [('female-meditation-guide', 'Meditation guide')]
SR = 48000
SENTENCE, PHRASE = 3.5, 1.5       # seconds of silence after a sentence, after a phrase
TAIL, TAIL_SI = 6.0, 14.0         # after a rung; after Silence, the last one
LEAD = 0.4                        # silence before the first word of a rung
MUSIC_FIRST = 20.0                # v51, before the first word of all: "first start the music, then the voice"
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

def slow(f, text, tail, lead=LEAD):
    x = dec(f)                    # the voice as it was read: never stretched
    ps = pauses(x)
    lead_cut = ps.pop(0)[1] if ps and ps[0][0] == 0 else 0
    end = ps.pop()[0] if ps and ps[-1][1] >= len(x) else len(x)
    inner = sorted(range(len(ps)), key=lambda k: ps[k][1] - ps[k][0], reverse=True)
    long = set(inner[:max(0, sentences(text) - 1)])
    fd = int(FADE * SR); ramp = np.linspace(0, 1, fd, dtype=np.float32)
    def piece(a, b):
        s = x[a:b].copy()
        if len(s) > 2 * fd: s[:fd] *= ramp; s[-fd:] *= ramp[::-1]
        return s
    sil = lambda t: np.zeros(int(t * SR), np.float32)
    out, at = [sil(lead)], lead_cut
    for k, (a, b) in enumerate(ps):
        # keep the edges of the pause (breath, decay) and put the new silence in its middle
        keep = int(0.06 * SR)
        out += [piece(at, a + keep), sil(SENTENCE if k in long else PHRASE)]
        at = b - keep
    out += [piece(at, end), sil(tail)]
    return np.concatenate(out)

J = json.load(open(A + '/toning.json'))
J['voices'] = [{'id': who, 'name': name, 'src': f'assets/toning/{who}.mp3', 'wave': f'assets/toning/{who}.wave.bin'} for who, name in VOICES]
for v in J['voices']:
    who = v['id']
    meta = json.load(open(f'{READ}/{who}/readings.json'))
    parts, ch, t = [], [], 0.0
    for m in meta:
        rid = m['id'].split('-', 1)[1]
        f = next(f'{READ}/{who}/{m["id"]}{x}' for x in ('.m4a', '.mp3', '.wav') if os.path.exists(f'{READ}/{who}/{m["id"]}{x}'))
        y = slow(f, m['text'], TAIL_SI if rid == 'si' else TAIL, MUSIC_FIRST if not parts else LEAD)
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
    print(f'{v["name"]}: {t:.0f} s')
    v['dur'] = round(t, 3); v['chapters'] = ch
json.dump(J, open(A + '/toning.json', 'w'), indent=1)
