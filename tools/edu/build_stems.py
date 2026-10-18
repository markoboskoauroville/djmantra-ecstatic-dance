"""The stem lanes of the educational player (v36): Ableton Live 12.4's stem separation (vocals, drums, bass, others, run
through the Stem Separation app's steps, ~/Music/Stems/<song>/), as 25 peaks a second per stem, aligned to the song.
<id>.stems.bin: 4 bytes per frame (vocals, drums, bass, others), one shared scale with a gentle curve (^0.6), so a quiet
stem looks quiet. The offset (stem time = song time - offset) is measured by cross-correlating the stems' sum with the
song: Secret ID +0.0376 s, I Follow Rivers -0.0089 s (the sums match the songs at 99.7 % and 99.3 %)."""
import numpy as np, subprocess, os
OUT = os.path.expanduser('~/Developer/DJMANTRA_ECSTATIC_DANCE/assets/edu')
SONGS = {'secret-id': ('Secret ID', 0.0376, 415.67), 'i-follow-rivers': ('I Follow Rivers', -0.0089, 156.39)}
STEMS = ['vocals', 'drums', 'bass', 'others']
SR, FPS = 8000, 25
for sid, (folder, off, dur) in SONGS.items():
    d = os.path.expanduser('~/Music/Stems/' + folder)
    pk = []
    for s in STEMS:
        x = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', f'{d}/{s}.wav', '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'],
                                         capture_output=True).stdout, np.float32)
        shift = int(round(off * SR))                       # song time T reads the stem at T - off
        x = np.concatenate([np.zeros(shift, np.float32), x]) if shift > 0 else x[-shift:]
        n = int(dur * FPS); hop = SR // FPS
        x = np.pad(x, (0, max(0, n * hop - len(x))))[:n * hop]
        pk.append(np.abs(x).reshape(n, hop).max(1))
    top = max(np.percentile(p, 99.5) for p in pk)
    lanes = np.stack([np.clip((p / top) ** 0.6 * 255, 0, 255) for p in pk], 1).astype(np.uint8)
    lanes.tofile(f'{OUT}/{sid}.stems.bin')
    act = (lanes.reshape(-1, 4) > 40).mean(0)
    print(sid, lanes.shape, 'share of time audible:', dict(zip(STEMS, np.round(act, 2))))
