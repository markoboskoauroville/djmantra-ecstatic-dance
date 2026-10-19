//! DJ Mantra's song analysis for djmantra.pages.dev (Marko 19.10.2026: "add a section, analyze your
//! song ... analyze it for BPMs and sections ... And the key"). Built to WebAssembly: the page decodes
//! the visitor's file in the browser, hands the samples here and frees them; nothing is uploaded.
//!
//! - BPM, beat grid, downbeat, phrase starts and key: rbxport's rbl-analysis (vendor/, Chris Le,
//!   GPL-2.0-or-later), the "Rekordbox" preset (one constant tempo, 70-180 BPM), as DJ Mantra V91 uses.
//! - Section names: DJ Mantra's own rules (djmantra_app src/analyzer/sectionnames.cpp, ported here),
//!   the names of the page's "Kako je pjesma građena": INTRO, BREAKDOWN, BUILD-UP, DROP, MAIN, OUTRO.

pub mod algorithms;

use rbl_analysis::downbeat;
use rbl_analysis::{analyse_with, AnalysisPreset};

/// One bar, measured for the names: the level, the kick (the two lowest bands at the beats) and the
/// highs, in dB
#[derive(Clone, Copy, Default)]
pub struct Bar {
    pub energy: f64,
    pub kick: f64,
    pub high: f64,
}

const FULL_WITHIN_DB: f64 = 11.0;
const BEATLESS_DB: f64 = 9.0;
const BUILD_UP_RISE_DB: f64 = 4.3;
const FILL_BARS: usize = 4;

fn percentile(values: &[f64], p: f64) -> f64 {
    if values.is_empty() {
        return 0.0;
    }
    let mut v = values.to_vec();
    v.sort_by(|a, b| a.partial_cmp(b).unwrap_or(std::cmp::Ordering::Equal));
    let i = ((p / 100.0 * (v.len() - 1) as f64) + 0.5) as usize;
    v[i.min(v.len() - 1)]
}

/// The parts that start at `starts` (bar indices) named; see sectionnames.h in the app for the
/// rules and how they were measured (82 songs against rekordbox's phrases)
pub fn name_sections(bars: &[Bar], starts: &[usize]) -> Vec<(usize, &'static str)> {
    let n = bars.len();
    let mut out: Vec<(usize, &'static str)> = Vec::new();
    if n == 0 {
        return out;
    }
    let mut starts: Vec<usize> = starts.iter().copied().filter(|&b| b < n).collect();
    starts.push(0);
    starts.sort_unstable();
    starts.dedup();
    let energy: Vec<f64> = bars.iter().map(|b| b.energy).collect();
    let kick: Vec<f64> = bars.iter().map(|b| b.kick).collect();
    let usual_kick = percentile(&kick, 80.0);
    let beatless: Vec<bool> = bars.iter().map(|b| b.kick < usual_kick - BEATLESS_DB).collect();
    if beatless.iter().filter(|&&b| !b).count() < 8 {
        out.push((0, "AMBIENT"));
        return out;
    }
    let main_level = percentile(&energy, 75.0);
    struct Part {
        from: usize,
        to: usize,
        beatless: f64,
        energy: f64,
    }
    let parts: Vec<Part> = starts
        .iter()
        .enumerate()
        .map(|(i, &from)| {
            let to = starts.get(i + 1).copied().unwrap_or(n);
            let len = (to - from) as f64;
            Part {
                from,
                to,
                beatless: (from..to).filter(|&b| beatless[b]).count() as f64 / len,
                energy: (from..to).map(|b| bars[b].energy).sum::<f64>() / len,
            }
        })
        .collect();
    let full: Vec<bool> = parts.iter().map(|p| p.energy >= main_level - FULL_WITHIN_DB && p.beatless < 0.5).collect();
    let first = full.iter().position(|&f| f);
    let last = full.iter().rposition(|&f| f);
    let mut previous = "";
    for (i, part) in parts.iter().enumerate() {
        let length = part.to - part.from;
        let label = match (first, last) {
            (None, _) | (_, None) => "INTRO",
            (Some(f), _) if i < f => "INTRO",
            (_, Some(l)) if i > l => "OUTRO",
            _ if part.beatless >= 0.5 && length >= FILL_BARS => {
                let tail = length.min(8);
                let rising = tail >= 2 && bars[part.to - 1].high - bars[part.to - tail].high >= BUILD_UP_RISE_DB;
                if rising && length <= 8 {
                    "BUILD-UP"
                } else if rising {
                    out.push((part.from, "BREAKDOWN"));
                    out.push((part.to - 8, "BUILD-UP"));
                    previous = "BUILD-UP";
                    continue;
                } else {
                    "BREAKDOWN"
                }
            }
            _ => {
                if previous == "BREAKDOWN" || previous == "BUILD-UP" {
                    "DROP"
                } else {
                    "MAIN"
                }
            }
        };
        out.push((part.from, label));
        previous = label;
    }
    let mut merged: Vec<(usize, &'static str)> = Vec::new();
    for part in out {
        if merged.last().map_or(true, |m| m.1 != part.1) {
            merged.push(part);
        }
    }
    merged
}

/// The whole analysis of mono samples, as JSON for the page
pub fn analyse_json(samples: &[f32], sample_rate: u32) -> String {
    let duration = samples.len() as f64 / f64::from(sample_rate.max(1));
    let analysis = analyse_with(samples, sample_rate, AnalysisPreset::Rekordbox.options());
    let tempo = &analysis.tempo;
    let beats: Vec<f64> = tempo.beats.iter().map(|b| f64::from(b.time_ms) / 1000.0).collect();
    let first_downbeat = tempo.beats.iter().position(|b| b.beat_number == 1).unwrap_or(0);

    // the bars from the first downbeat, measured as the app measures them
    let mut sections_json = Vec::new();
    let bar_starts: Vec<f64> = beats.iter().skip(first_downbeat).step_by(4).copied().collect();
    if bar_starts.len() >= 2 && !analysis.frames.is_empty() {
        const DB: f64 = 4.342944819; // ln power to dB
        let profiles = downbeat::beat_profiles_from(&analysis.frames, sample_rate, &bar_starts);
        let frame_rate = f64::from(sample_rate) / downbeat::HOP as f64;
        let low_at = |secs: f64| {
            let f = (secs * frame_rate).round() as i64;
            let mut best = -1e9_f64;
            for g in f - 2..=f + 2 {
                if g >= 0 && (g as usize) < analysis.frames.len() {
                    let frame = &analysis.frames[g as usize];
                    best = best.max(frame[0].max(frame[1]));
                }
            }
            best
        };
        let bars: Vec<Bar> = profiles
            .iter()
            .enumerate()
            .map(|(b, p)| {
                let at: Vec<f64> = beats.iter().skip(first_downbeat + b * 4).take(4).map(|&t| low_at(t)).collect();
                Bar {
                    energy: p.iter().sum::<f64>() / downbeat::BANDS as f64 * DB,
                    kick: if at.is_empty() { -1e9 } else { at.iter().sum::<f64>() / at.len() as f64 * DB },
                    high: (p[9] + p[10] + p[11]) / 3.0 * DB,
                }
            })
            .collect();
        let bar_secs = bar_starts[1] - bar_starts[0];
        let starts: Vec<usize> = analysis
            .phrase_starts
            .iter()
            .map(|s| ((s - bar_starts[0]) / bar_secs).round())
            .filter(|&b| b > 0.0)
            .map(|b| b as usize)
            .collect();
        let named = name_sections(&bars, &starts);
        for (i, (from, label)) in named.iter().enumerate() {
            let to = named.get(i + 1).map_or(bars.len(), |n| n.0);
            let secs = if *from == 0 { 0.0 } else { bar_starts[*from] };
            sections_json.push(format!("{{\"secs\":{secs:.3},\"name\":\"{label}\",\"bars\":{}}}", to - from));
        }
    }

    // a small three-band overview to draw (600 columns, the loudest of each stretch)
    let columns = &analysis.waveform.columns;
    let mut overview = Vec::new();
    if !columns.is_empty() {
        let n = 600.min(columns.len());
        for i in 0..n {
            let from = i * columns.len() / n;
            let to = ((i + 1) * columns.len() / n).max(from + 1);
            let mut c = [0u8; 4];
            for col in &columns[from..to] {
                c[0] = c[0].max(col.low);
                c[1] = c[1].max(col.mid);
                c[2] = c[2].max(col.high);
                c[3] = c[3].max(col.peak);
            }
            overview.push(format!("[{},{},{},{}]", c[0], c[1], c[2], c[3]));
        }
    }
    // the app's section finders (the page's playground), every one at every sensitivity: the song is gone
    // after this call, so the page switches between ready answers
    let cps = analysis.waveform.columns_per_sec.max(1.0);
    let points: Vec<[f64; 3]> =
        columns.iter().map(|c| [f64::from(c.low), f64::from(c.mid), f64::from(c.high)]).collect();
    let beats_pts: Vec<f64> = beats.iter().map(|b| b * cps).collect();
    let as_json = |list: Vec<(f64, &'static str, usize)>| {
        let parts: Vec<String> = list
            .into_iter()
            .map(|(secs, name, bars)| format!("{{\"secs\":{secs:.3},\"name\":\"{name}\",\"bars\":{bars}}}"))
            .collect();
        format!("[{}]", parts.join(","))
    };
    let mut algos = Vec::new();
    for (id, algorithm) in [
        ("energy", algorithms::Algorithm::Energy),
        ("phrases", algorithms::Algorithm::Phrases),
        ("energyOnly", algorithms::Algorithm::EnergyOnly),
    ] {
        let levels: Vec<String> = (1..=5)
            .map(|level| {
                let found = algorithms::section_beats_v3(&points, &beats_pts, 4, algorithm, level);
                as_json(algorithms::name_found(&points, &beats_pts, &beats, &found, 4))
            })
            .collect();
        algos.push(format!("\"{id}\":[{}]", levels.join(",")));
    }
    let classic = algorithms::section_beats_v2(&points, &beats_pts, 4);
    algos.push(format!("\"classic\":[{}]", as_json(algorithms::name_found(&points, &beats_pts, &beats, &classic, 4))));
    algos.push(format!("\"rbxport\":[[{}]]", sections_json.join(",")));

    let key = analysis.key.as_ref().map_or("null".to_string(), |k| {
        format!("{{\"name\":\"{}\",\"camelot\":\"{}\",\"minor\":{}}}", k.name, k.camelot(), k.minor)
    });
    let beats_json: Vec<String> = beats.iter().map(|b| format!("{b:.3}")).collect();
    format!(
        "{{\"bpm\":{:.2},\"confidence\":{:.3},\"duration\":{:.3},\"firstDownbeat\":{},\"beats\":[{}],\"key\":{},\"sections\":[{}],\"phraseStarts\":[{}],\"overview\":[{}],\"peak\":{:.4},\"algos\":{{{}}}}}",
        tempo.bpm,
        tempo.confidence,
        duration,
        first_downbeat,
        beats_json.join(","),
        key,
        sections_json.join(","),
        analysis.phrase_starts.iter().map(|s| format!("{s:.3}")).collect::<Vec<_>>().join(","),
        overview.join(","),
        analysis.peak,
        algos.join(",")
    )
}

// ------------------------------------------------------------------ the page's calls (WebAssembly)

static mut RESULT: Vec<u8> = Vec::new();

/// Room for `count` samples; the page writes the decoded mono song there
#[no_mangle]
pub extern "C" fn alloc_samples(count: usize) -> *mut f32 {
    let mut buffer = vec![0.0_f32; count];
    let ptr = buffer.as_mut_ptr();
    std::mem::forget(buffer);
    ptr
}

/// Frees the samples (the page calls it right after `analyse`, so no copy of the song stays)
#[no_mangle]
pub unsafe extern "C" fn free_samples(ptr: *mut f32, count: usize) {
    if !ptr.is_null() {
        let mut buffer = Vec::from_raw_parts(ptr, count, count);
        buffer.fill(0.0);
        drop(buffer);
    }
}

/// Analyses the samples; the JSON is at `result_ptr()`, `result_len()` bytes long
#[no_mangle]
pub unsafe extern "C" fn analyse(ptr: *const f32, count: usize, sample_rate: u32) -> usize {
    let samples = std::slice::from_raw_parts(ptr, count);
    let json = analyse_json(samples, sample_rate);
    let result = &mut *std::ptr::addr_of_mut!(RESULT);
    *result = json.into_bytes();
    result.len()
}

#[no_mangle]
pub unsafe extern "C" fn result_ptr() -> *const u8 {
    (*std::ptr::addr_of!(RESULT)).as_ptr()
}

#[no_mangle]
pub unsafe extern "C" fn result_len() -> usize {
    (*std::ptr::addr_of!(RESULT)).len()
}
