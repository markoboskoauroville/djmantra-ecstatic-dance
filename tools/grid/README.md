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
