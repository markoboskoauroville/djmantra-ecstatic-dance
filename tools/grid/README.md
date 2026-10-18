# The demo mix grid (18.10.2026)

`assets/mix/grid.json` for the player: every beat of the mix with its number in the bar, rekordbox's phrases, and the
stretches without a grid. Made on Marko's Mac from the original file
`~/Music/djay/Recordings/DJ Mantra For Indra - Ecstatic Dance Demo Mix 04-10-26.mp4` (AAC 320 kbps, 6803.9 s).

- **Beats: djay Pro** (Marko: "we use the beat grid from DJ Pro to get the right BPM as the mix is progressing").
  djay's neural tracker (ARDeepBeatTrackerModel1011_9) follows the tempo: 13,341 beats, read from its
  `.djayMetadata` (`djay_metadata.py`). Its beats sit on the kick in every track with a kick.
- **Bar numbers and sections: rekordbox 7** (dynamic analysis + phrase analysis, ANLZ0000.DAT/EXT read by
  `rekordbox_phrases.py`). rekordbox's grid is half a beat early in tracks 8-13 (Miss You to DMT), so only its count
  is used; its 286 phrases are snapped to djay's downbeats (263 land on one; the rest are in free time or more than
  0.7 s from a djay downbeat).
- **Time bases:** ffmpeg = djay = the original file. rekordbox reads 45 ms late (it keeps the 2112-sample AAC encoder
  delay). The site's HLS runs 21 ms after the original (cross-correlation at 20, 60, 120 s: constant). grid.json is on
  the player's timeline: djay + 0.021 s.
- **Free:** 648.3-883.8 s (Ólafur Arnalds 03:06, no kick; djay counts it at 182 BPM, rekordbox too, but it is piano)
  and 6520.2 s to the end (Shallow Water's fade, Arabesque 3, Sunsets: almost no onsets).

`python3 -I make_grid.py` next to `mix_djay.json` (from djay_metadata.py), `rb/ANLZ0000.DAT|EXT` and nothing else.
`assets/mix/rekordbox-mix.xml` is built from rekordbox's ANLZ files in the shape of its XML export (TEMPO per tempo
change, in rekordbox's time base) plus the phrases; rekordbox's own Export Collection was not run.

## The section names (v32, 18.10.2026)

Marko: *"name the sections ... intro, breakdown, etc. All the standard names for this kind of music"*, and *"the easiest
test is when the beat stops and then comes back. Between these two points, there is one section."* rekordbox's phrases
(UP / DOWN / CHORUS, kept as `sections_rekordbox`) did not follow the kick, so `label.py` cuts the mix by the beat:
`feats.py` measures every bar (between djay downbeats): loudness, bass, mids, highs and the kick (low band <150 Hz on
the beats). A bar is beatless when its kick is 9 dB under the track's usual kick (its 70th percentile); a beatless run
under 4 bars is a fill, a beat run under 2 bars inside silence a stray hit. Then:

| Name | When |
|---|---|
| INTRO | the first beatless stretch of the mix or after free time; the beat that returns after an OUTRO (the next track coming in), 16 bars |
| BREAKDOWN | the beat stops inside a track |
| BUILD-UP | the end of a breakdown where the energy climbs bar by bar, 4+ bars and 3+ dB |
| DROP | the beat comes back after a breakdown or build-up, its first 16 bars |
| GROOVE | the beat running: after the drop, at a new track over a beat that never stopped |
| OUTRO | the beat stops in the last 30 s before the next track |
| AMBIENT | free time, no beat at all |

110 sections: 37 GROOVE, 31 BREAKDOWN, 31 DROP, 3 BUILD-UP, 3 INTRO, 3 OUTRO, 2 AMBIENT.
