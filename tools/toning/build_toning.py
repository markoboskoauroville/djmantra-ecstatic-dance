"""The toning player's audio (v47, 21.10.2026).

Three voices read the ladder, one MP3 per rung in tools/toning/readings/<who>/ (julian: Hume, Classical Film Actor,
Octave 1; oliver: Speechify, oliver, simba-english; orion: Gemini TTS, Alnilam). For each voice this joins the rungs,
levels the whole to -16 LUFS and writes the chapters and a 3-band waveform (25 fps; low, mid, high, full; uint8).

The two music decks play one Centering song per element (Marko's own collection, "MUSIC FOR EDITING/Centering
[Marko]" on EXT_1TB): two minutes from the song's steady middle, levelled to -20 LUFS, with its own waveform. The page
sets the level with the BACKGROUND knob, -30 dB by default (Marko: "the background music should be minus 30 dB")."""
import json, subprocess, numpy as np, os, sys
R = os.path.expanduser('~/Developer/DJMANTRA_ECSTATIC_DANCE')
A = R + '/assets/toning'
SONGS = "/Volumes/EXT_1TB/MUSIC/MUSIC FOR EDITING/Centering [Marko]/"
VOICES = [('julian', 'Julian'), ('oliver', 'Oliver'), ('orion', 'Orion')]
BG = {'intro': '11. Calm', 'a': '24. Breath of the Earth', 'u': '4. Riverbank', 'i': '13. Epilogue', 'o': '12. Closeness',
      'ov': '22. Zense', 'om': '20. Cradle of Stars', 'si': '23. Aether Window'}
BG_LEN = 120

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

os.makedirs(A + '/bg', exist_ok=True)
J = {'voices': [], 'bg': {}}
for who, name in VOICES:
    if not os.path.exists(f'{R}/tools/toning/readings/{who}/readings.json'): print(name, 'not ready, left out'); continue
    meta = json.load(open(f'{R}/tools/toning/readings/{who}/readings.json'))
    files = [f'{R}/tools/toning/readings/{who}/{m["id"]}.mp3' for m in meta]
    t, ch = 0.0, []
    for m, f in zip(meta, files):
        d = dur(f); ch.append({'id': m['id'].split('-', 1)[1], 't': round(t, 3), 'dur': round(d, 3)}); t += d
    lst = f'{A}/list.txt'; open(lst, 'w').write(''.join("file '%s'\n" % f for f in files))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11',
                    '-ac', '1', '-ar', '44100', '-b:a', '96k', f'{A}/{who}.mp3'], check=True)
    os.remove(lst); wave(f'{A}/{who}.mp3', f'{A}/{who}.wave.bin')
    J['voices'].append({'id': who, 'name': name, 'src': f'assets/toning/{who}.mp3', 'wave': f'assets/toning/{who}.wave.bin',
                        'dur': round(t, 3), 'chapters': ch})
    print(name, round(t, 1), 's')
for k, song in BG.items():
    f = SONGS + song + '.mp4'; d = dur(f); s = max(0, min(d * .3, d - BG_LEN - 2))
    o = f'{A}/bg/{k}.mp3'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(s), '-t', str(BG_LEN), '-i', f, '-vn',
                    '-af', f'loudnorm=I=-20:TP=-2:LRA=11,afade=t=out:st={BG_LEN-4}:d=4', '-ac', '1', '-ar', '44100', '-b:a', '64k', o], check=True)
    wave(o, f'{A}/bg/{k}.wave.bin')
    J['bg'][k] = {'src': f'assets/toning/bg/{k}.mp3', 'wave': f'assets/toning/bg/{k}.wave.bin', 'song': song.split('. ', 1)[1], 'dur': BG_LEN}
J['bgLufs'] = -20
json.dump(J, open(f'{A}/toning.json', 'w'), indent=1)
for f in ('toning.mp3', 'toning.wave.bin'):
    if os.path.exists(f'{A}/{f}'): os.remove(f'{A}/{f}')
print('done')
