# The educational player's songs (v34, 18.10.2026)

Marko: *"take the songs from my set to give an example. One instrumental song, only one, the best section you can
assess. One vocal song ... publish them in the educational player."* From his library (Tidal M4A), re-encoded AAC
192 kbps and streamed as HLS (`assets/edu/<id>/index.m3u8`, 10 s segments: Cloudflare Pages answers no byte
ranges, so a single file could not be jumped in; measured 18.10.2026), with a 3-band waveform (25 fps, the layout of the mix's wave.bin) and `edu.json`.

- **Secret ID** (Moojo, Da Capo), the instrumental: djay Pro's beats (120 BPM, 204 bars). Read per bar from the kick
  (<150 Hz onsets), bass, mids and highs: bars 1–16 kick and bass only, 17–48 hi-hats in (+13 dB highs) but the mids
  5 dB under the main part: a 48-bar intro (16 + 32). Breakdown 49–64, build-up 65–84 (highs climb ~1 dB a bar, bass cut
  in the last four), drop 85, main to 132; breakdown 133–148, build-up 149–156, drop 157, main to 188; outro 189–204 at
  exactly the intro's levels. Code I16 · I32 · B36 · M48 · B24 · M32 · O16.
- **I Follow Rivers** (Sean Finn, Play!On), the vocal: the voice separated with Demucs and read by Whisper with word
  times (MANTRA_VOICE /hear?words=1): verse (13 bars from the first second), pre-chorus 8 (beat stops), chorus 8, 8 bars
  instrumental, verse 8, pre-chorus 4, chorus 8, bridge 8 (beatless echo of the hook), chorus 16 to the end, no outro.
- Picked over Rapture Pt.II (one 64-bar breakdown), DMT (four breakdowns), Back To The Roots, Rej; Falling and Halele
  are mostly their hook repeated.
- The All-In-One structure analyser (~/.venvs/allin1) does not run on this Mac (natten needs CUDA).

## The stems (v36)

Ableton Live 12.4.6 separated both songs (vocals, drums, bass, others; High Speed, Live's default) on 18.10.2026, the
Stem Separation app's steps run by hand on its first run. Live writes them into the set's project; for an unsaved set
that is `~/Music/Ableton/Live Recordings/<date> Temp Project/Samples/Processed/Stems/<song> [time] (Vocals).wav` etc.
Copies in ~/Music/Stems/<song>/. `build_stems.py` writes `<id>.stems.bin` (see its header).
