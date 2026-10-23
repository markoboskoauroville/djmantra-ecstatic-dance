"""Toning song v8 on the page (page v57, 23.10.2026): six stage songs under meditation voice v5.

Marko, 23.10.2026: "Please cut my voice to different stages of the meditation. So each vowel has its own file and it
has its own audio from the Suno ... don't write any lyrics inside, just let it follow the audio 100%, add reverb, echo,
and the quiet following Tibetan voices in the background singing ... I must be loudest one." He cut his template in
Resolve himself (the timeline "Audio 2_001": AAA, UUU, III, OOO, A-U-I-O, AUM); each cut became a Suno Cover (two
takes), each take recorded whole through BlackHole his way (silence first, play, silence after). Then: "align it and
publish it to the website. Everything fully automatic", and "We have 3 channels ... all 3 players working only on the
transitions ... running only 2 channels most of the time."

- Which take: the one whose level follows his cut more closely (tools/toning/suno/takes/v8/align.json, from align8.py
  on the Mac: normalised cross-correlation of the 100 Hz level envelopes).
- Where: his cut's place in the template (his timeline's source in-points, positions.json), minus the template's 23
  frames before the voice, minus where his cut's start falls inside the recording (the lag). So `at` is the second of
  the voice at which the recording's own first sample plays.
- Each recording is copied whole (AAC 320, Apple's encoder): nothing cut, joined or stretched.
- Marko, 23.10.2026: "Please make sure the audio is not cut in, in and out. It needs to be fading in and fading out
  very slowly ... everything needs to be meditation and slow as, as the breathing of these LED lights." Each stage's
  `in` and `out` are its first and last sound; the page fades it in over 8 s from `in` and out over 8 s to `out`, on a
  raised-cosine curve (a breath), by volume only. The stages overlap, so a hand-over is a slow crossfade.
- The music lane's waveform is drawn from the six placed on one timeline; that picture is only for the eye.

Run on the Mac: python3 tools/toning/build_v57.py"""
import json, os, re, subprocess, numpy as np
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
A, T = R + '/assets/toning', R + '/tools/toning/suno/takes/v8'
NAME = {'1-AAA': ('a', 'A'), '2-UUU': ('u', 'U'), '3-III': ('i', 'I'), '4-OOO': ('o', 'O'), '5-A-U-I-O': ('ov', 'A-U-I-O'), '6-AUM': ('om', 'AUM')}
SR = 48000

def dec(f, sr=SR, ch=2):
    return np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-ac', str(ch), '-ar', str(sr), '-f', 'f32le', '-'],
                                        capture_output=True, check=True).stdout, np.float32).reshape(-1, ch)
def lufs_of(x):
    raw = '/tmp/_lufs.f32'; x.astype(np.float32).tofile(raw)
    e = subprocess.run(['ffmpeg', '-hide_banner', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', raw, '-af', 'ebur128', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    os.remove(raw); return round(float(re.findall(r'I:\s+(-?[0-9.]+) LUFS', e)[-1]), 1)

al = json.load(open(T + '/align.json'))
best = {}
for a in al:
    if a['stage'] not in best or a['r'] > best[a['stage']]['r']: best[a['stage']] = a
songs, lane = [], None
for st, a in best.items():
    k, lab = NAME[st]; take = a['file'].rsplit('-', 1)[1][:-4]
    out = f'{A}/song-v8-{k}.m4a'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{T}/{a["file"]}', '-c:a', 'aac_at', '-b:a', '320k', '-aac_at_mode', 'cbr',
                    '-movflags', '+faststart', out], check=True)
    x = dec(out); at = a['at_on_voice_s']
    # where the sound begins and ends inside the recording (the silence before and after it is the recording's own):
    # the page swells the stage in from its first sound and lets it fade out to its last, FADE s each way
    m = x.mean(1); h = SR // 20; e = 20 * np.log10(np.sqrt((m[:len(m)//h*h].reshape(-1, h)**2).mean(1)) + 1e-9)
    on = float(np.argmax(e > -60)) / 20; off = (len(e) - float(np.argmax(e[::-1] > -60))) / 20
    songs.append({'id': k, 'name': f'{lab} · {take}', 'src': f'assets/toning/song-v8-{k}.m4a', 'at': at, 'dur': round(len(x) / SR, 3),
                  'in': round(on, 2), 'out': round(off, 2), 'r': a['r']})
    s0 = int(round(at * SR)); end = s0 + len(x)
    if lane is None: lane = np.zeros((end, 2), np.float32)
    if end > len(lane): lane = np.vstack([lane, np.zeros((end - len(lane), 2), np.float32)])
    lane[s0:end] += x
    print(f'{st}: {a["file"]}, r {a["r"]}, at {at:.2f} s, {len(x)/SR:.1f} s')
songs.sort(key=lambda s: s['at'])
# the lane, for its waveform and its loudness (the page's BACKGROUND gain is set from it, as for one song before)
raw = '/tmp/_lane.wav'
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', raw], input=lane.astype(np.float32).tobytes(), check=True)
def wave(f, out):
    """the 3-band waveform of build_v54.py: 25 fps; low, mid, high, full; uint8"""
    sr = 8000; hop = sr // 25
    bands = [dec(f, sr, 1)[:, 0] if a == 'anull' else np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-af', a, '-ac', '1', '-ar', str(sr), '-f', 'f32le', '-'],
             capture_output=True).stdout, np.float32) for a in ('lowpass=f=200,lowpass=f=200', 'highpass=f=200,lowpass=f=2500', 'highpass=f=2500', 'anull')]
    n = min(len(b) for b in bands) // hop; o = []
    for b in bands:
        pk = np.abs(b[:n*hop]).reshape(n, hop).max(1)
        o.append(np.clip(pk / (np.percentile(pk, 99.5) + 1e-9) * 255, 0, 255))
    np.stack(o, 1).astype(np.uint8).tofile(out)
wave(raw, f'{A}/song-v8.wave.bin')
J = json.load(open(A + '/toning.json'))
J['song'] = {'name': 'Toning song v8', 'credit': 'Toning A U I O by DJ Mantra (v8): his own voice in six stages, each with a quiet choir behind it',
             'wave': 'assets/toning/song-v8.wave.bin', 'dur': round(len(lane) / SR, 3)}
J['songs'] = songs
J['songLufs'] = lufs_of(lane)
json.dump(J, open(A + '/toning.json', 'w'), indent=1)
os.remove(raw)
print(f'lane {len(lane)/SR:.1f} s, {J["songLufs"]} LUFS')
