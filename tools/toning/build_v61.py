"""The toning player's new song (page v61, 9.11.2026).

Marko, 9.11.2026: "This is the song ... create a long, very slow fade-out at the end, 10 seconds; export an MP3 with
Ableton Live; that MP3 becomes part of the player. This is our new song: replace it on the DJ page and on MPA."

- The song: Suno "Chakra Toning raga (held notes)" (id 39d41591-e755-4dd3-a9d3-cb78e3b0e7c9), played into BlackHole,
  recorded by Marko in Ableton Live, a 10 s fade-out on the clip, exported by Live as MP3 CBR 320 (no WAV backup: Marko
  recreates it anytime through Suno).
- This script takes that MP3 (argument 1), copies it as assets/toning/chakra-toning-mix.mp3, draws the 3-band waveform
  (build_v60.py's wave function, 25 fps, uint8) and writes toning.json.

Run on the Mac: python3 tools/toning/build_v61.py <the exported .mp3>"""
import json, os, shutil, subprocess, sys, numpy as np
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
A = R + '/assets/toning'
SRC = sys.argv[1]
OUT = A + '/chakra-toning-mix.mp3'
shutil.copyfile(SRC, OUT)
dur, kbps = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'a', '-show_entries', 'stream=duration,bit_rate',
                            '-of', 'csv=p=0', OUT], capture_output=True, text=True).stdout.strip().split(',')
if dur == 'N/A': dur = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', OUT], capture_output=True, text=True).stdout.strip()
dur, kbps = float(dur), round(int(kbps) / 1000)

def wave(f, out):
    sr = 8000; hop = sr // 25
    bands = [np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-af', a, '-ac', '1', '-ar', str(sr), '-f', 'f32le', '-'],
             capture_output=True).stdout, np.float32) for a in ('lowpass=f=200,lowpass=f=200', 'highpass=f=200,lowpass=f=2500', 'highpass=f=2500', 'anull')]
    n = min(len(b) for b in bands) // hop; o = []
    for b in bands:
        pk = np.abs(b[:n*hop]).reshape(n, hop).max(1)
        o.append(np.clip(pk / (np.percentile(pk, 99.5) + 1e-9) * 255, 0, 255))
    np.stack(o, 1).astype(np.uint8).tofile(out)
wave(OUT, A + '/chakra-toning-mix.wave.bin')
json.dump({'mix': {'name': 'Chakra toning · raga, held notes', 'src': 'assets/toning/chakra-toning-mix.mp3?v=61',
                   'wave': 'assets/toning/chakra-toning-mix.wave.bin?v=61', 'dur': round(dur, 3), 'kbps': kbps, 'fmt': 'MP3',
                   'credit': 'Chakra toning, raga with held notes: Suno, recorded and faded in Ableton Live by DJ Mantra'}},
          open(A + '/toning.json', 'w'), indent=1, ensure_ascii=False)
print(f'{OUT}: {dur:.1f} s, {kbps} kbps')
