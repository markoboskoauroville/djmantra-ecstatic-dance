"""The toning meditation as one file to download (v52, 21.10.2026; v54: the two whole files).

Marko, 21.10.2026: "in the website give option to download the audio for this vocal meditation." Since page v54 the
page plays two whole files together ("You don't edit anything"), so this lays them together as the page does: the
voice as it is, the song from the same first moment at the page's default BACKGROUND level of -30 dB, playing once,
with the page's two volumes;
nothing cut, joined, looped or stretched (MANTRA_MANIFEST modules/never-time-stretch.md). AAC 320 kbps stereo (modules/aac-320.md), over the 25 MiB a Pages
file may be, so it goes up as a GitHub Release asset (tag toning-meditation) and toning.json points the page's
DOWNLOAD button at it.
On the Mac it encodes with Apple's aac_at, CBR, a true 320 kbps; ffmpeg's own aac reaches only ~285 kbps on this quiet
mix (measured 21.10.2026), so the file to publish is made on the Mac. The file stays out of git (.gitignore): the
deploy publishes the whole repository, and a Pages file may be 25 MiB at most.

Run from anywhere: python3 tools/toning/render_meditation.py [--upload]   (--upload needs gh, logged in)"""
import json, os, shutil, subprocess, sys, numpy as np
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
A = R + '/assets/toning'
SR, DB = 48000, -30
OUT = R + '/tools/toning/dj-mantra-toning-meditation.m4a'
REPO, TAG = 'markoboskoauroville/djmantra-ecstatic-dance', 'toning-meditation'

def dec(f, ch):
    return np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-ac', str(ch), '-ar', str(SR), '-f', 'f32le', '-'],
                                        capture_output=True, check=True).stdout, np.float32).reshape(-1, ch)

J = json.load(open(A + '/toning.json')); V = J['voice']; S = J['song']
voice = dec(R + '/' + V['src'], 2); song = dec(R + '/' + S['src'], 2)
n = max(len(voice), len(song)); mix = np.zeros((n, 2), np.float32)
vdb = min(-16 - J['voiceLufs'], 20 * np.log10(.95 / J['voicePeak']))       # the page's volumes (index.html, level())
mix[:len(voice)] += voice * 10 ** (vdb / 20)
mix[:len(song)] += song * 10 ** ((J['voiceLufs'] + vdb - 14 + (DB + 30) - J['songLufs']) / 20)
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
