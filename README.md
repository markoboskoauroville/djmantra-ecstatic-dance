# DJ Mantra — ecstatic dance

Bilingual (HR / EN) one page bio for **Marko Boško / DJ Mantra**, written for the ecstatic dance community in Croatia.

Covers the percussion work and Tribal Jam Orchestra, the seven years in Auroville and the Sun Moon Yoga method, the lineage of teachers, and the three part arc of an evening, shown as three illustrated acts with his modules in each: I Opening (yoga and pranayama, guided meditation, vowel toning), II The dance (DJ set, live drums), III Closing (sound bath). Galleries of **Tribal Jam Orchestra** (Zagreb, since 2011) and **Tribal Jam Collective** (KalaBhumi Studio, Auroville) open in a lightbox.

## Technical notes

* One static `index.html`. No framework, no build step, no dependencies, no tracking.
* Bilingual dictionary compiled into the page. Croatian is the default, choice persisted in `localStorage` with a cookie fallback.
* Images are self hosted in `assets/` (`assets/tjo/`, `assets/tjc/`, `act-*.jpg`), lazy loaded below the fold.
* Headings in **Spectral** (Google Fonts), chosen 5.10.2026 because it draws č ć š ž đ properly; Cormorant Garamond drew a loose floating caron on ž and was dropped.
* A version label sits top left (`v3`), bumped on every change, so a cached copy is easy to tell from the current one.
* Responsive to 360px, `prefers-reduced-motion` respected.

## The demo mix player (v9, 6.10.2026)

* Right under the hero: the ecstatic dance demo mix of 4.10.2026 (1:53:24) in a deck drawn after djay Pro's waveform: a scrolling three band waveform (low red, mid amber, high cyan) with a centre playhead, an overview strip to jump anywhere, the 26 track playlist.
* `assets/mix/mix.m3u8` + 683 fMP4 segments (AAC 160 kbps, 10 s each): Cloudflare Pages refuses files over 25 MiB, so the mix is HLS. hls.js 1.6.16 from cdnjs where Media Source exists, native HLS otherwise.
* `assets/mix/wave.bin`: low, mid, high, peak as bytes at 25 per second (scipy Butterworth bands at 200 Hz and 2.5 kHz).
* `assets/mix/tracks.json`: [start seconds, title, artist, phase]. Start times found by cross correlating each source file in ~/Music/DJMantra against the mix (20 tracks, score above 0.95); the other six from djay's history minus its 32 s lag. The last five were remixed on Android, so their order differs from djay's Mac history (Shallow Water before Arabesque 3).
* Phase = the six part ecstatic dance wave of his own library folders (01 Arrival/Ground, 02 Awakening, 03 Building, 04 Peak, 05 Release, 06 Stillness); each section is underlined in its phase color, with a color guide.
* The original 320 kbps file is a GitHub Release asset (`mix-2026-10-04`), linked as the download.

## Sounding Silence, the album player (v10, 6.10.2026)

* Under the "who" section, which names the album: Mantreshvar, Sounding Silence, ten mantras and the bonus Window of Wisdom.
* Audio from his masters in ~/Music/DJMantra/Sounding Silence (the same songs as the Drive folder 1fljam_WMaYfIvjAvmh8jyp9TQhO8L90X), AAC 192 kbps in `assets/ss/`.
* `assets/ss/album.json`: title, duration, a one line Croatian summary, his full English text from the YouTube playlist PLCxh3j1gI2nqVCXRWbWYWKMN7l_kVwa9d (yt-dlp --write-info-json), the art (album cover, the bonus has its own), a three band waveform of 480 bins.
* The album and the mix never play together (a `mantra-play` event pauses the other).

## The DJ Mantra app section (v59, 23.10.2026; v15 was a progress list)

* "Learn to DJ by ear", before Contact: the DJ Mantra app for Android (repository markoboskoauroville/djmantra_app,
  the Mixxx engine on phones) presented as finished, a summary of its own page https://djmantraapp.pages.dev: what it
  teaches, eight features, what it needs, and three links: the app's page, the latest APK (the GitHub Release
  `android-latest`) and the source code. HR and EN in the page's dictionary.
* When the app page changes, read it again and update this summary (Marko, 23.10.2026: "read the page about DJ app and
  make a summary here and also link to that page"). The old `assets/app/progress.json` is gone.

## Deploy

Cloudflare Pages, project `djmantra`, https://djmantra.pages.dev.

* **Automatic (since v16, 8.10.2026):** every push to `main` runs `.github/workflows/deploy.yml`, which publishes the page with wrangler. It needs the repository secrets `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID`. A push to any other branch publishes nothing, so work on a branch is merged into `main` to go live. The Actions tab shows each deploy; it can also be started by hand there (Run workflow).
* **By hand:** `npx wrangler pages deploy . --project-name djmantra --branch main` with CLOUDFLARE_ACCOUNT_ID and the token from ~/Downloads/API/Cloudflare.api.txt (the last line of 30+ token characters, as SHOP_FINDER/deploy.sh reads it).

## Contact

marko.bosko@auroville.community

## The player in the DJ Mantra app's look, with a beat and section counter (v28, 18.10.2026)

* The deck uses the app's palette (`res/qml/djmantra/Style.qml`: navy #0B1026, one yellow accent #FFD54A, the knobs'
  band colours LOW red, MID green, HIGH blue) and starts with the app's top bar: "DJ Mantra **app**" and its yellow clock,
  linking to the app section.
* Under the waveform, the app's Phrasing view: BPM, bar and beat (four beat lights), the 8 bars of the phrase, and the
  next section with the beats and time to it ("DROP · 24 beats · 0:12"); tracks without a steady beat say FREE TIME and
  count the time to the next change. The big waveform shows the beat grid (bar lines brighter, 8-bar phrases yellow) and
  the sections as yellow flags.
* `assets/mix/beats.json`, one entry per track: `bpm` (0 = no steady beat), `down` (a downbeat), `phrase` (the start of an
  8-bar phrase), `sections` [[time, DROP / BREAKDOWN / BUILD / CHANGE]]. Made from the HLS audio: librosa's tempo, then
  the grid fitted to the kick (below 150 Hz), the downbeat and phrase where the bands change most, the sections where the
  16 beats after a phrase line differ most from the 16 before (wave.bin bands). Approximate: it is for listening, the
  app is for DJing.
* **`assets/mix/grid.json` (when present) replaces it**: the exact grid from rekordbox (dynamic tempo + phrase analysis,
  checked in djay Pro) made on Marko's Mac: `beats` [[t, beat 1-4]] for the whole mix, `sections` [[t, INTRO / UP /
  DOWN / CHORUS / VERSE / BRIDGE / OUTRO, bars]], `free` [[t0, t1]] without a steady beat. The player reads it first and
  falls back to beats.json.

## Analyse your song (v38, 19.10.2026)

* `#analyse`, after the song-structure guide: pick or drop a song and get its BPM, key (with Camelot), length, the
  sections (INTRO, BREAKDOWN, BUILD-UP, DROP, MAIN, OUTRO) with their bars, the guide's short code and a three band
  waveform with the sections over it.
* Nothing leaves the browser: `decodeAudioData` decodes, the mono samples are handed (transferred) to
  `assets/analyzer/worker.js`, which runs `assets/analyzer/djmantra_analyzer.wasm` (rbxport's analysis plus DJ Mantra's
  section names, source and build in `tools/analyzer/`), zeroes the samples; the page then ends the worker.
* About 5 s for a 3-minute song in desktop Chromium; up to 20 minutes per song.
* v39: the analysed song plays on the page: play / pause, previous / next section, LOOP the section, click the
  waveform or a section to jump, NOW / NEXT with the bar.beat count, the beat and 8-bar phrase lights and the bars and
  time to the next section. It plays the visitor's own file through an object URL (nothing is uploaded or copied);
  the URL is released when another song is picked or the page is left.
* v40: the section playground and the dot-matrix display. One button per section finder of the DJ Mantra app
  (Settings -> SECTIONS: ENERGY CHANGES, the default, PHRASES, ENERGY ONLY, CLASSIC 8-BAR, RBXPORT) and SENSITIVITY 1-5,
  ported from the app's `sectiondetector.cpp` to `tools/analyzer/src/algorithms.rs`. The analysis computes every
  finder at every sensitivity at once (the song's audio is gone afterwards), so a button only picks a ready answer.
  The names are labelled a guess. Under the waveform the app's dot-matrix display (`MatrixDisplay.qml`, the 5x7
  `PixelFont.qml`): time left, bar.beat from the section start, the countdown to the next section and one cell per beat
  of the phrase (8 / 16 / 32 BEATS).

## The toning voice, slow, and the breathing knob (v48, 21.10.2026)

* One voice only, Orion (Marko: "use only Orion voice, that is all"), read much slower: `tools/toning/slow_toning.py`
  stretches each rung of `tools/toning/readings/orion/` to 80 % speed (rubberband, pitch and formants kept), opens 3 s
  after every sentence and 1.2 s after every phrase, 6 s after a rung, 14 s after Silence; then writes
  `assets/toning/orion.mp3`, its waveform and the chapters in `toning.json`. 10:31.
* The BACKGROUND knob's LED ring crossfades its colour between elements with the decks' gains and breathes six times a
  minute (4 s in, 6 s out); with `prefers-reduced-motion` it only crossfades.
* v49: the only background is Marko's own song "Toning A U I O DJ MANTRA WEB PAGE", cut per element by
  `tools/toning/build_bg.py` (AAC 320 kbps, the default, MANTRA_MANIFEST modules/aac-320.md).

## Two sessions build this page (21.10.2026)

The Mac session and the cloud session work together and talk both ways; read `COLLABORATION.md` first.
