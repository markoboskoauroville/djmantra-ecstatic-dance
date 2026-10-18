"""grid.json for the demo mix player: djay Pro's beats, rekordbox's bar numbers and phrases (18.10.2026)."""
import json, sys
import numpy as np
sys.path.insert(0, '.')
import rekordbox_phrases as rp

PLAYER = 0.021     # the site's HLS runs 21 ms after the original file (AAC priming, measured by cross-correlation)
RB = 0.045         # rekordbox reads the file 45 ms late (it keeps the 2112-sample encoder delay)
FREE = [(648.3, 883.78), (6520.2, 6803.9)]   # no kick: Olafur Arnalds 03:06 and the start of track 3; Shallow Water's fade to the end

b = np.array(json.load(open('mix_djay.json'))['beat']['beats']); per = np.diff(b, append=b[-1] + 0.5)
dat, ext = rp.tags('rb/ANLZ0000.DAT'), rp.tags('rb/ANLZ0000.EXT')
grid = rp.beat_grid(dat['PQTZ']); rt = np.array([g[2] for g in grid]) - RB; rn = np.array([g[0] for g in grid])
free = lambda t: any(a <= t < z for a, z in FREE)

# rekordbox's bar position for each djay beat: the rekordbox beat at or just before it (within -0.6 .. +0.2 beat),
# so a rekordbox grid half a beat early still gives its count to the kick that follows
phase = np.full(len(b), -1)
for i, t in enumerate(b):
    j = np.searchsorted(rt, t + 0.2 * per[i]) - 1
    if j >= 0 and rt[j] >= t - 0.6 * per[i]:
        phase[i] = (i - (rn[j] - 1)) % 4
# majority over 32 beats; a phase holds until another wins clearly (60 %); djay's own count where nobody is sure
own = 3 % 4
cur, out = own, np.zeros(len(b), int)
for i in range(len(b)):
    w = phase[max(0, i - 16):i + 16]; w = w[w >= 0]
    if len(w) >= 12:
        c = np.bincount(w, minlength=4)
        if c.max() >= 0.6 * len(w): cur = int(np.argmax(c))
    out[i] = cur
# a bar change that lasts less than 8 bars is rekordbox restarting its count, not the music: it is merged back
runs = []
for i, v in enumerate(out):
    if runs and runs[-1][2] == v: runs[-1][1] = i + 1
    else: runs.append([i, i + 1, v])
changed = True
while changed:
    changed = False
    for r in range(1, len(runs)):
        if runs[r][1] - runs[r][0] < 32:
            runs[r][2] = runs[r - 1][2]; changed = True
    merged = []
    for r in runs:
        if merged and merged[-1][2] == r[2]: merged[-1][1] = r[1]
        else: merged.append(r)
    runs = merged
for a0, z0, v in runs: out[a0:z0] = v
n = (np.arange(len(b)) - out) % 4 + 1

beats = [[round(float(t) + PLAYER, 3), int(k)] for t, k in zip(b, n) if not free(t)]

# phrases: rekordbox's start beat -> its time -> the nearest djay downbeat (within one beat), bars by rekordbox's count
mood, end_beat, ph = rp.phrases(ext['PSSI'])
downs = np.array([t for t, k in zip(b, n) if k == 1])
sections = []
for p, q in zip(ph, ph[1:] + [{'beat': end_beat}]):
    t = rt[min(len(rt), max(1, p['beat'])) - 1]
    if not free(t) and len(downs):
        d = downs[np.argmin(np.abs(downs - t))]
        if abs(d - t) < 0.7: t = d
    bars = max(1, round((q['beat'] - p['beat']) / 4))
    sections.append([round(float(t) + PLAYER, 3), p['kind'].upper(), bars])

out_json = {
    'source': 'beats: djay Pro 5 neural beat tracker (ARDeepBeatTrackerModel1011_9, dynamic grid, the authority); '
              'bar numbers and sections: rekordbox 7 dynamic analysis + phrase analysis (mood high), snapped to djay downbeats; '
              'times on the player timeline (original file + 0.021 s); free = no steady kick',
    'beats': beats, 'sections': sections, 'free': [[round(a + PLAYER, 3), round(z + PLAYER, 3)] for a, z in FREE]}
json.dump(out_json, open('grid.json', 'w'), separators=(',', ':'))
print(len(beats), 'beats,', len(sections), 'sections, kinds', sorted({s[1] for s in sections}))
