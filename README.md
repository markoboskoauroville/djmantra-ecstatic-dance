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

## Deploy

Cloudflare Pages, project `djmantra`. The `main` branch is the source of truth.

## Contact

marko.bosko@auroville.community
