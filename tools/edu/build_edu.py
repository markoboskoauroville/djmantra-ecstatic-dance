"""The educational player's songs (v34): audio for the web, a 3-band waveform (25 fps, the mix's wave.bin layout:
low, mid, high, full), djay Pro's beats, and the sections read from the song (kick, bands, the separated voice)."""
import json, subprocess, numpy as np, os
OUT = os.path.expanduser('~/Developer/DJMANTRA_ECSTATIC_DANCE/assets/edu')
F = json.load(open('files.json')); BARS = json.load(open('bars.json'))
def dec(f, af, sr):
    return np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-af', af, '-ac', '1', '-ar', str(sr), '-f', 'f32le', '-'],
                                        capture_output=True).stdout, np.float32)
def wave(f):
    sr = 8000; hop = sr // 25
    bands = [dec(f, a, sr) for a in ('lowpass=f=200,lowpass=f=200', 'highpass=f=200,lowpass=f=2500', 'highpass=f=2500', 'anull')]
    n = min(len(b) for b in bands) // hop
    out = []
    for b in bands:
        pk = np.abs(b[:n*hop]).reshape(n, hop).max(1)
        out.append(np.clip(pk / (np.percentile(pk, 99.5) + 1e-9) * 255, 0, 255))
    return np.stack(out, 1).astype(np.uint8)
def bar(song, n):            # the start of bar n (1-based, djay's downbeats)
    return round(BARS[song]['bars'][n-1][0], 3)
SONGS = []
# --- Secret ID: the instrumental example -------------------------------------------------------------------------
s = 'secret'
SONGS.append(dict(id='secret-id', kind='instrumental', title='Secret ID', artist='Moojo, Da Capo', bpm=120, key='',
  code='I16 · I32 · B36 · M48 · B24 · M32 · O16',
  sections=[[0, 'INTRO', 48, 'i1'], [bar(s, 49), 'BREAKDOWN', 16, 'b1'], [bar(s, 65), 'BUILD-UP', 20, 'u1'],
            [bar(s, 85), 'DROP', 48, 'd1'], [bar(s, 133), 'BREAKDOWN', 16, 'b2'], [bar(s, 149), 'BUILD-UP', 8, 'u2'],
            [bar(s, 157), 'DROP', 32, 'd2'], [bar(s, 189), 'OUTRO', 16, 'o1']],
  events=[[bar(s, 1), 'e.kick'], [bar(s, 17), 'e.hats'], [bar(s, 49), 'e.stop'], [bar(s, 65), 'e.rise'],
          [bar(s, 81), 'e.bascut'], [bar(s, 85), 'e.drop'], [bar(s, 133), 'e.stop'], [bar(s, 149), 'e.rise'],
          [bar(s, 157), 'e.drop'], [bar(s, 189), 'e.out'], [bar(s, 205), 'e.end']]))
# --- I Follow Rivers: the vocal example ---------------------------------------------------------------------------
s = 'rivers'
SONGS.append(dict(id='i-follow-rivers', kind='vocal', title='I Follow Rivers', artist='Sean Finn, Play!On', bpm=125, key='',
  code='V13vo · P8vo · C8vo · M8 · V8vo · P4vo · C8vo · B8vo · C16vo',
  sections=[[0, 'VERSE', 13, 'v1'], [bar(s, 14), 'PRE-CHORUS', 8, 'p1'], [bar(s, 22), 'CHORUS', 8, 'c1'],
            [bar(s, 30), 'INSTRUMENTAL', 8, 'n1'], [bar(s, 38), 'VERSE', 8, 'v2'], [bar(s, 46), 'PRE-CHORUS', 4, 'p2'],
            [bar(s, 50), 'CHORUS', 8, 'c2'], [bar(s, 58), 'BRIDGE', 8, 'br'], [bar(s, 66), 'CHORUS', 16, 'c3']],
  events=[[0.0, 'e.voice'], [bar(s, 14), 'e.stopv'], [bar(s, 22), 'e.hook'], [bar(s, 30), 'e.novoice'],
          [bar(s, 38), 'e.story'], [bar(s, 46), 'e.stopv'], [bar(s, 50), 'e.hook'], [bar(s, 58), 'e.echo'],
          [bar(s, 66), 'e.last'], [round(BARS[s]['bars'][-1][1], 3), 'e.noout']]))
for song, key in zip(SONGS, ('secret', 'rivers')):
    f = F[key]['file']
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f, '-vn', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart',
                    os.path.join(OUT, song['id'] + '.m4a')], check=True)
    wave(f).tofile(os.path.join(OUT, song['id'] + '.wave.bin'))
    song['src'] = 'assets/edu/' + song['id'] + '.m4a'; song['wave'] = 'assets/edu/' + song['id'] + '.wave.bin'
    song['dur'] = round(F[key]['dur'], 2)
    B = BARS[key]; song['beats'] = [[round(t, 3), ((i - B['fd']) % 4) + 1] for i, t in enumerate(B['beats'])]
json.dump({'note': 'v34 educational player; beats: djay Pro; sections read from the kick, the bands and the voice (Demucs + Whisper)',
           'songs': SONGS}, open(os.path.join(OUT, 'edu.json'), 'w'), separators=(',', ':'), ensure_ascii=False)
for s in SONGS: print(s['title'], s['dur'], [(x[1], x[0]) for x in s['sections']])
