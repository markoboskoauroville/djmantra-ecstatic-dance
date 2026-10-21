"""The toning player's two files (page v54, 21.10.2026): one whole voice, one whole song, untouched.

Marko, 21.10.2026: "Your audio editing is very bad. It cuts, it drops ... generate one whole block with only one
prompt, one audio file ... And the background music should be also only one piece. So we have 2 pieces. You don't
edit anything. You just play both files at the same time in the web interface."

- The voice: meditation voice v4, the whole say.json text read by Hume's Female Meditation Guide in one generation
  (the Mac session, the playground), tools/toning/readings/voice-v4.m4a. Copied byte for byte to assets/toning.
- The song: toning song v2 (take 2 HUSHED), tools/toning/suno/toning-auio-djmantra-v2.m4a, copied byte for byte.
- Added, nothing changed: each file's 3-band waveform (25 fps; low, mid, high, full; uint8), both files' loudness and
  the voice's peak (the player sets the volumes from them: the voice raised towards -16 LUFS as far as its peak allows,
  the song 14 dB under the voice at the knob's default -30 dB, as in v47-v53), and the rungs' start times in the voice. Those come from
  tools/toning/readings/voice-v4.chapters.json ([[id, seconds], ...], from Whisper's word times on the Mac) when it is
  there, else from the voice's longest pauses (the paragraph breaks between rungs).
Nothing is cut, joined, stretched or levelled (MANTRA_MANIFEST modules/never-time-stretch.md).

Run from anywhere: python3 tools/toning/build_v54.py [--voice <file>]"""
import json, os, re, shutil, subprocess, sys, numpy as np
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
A = R + '/assets/toning'
VOICE = sys.argv[sys.argv.index('--voice') + 1] if '--voice' in sys.argv else R + '/tools/toning/readings/voice-v4.m4a'
CHAPTERS = R + '/tools/toning/readings/voice-v4.chapters.json'
# toning song v3 (v2 made longer in Suno, recorded through BlackHole; Marko: "Simply create a longer song and record it
# through black hole") once it is there, else toning song v2
# the newest toning song there is: v4 (Suno Cover of Marko's own sung vowels, "toning.wav"), v3, v2
SONG = next(f for f in (R + f'/tools/toning/suno/toning-auio-djmantra-{v}.m4a' for v in ('v4', 'v3', 'v2')) if os.path.exists(f))
SV = SONG.rsplit('-', 1)[1][:-4]
IDS = ['intro', 'a', 'u', 'i', 'o', 'ov', 'om', 'si']

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
def lufs(f):
    e = subprocess.run(['ffmpeg', '-hide_banner', '-i', f, '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr
    return round(float(re.findall(r'I:\s+(-?[0-9.]+) LUFS', e)[-1]), 1)
def peak(f):
    return round(float(np.abs(dec(f, 'anull', 48000)).max()), 4)
def pauses_chapters(f):
    """the rungs' starts: the ends of the 7 longest pauses (the paragraph breaks), in order"""
    x = dec(f, 'anull', 8000); hop = 80; n = len(x) // hop
    q = 20 * np.log10(np.abs(x[:n*hop]).reshape(n, hop).max(1) + 1e-9) < -40
    runs, i = [], 0
    while i < n:
        if q[i]:
            j = i
            while j < n and q[j]: j += 1
            if i > 0 and j < n: runs.append((j - i, j * hop / 8000))
            i = j
        else: i += 1
    starts = sorted(t for _, t in sorted(runs, reverse=True)[:len(IDS) - 1])
    return [[k, t] for k, t in zip(IDS, [0.0] + starts)]

vd, sd = dur(VOICE), dur(SONG)
ch = json.load(open(CHAPTERS)) if os.path.exists(CHAPTERS) else pauses_chapters(VOICE)
ext = os.path.splitext(VOICE)[1]
shutil.copyfile(VOICE, f'{A}/voice-v4{ext}'); shutil.copyfile(SONG, f'{A}/song-{SV}.m4a')
wave(f'{A}/voice-v4{ext}', f'{A}/voice-v4.wave.bin'); wave(f'{A}/song-{SV}.m4a', f'{A}/song-{SV}.wave.bin')
J = json.load(open(f'{A}/toning.json'))
J = {'voice': {'name': 'Meditation guide', 'src': f'assets/toning/voice-v4{ext}', 'wave': 'assets/toning/voice-v4.wave.bin',
               'dur': round(vd, 3), 'chapters': [{'id': k, 't': round(t, 3)} for k, t in ch]},
     'song': {'name': f'Toning song {SV}', 'credit': f'Toning A U I O, an original song by DJ Mantra ({SV})', 'src': f'assets/toning/song-{SV}.m4a',
              'wave': f'assets/toning/song-{SV}.wave.bin', 'dur': round(sd, 3)},
     'songLufs': lufs(SONG), 'voiceLufs': lufs(VOICE), 'voicePeak': peak(VOICE), **({'download': J['download']} if 'download' in J else {})}
json.dump(J, open(f'{A}/toning.json', 'w'), indent=1)
print(f'voice {vd:.1f} s, song {sd:.1f} s, song {J["songLufs"]} LUFS; chapters', [(k, round(t, 1)) for k, t in ch])
