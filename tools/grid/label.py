"""Sections of the demo mix by the beat (Marko, 18.10.2026: "the easiest test is when the beat stops and then comes back.
Between these two points, there is one section"), named the way DJs and producers name them."""
import json, numpy as np
P = 0.021
g = json.load(open('grid.json')); b = np.array(json.load(open('bars.json'))); tr = json.load(open('tracks.json'))
st = [t[0] for t in tr] + [6803.9]
T0, T1 = b[:, 0], b[:, 1]
full = b[:, 2]; kick = 20 * np.log10(b[:, 6] + 1e-6)
trk = np.array([max(i for i in range(len(tr)) if st[i] <= t + 1e-6) for t in T0])
# the track's own beat: its 70th percentile kick; a bar is beatless 9 dB under it
ref = {i: np.percentile(kick[trk == i], 70) for i in set(trk)}
beat = np.array([kick[j] >= ref[trk[j]] - 9 for j in range(len(b))])
# gaps between bars (free time) break runs
gap = np.r_[True, T0[1:] - T1[:-1] > 0.5]

def runs(x):
    out, s = [], 0
    for j in range(1, len(x) + 1):
        if j == len(x) or x[j] != x[s] or gap[j]:
            out.append([s, j, bool(x[s])]); s = j
    return out
# a beatless stretch shorter than 4 bars is a fill; a beat stretch shorter than 2 bars inside silence is a stray hit
for minlen, val in ((4, False), (2, True)):
    for s, e, v in runs(beat):
        if v == val and e - s < minlen and not gap[s]: beat[s:e] = not val
R = runs(beat)

def rise(s, e):
    """bars at the end of a beatless run where the energy climbs: the build-up (riser, snare roll)"""
    k = e
    while k - 1 > s and full[k - 1] >= full[k - 2] - 0.3: k -= 1
    return k if e - k >= 4 and full[e - 1] - full[k] >= 3 else e

secs = []          # [start time, name]
prev = None
for n, (s, e, v) in enumerate(R):
    t0, t1 = T0[s], T1[e - 1]; i = trk[s]
    starts_track = any(abs(t0 - x) < 40 for x in st[:-1]) or gap[s]
    near_end = (t1 > st[i + 1] - 30) or (e < len(b) and gap[e]) or e == len(b)
    if not v:
        if starts_track and (prev is None or gap[s]):
            name = 'INTRO'
        elif near_end and not starts_track:
            name = 'OUTRO'
        else:
            name = 'BREAKDOWN'
        k = rise(s, e) if name != 'OUTRO' else e
        secs.append([t0, name])
        if k < e: secs.append([T0[k], 'BUILD-UP'])
        prev = 'OUTRO' if name == 'OUTRO' else ('BREAK' if k == e else 'BUILD')
    else:
        if prev == 'OUTRO':
            # the beat that comes back after an outro is the next track's: its intro, then its groove
            secs.append([t0, 'INTRO'])
            if e - s > 24: secs.append([T0[s + 16], 'MAIN'])
        elif prev in ('BREAK', 'BUILD'):
            # the beat comes back: the drop, 16 bars of it, then the groove
            secs.append([t0, 'DROP'])
            if e - s > 24: secs.append([T0[s + 16], 'MAIN'])
        else:
            secs.append([t0, 'MAIN'])
        prev = 'BEAT'
# a new track coming in on a beat that never stopped: its groove starts at the track's own start
for x in st[1:-1]:
    if not any(abs(x - t) < 20 for t, _ in secs):
        j = np.searchsorted(T0, x)
        if j < len(b) and beat[j] and not gap[j]: secs.append([T0[j], 'MAIN'])
# the free stretches have no beat at all
for a, z in g['free']: secs.append([a - P, 'AMBIENT'])
secs.sort()
# merge equal neighbours
out = []
for t, nm in secs:
    if out and out[-1][1] == nm and nm != 'MAIN': continue
    out.append([t, nm])
# bars per section from the downbeats
D = np.array([x[0] for x in g['beats'] if x[1] == 1]) - P
res = []
for (t, nm), (t2, _) in zip(out, out[1:] + [[6803.9, None]]):
    nb = int(((D >= t - 0.05) & (D < t2 - 0.05)).sum())
    res.append([round(t + P, 3), nm, 0 if nm == 'AMBIENT' else max(nb, 1)])
json.dump(res, open('sections_new.json', 'w'))
if __name__ == '__main__':
    import collections
    print(len(res), 'sections', collections.Counter(r[1] for r in res))
    for r in res:
        i = max(k for k in range(len(tr)) if st[k] <= r[0])
        print(f"{r[0]:8.1f} {int(r[0]//60):3d}:{int(r[0]%60):02d}  {r[1]:10s} {r[2]:4d} bars   {tr[i][1][:30]}")
