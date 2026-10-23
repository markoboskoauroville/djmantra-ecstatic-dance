"""The toning player as one plain player (page v60, 23.10.2026).

Marko, 23.10.2026: "there is a new mix for my chakra toning on my web page. Please replace it with only this mix. Now
we don't have multiple channels. We don't have this kind of knobs. It's a pure player: simplicity and easy to work
with. You need to just re-encode from WAV to AAC, and that's it."

- The master: ~/Music/DJ_MANTRA_TONING/chakra toning ecstatic dance mix.wav (from his Desktop; 4:20.7, stereo 48 kHz
  24-bit), his own mix of voice and song. Encoded whole, nothing cut or levelled: AAC 320 kbps CBR, Apple's encoder,
  faststart (MANTRA_MANIFEST modules/aac-320.md).
- The waveform picture: the 3-band wave.bin of build_v57.py (25 fps; low, mid, high, full; uint8).

Run on the Mac: python3 tools/toning/build_v60.py"""
import json, os, subprocess, numpy as np
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
A = R + '/assets/toning'
WAV = os.path.expanduser('~/Music/DJ_MANTRA_TONING/chakra toning ecstatic dance mix.wav')
OUT = A + '/chakra-toning-mix.m4a'

subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', WAV, '-c:a', 'aac_at', '-b:a', '320k', '-aac_at_mode', 'cbr',
                '-movflags', '+faststart', OUT], check=True)
dur, kbps = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'a', '-show_entries', 'stream=duration,bit_rate',
                            '-of', 'csv=p=0', OUT], capture_output=True, text=True).stdout.strip().split(',')
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
wave(WAV, A + '/chakra-toning-mix.wave.bin')

json.dump({'mix': {'name': 'Chakra toning · Ecstatic Dance mix', 'src': 'assets/toning/chakra-toning-mix.m4a',
                   'wave': 'assets/toning/chakra-toning-mix.wave.bin', 'dur': round(dur, 3), 'kbps': kbps,
                   'credit': 'Chakra toning, Ecstatic Dance mix by DJ Mantra'}},
          open(A + '/toning.json', 'w'), indent=1, ensure_ascii=False)
print(f'{OUT}: {dur:.1f} s, {kbps} kbps')
