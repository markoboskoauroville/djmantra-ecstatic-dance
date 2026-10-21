"""The toning reading (v46): Hume AI's Female Meditation Guide reads the ladder, one MP3 per rung (assets/toning/0N-*.mp3,
made by Hume's /v0/tts, Octave 1). This joins them into toning.mp3, writes the chapters and a 3-band waveform in the
educational player's wave.bin layout (25 fps, low, mid, high, full; uint8)."""
import json, subprocess, numpy as np, os
D = os.path.expanduser('~/Developer/DJMANTRA_ECSTATIC_DANCE/assets/toning')
meta = json.load(open(os.path.expanduser('~/Developer/DJMANTRA_ECSTATIC_DANCE/tools/toning/readings/readings.json')))
files = [os.path.expanduser('~/Developer/DJMANTRA_ECSTATIC_DANCE/tools/toning/readings/') + m['id'] + '.mp3' for m in meta]
def dur(f):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f], capture_output=True, text=True).stdout)
t, ch = 0.0, []
for m, f in zip(meta, files):
    d = dur(f); ch.append({'id': m['id'].split('-', 1)[1], 't': round(t, 3), 'dur': round(d, 3)}); t += d
lst = os.path.join(D, 'list.txt')
open(lst, 'w').write(''.join("file '%s'\n" % f for f in files))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-ac', '1', '-ar', '44100', '-b:a', '96k', os.path.join(D, 'toning.mp3')], check=True)
os.remove(lst)
def dec(f, af, sr):
    return np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-af', af, '-ac', '1', '-ar', str(sr), '-f', 'f32le', '-'], capture_output=True).stdout, np.float32)
f = os.path.join(D, 'toning.mp3'); sr = 8000; hop = sr // 25
bands = [dec(f, a, sr) for a in ('lowpass=f=200,lowpass=f=200', 'highpass=f=200,lowpass=f=2500', 'highpass=f=2500', 'anull')]
n = min(len(b) for b in bands) // hop
out = []
for b in bands:
    pk = np.abs(b[:n*hop]).reshape(n, hop).max(1)
    out.append(np.clip(pk / (np.percentile(pk, 99.5) + 1e-9) * 255, 0, 255))
np.stack(out, 1).astype(np.uint8).tofile(os.path.join(D, 'toning.wave.bin'))
json.dump({'voice': 'Hume AI · Female Meditation Guide (Octave 1)', 'src': 'assets/toning/toning.mp3', 'wave': 'assets/toning/toning.wave.bin',
           'dur': round(t, 3), 'chapters': ch}, open(os.path.join(D, 'toning.json'), 'w'), indent=1)
print(round(t, 1), 's,', len(ch), 'chapters,', n, 'frames')
