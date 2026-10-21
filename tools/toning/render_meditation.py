"""The toning meditation as one file to download (v52, 21.10.2026).

Marko, 21.10.2026: "in the website give option to download the audio for this vocal meditation." The page mixes it
live (the voice, deck A and deck B); this renders the same mix offline: each element's background piece in its window
on the voice's clock (in 3 s before its rung, out 3 s after the next begins, a 6 s crossfade, looped when the rung is
longer than its piece), at the page's default BACKGROUND level of -30 dB, under the voice. Nothing is stretched
(MANTRA_MANIFEST modules/never-time-stretch.md). AAC 320 kbps stereo (modules/aac-320.md), over the 25 MiB a Pages
file may be, so it goes up as a GitHub Release asset (tag toning-meditation) and toning.json points the page's
DOWNLOAD button at it.
On the Mac it encodes with Apple's aac_at, CBR, a true 320 kbps; ffmpeg's own aac reaches only ~285 kbps on this quiet
mix (measured 21.10.2026), so the file to publish is made on the Mac. The file stays out of git (.gitignore): the
deploy publishes the whole repository, and a Pages file may be 25 MiB at most.

Run from anywhere: python3 tools/toning/render_meditation.py [--upload]   (--upload needs gh, logged in)"""
import json, os, shutil, subprocess, sys, numpy as np
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
A = R + '/assets/toning'
SR, XF, DB = 48000, 6, -30
OUT = R + '/tools/toning/dj-mantra-toning-meditation.m4a'
REPO, TAG = 'markoboskoauroville/djmantra-ecstatic-dance', 'toning-meditation'

def dec(f, ch):
    return np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-ac', str(ch), '-ar', str(SR), '-f', 'f32le', '-'],
                                        capture_output=True, check=True).stdout, np.float32).reshape(-1, ch)

J = json.load(open(A + '/toning.json')); V = J['voices'][0]; O = J['bgs'][0]; C = V['chapters']
voice = dec(R + '/' + V['src'], 1)[:, 0]
n = len(voice); mix = np.zeros((n, 2), np.float32); mix += voice[:, None]
g = 10 ** ((DB - J['bgLufs']) / 20)
for i, c in enumerate(C):
    nx = C[i + 1] if i + 1 < len(C) else None
    s = c['t'] - XF / 2 if i else 0.0; e = nx['t'] + XF / 2 if nx else V['dur']
    a, b = int(s * SR), min(n, int(e * SR))
    piece = dec(R + '/' + O['pieces'][c['id']]['src'], 2)
    idx = np.arange(b - a) % len(piece)                       # looped from the window's start, as the page does
    t = np.arange(a, b) / SR
    env = np.minimum.reduce([np.ones_like(t), (t - s) / XF if i else np.ones_like(t), (e - t) / XF if nx else np.ones_like(t)])
    mix[a:b] += piece[idx] * (env * g)[:, None]
pk = np.abs(mix).max()
if pk > .98: mix *= .98 / pk
ENC = (['-c:a', 'aac_at', '-b:a', '320k', '-aac_at_mode', 'cbr'] if 'aac_at' in subprocess.run(['ffmpeg', '-hide_banner', '-encoders'],
       capture_output=True, text=True).stdout else ['-c:a', 'aac', '-b:a', '320k'])
raw = OUT + '.f32'; mix.astype(np.float32).tofile(raw)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', raw,
                '-metadata', 'title=Toning · The voice opens the channels', '-metadata', 'artist=DJ Mantra',
                *ENC, '-movflags', '+faststart', OUT], check=True)
os.remove(raw)
br = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'a', '-show_entries', 'stream=bit_rate', '-of', 'csv=p=0', OUT],
                    capture_output=True, text=True).stdout.strip()
print(f'{OUT}: {n/SR:.1f} s, {os.path.getsize(OUT)/2**20:.1f} MiB, {br} bps, peak {pk:.2f}')
name = os.path.basename(OUT)
J['download'] = {'url': f'https://github.com/{REPO}/releases/download/{TAG}/{name}', 'name': 'DJ Mantra · Toning meditation', 'dur': round(n / SR, 1)}
json.dump(J, open(A + '/toning.json', 'w'), indent=1)
if '--upload' in sys.argv:
    # the GitHub Release asset, replaced each time: upload it before main goes live, or the button points at nothing
    if subprocess.run(['gh', 'release', 'view', TAG, '-R', REPO], capture_output=True).returncode:
        subprocess.run(['gh', 'release', 'create', TAG, '-R', REPO, '--target', 'main', '--title', 'Toning meditation (The voice opens the channels)',
                        '--notes', 'The toning meditation of djmantra.pages.dev as one file: the voice and the music, AAC 320 kbps. Made by tools/toning/render_meditation.py.'], check=True)
    subprocess.run(['gh', 'release', 'upload', TAG, OUT, '-R', REPO, '--clobber'], check=True)
    print('uploaded', J['download']['url'])
