# Song analyser (djmantra.pages.dev, "Analiziraj svoju pjesmu", v38)

The page's "Analyse your song" section: a visitor picks a song, the browser decodes it, a Web Worker
(`assets/analyzer/worker.js`) runs this crate compiled to WebAssembly (`assets/analyzer/djmantra_analyzer.wasm`),
the samples are zeroed and the worker is ended. Nothing is uploaded or stored.

- `vendor/rbl-analysis`: rbxport 1.9.0's analysis crate (https://github.com/chrisle/rbxport, Chris Le,
  GPL-2.0-or-later), the "Rekordbox" preset (one tempo, 70-180 BPM): BPM, beat grid, downbeat, phrase starts, key.
  Changed: `src/lib.rs` runs the stages one after another (no threads in a browser's WebAssembly) and also returns
  the phrase starts and band frames; `downbeat::HOP` is public.
- `src/lib.rs`: the section names of DJ Mantra's app (djmantra_app `src/analyzer/sectionnames.cpp`, ported):
  INTRO, BREAKDOWN, BUILD-UP, DROP, MAIN, OUTRO, AMBIENT; the JSON for the page; the WebAssembly calls
  (`alloc_samples`, `analyse`, `free_samples`, `result_ptr`, `result_len`; no imports).
- Build: `./build.sh` (needs `rustup target add wasm32-unknown-unknown`).
- Check natively: `ffmpeg -i song.mp3 -ac 1 -ar 44100 -f f32le - | cargo run --release --example analyse_file`.
  The WebAssembly gives byte-identical JSON (checked in Node on El Layali, 19.10.2026).
