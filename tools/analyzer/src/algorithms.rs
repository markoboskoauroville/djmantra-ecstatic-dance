//! The section finders of the DJ Mantra app (djmantra_app src/engine/controls/sectiondetector.cpp, Settings ->
//! SECTIONS), ported for the page's playground (Marko 19.10.2026: "use algorithms which are inside my DJ android
//! app ... each button for each algorithm on the website so user can experiment with their own songs").
//!
//! The app reads Mixxx's waveform (low / mid / high per point); here the points are rbxport's waveform columns
//! (150 a second, 0..255 per band). Both finders scale the bands to their peaks, so only the shape counts.
//! - ENERGY CHANGES (the app's default), PHRASES, ENERGY ONLY: `section_beats_v3`
//! - CLASSIC 8-BAR: `section_beats_v2`
//! The names come as in the app's detectSections: bars measured from the waveform, then `crate::name_sections`.

use crate::{name_sections, Bar};

type Bands = [f64; 3];

const FLOOR: f64 = 4.0;

#[derive(Clone, Copy, PartialEq, Eq)]
pub enum Algorithm {
    Energy,
    Phrases,
    EnergyOnly,
}

fn span_mean(points: &[Bands], from: f64, to: f64) -> Bands {
    let size = points.len() as i64;
    let a = (from.round() as i64).clamp(0, size - 1);
    let b = (to.round() as i64).clamp(a + 1, size);
    let mut sum = [0.0; 3];
    for p in &points[a as usize..b as usize] {
        for c in 0..3 {
            sum[c] += p[c];
        }
    }
    for v in &mut sum {
        *v /= (b - a) as f64;
    }
    sum
}

fn log_bands(b: Bands) -> Bands {
    [b[0].ln_1p(), b[1].ln_1p(), b[2].ln_1p()]
}

fn median(v: &[f64]) -> f64 {
    if v.is_empty() {
        return 0.0;
    }
    let mut v = v.to_vec();
    v.sort_by(|a, b| a.partial_cmp(b).unwrap_or(std::cmp::Ordering::Equal));
    let n = v.len();
    if n % 2 == 1 {
        v[n / 2]
    } else {
        0.5 * (v[n / 2 - 1] + v[n / 2])
    }
}

/// numpy.percentile (linear)
fn percentile(v: &[f64], p: f64) -> f64 {
    if v.is_empty() {
        return 0.0;
    }
    let mut v = v.to_vec();
    v.sort_by(|a, b| a.partial_cmp(b).unwrap_or(std::cmp::Ordering::Equal));
    let pos = (v.len() - 1) as f64 * p / 100.0;
    let lo = pos.floor() as usize;
    let hi = (lo + 1).min(v.len() - 1);
    v[lo] + (v[hi] - v[lo]) * (pos - lo as f64)
}

/// Foote's checkerboard kernel (Gaussian tapered) along the diagonal, >= 0, peak 1
fn checker_novelty(ssm: &[Vec<f64>], half: usize) -> Vec<f64> {
    let n = ssm.len() as i64;
    let size = 2 * half;
    let g: Vec<f64> = (0..size)
        .map(|i| {
            let x = -1.5 + 3.0 * i as f64 / (size as f64 - 1.0).max(1.0);
            (-0.5 * x * x).exp()
        })
        .collect();
    let mut nov = vec![0.0; n as usize];
    let mut peak = 0.0_f64;
    for i in 0..n {
        let mut sum = 0.0;
        for r in 0..size {
            let row = (i - half as i64 + r as i64).clamp(0, n - 1) as usize;
            for k in 0..size {
                let col = (i - half as i64 + k as i64).clamp(0, n - 1) as usize;
                let sign = if (r < half) == (k < half) { 1.0 } else { -1.0 };
                sum += g[r] * g[k] * sign * ssm[row][col];
            }
        }
        nov[i as usize] = sum.max(0.0);
        peak = peak.max(nov[i as usize]);
    }
    for v in &mut nov {
        *v /= peak + 1e-9;
    }
    nov
}

/// The downbeat (the beat phase with the largest bar-to-bar band change), the bars' first beats, the bands per bar
/// (0..230 of each band's peak) and their quarters (log)
struct BarData {
    bar_beat: Vec<usize>,
    b3: Vec<Bands>,
    quarters: Vec<[f64; 12]>,
    pulse: Vec<f64>,
}

fn bar_data(points: &[Bands], beats: &[f64], bpb: usize) -> Option<BarData> {
    if points.is_empty() || beats.len() < 16 * bpb {
        return None;
    }
    let mut downbeat = 0;
    let mut best = -1.0;
    for p in 0..bpb {
        let mut change = 0.0;
        let mut previous: Option<Bands> = None;
        let mut i = p;
        while i + bpb < beats.len() {
            let now = log_bands(span_mean(points, beats[i], beats[i + bpb]));
            if let Some(prev) = previous {
                for c in 0..3 {
                    change += (now[c] - prev[c]).abs();
                }
            }
            previous = Some(now);
            i += bpb;
        }
        if change > best {
            best = change;
            downbeat = p;
        }
    }
    let bar_beat: Vec<usize> = (downbeat..).step_by(bpb).take_while(|i| i + bpb < beats.len()).collect();
    let nb = bar_beat.len();
    if nb < 16 {
        return None;
    }
    let mut b3 = vec![[0.0; 3]; nb];
    let mut quarters = vec![[0.0; 12]; nb];
    let mut pulse = vec![0.0; nb];
    let mut peak: Bands = [1e-9; 3];
    for k in 0..nb {
        let from = beats[bar_beat[k]];
        let to = beats[bar_beat[k] + bpb];
        b3[k] = span_mean(points, from, to);
        let mut pulse_sum = 0.0;
        for q in 0..4 {
            let qa = from + (to - from) * q as f64 / 4.0;
            let qb = from + (to - from) * (q + 1) as f64 / 4.0;
            let m = log_bands(span_mean(points, qa, qb));
            for c in 0..3 {
                quarters[k][q * 3 + c] = m[c];
            }
            // the low band's peak at the head of this quarter over its median (v2's kick)
            let a = (qa as i64).clamp(0, points.len() as i64 - 1) as usize;
            let b = (qb as i64).clamp(a as i64 + 1, points.len() as i64) as usize;
            let seg: Vec<f64> = points[a..b].iter().map(|p| p[0]).collect();
            let head_size = (seg.len() / 4).max(1);
            let head = seg[..head_size].iter().copied().fold(f64::MIN, f64::max);
            let top = seg.iter().copied().fold(f64::MIN, f64::max);
            pulse_sum += (head - median(&seg)) / (top + 1e-9);
        }
        pulse[k] = pulse_sum / 4.0;
        for c in 0..3 {
            peak[c] = peak[c].max(b3[k][c]);
        }
    }
    for b in &mut b3 {
        for c in 0..3 {
            b[c] = 230.0 * b[c] / peak[c];
        }
    }
    Some(BarData { bar_beat, b3, quarters, pulse })
}

/// The bars' self-similarity (bands + rhythm), z-scored, cosine
fn self_similarity(b3: &[Bands], quarters: &[[f64; 12]]) -> Vec<Vec<f64>> {
    const DIMS: usize = 15;
    let nb = b3.len();
    let mut f = vec![[0.0; DIMS]; nb];
    for k in 0..nb {
        for c in 0..3 {
            f[k][c] = 3.0 * b3[k][c].ln_1p();
        }
        f[k][3..].copy_from_slice(&quarters[k]);
    }
    for d in 0..DIMS {
        let mean = f.iter().map(|r| r[d]).sum::<f64>() / nb as f64;
        let var = f.iter().map(|r| (r[d] - mean) * (r[d] - mean)).sum::<f64>() / nb as f64;
        let sd = var.sqrt() + 1e-6;
        for r in &mut f {
            r[d] = (r[d] - mean) / sd;
        }
    }
    for r in &mut f {
        let norm = r.iter().map(|v| v * v).sum::<f64>().sqrt() + 1e-9;
        for v in r.iter_mut() {
            *v /= norm;
        }
    }
    (0..nb).map(|i| (0..nb).map(|j| (0..DIMS).map(|d| f[i][d] * f[j][d]).sum()).collect()).collect()
}

/// CLASSIC 8-BAR (v2): novelty, the kick going on and off, band changes, weighted to the 8-bar grid
pub fn section_beats_v2(points: &[Bands], beats: &[f64], bpb: usize) -> Vec<usize> {
    let Some(BarData { bar_beat, b3, quarters, pulse }) = bar_data(points, beats, bpb) else { return Vec::new() };
    let nb = b3.len();
    let kick_raw: Vec<f64> = (0..nb).map(|k| pulse[k] * b3[k][0]).collect();
    let p90 = percentile(&kick_raw, 90.0) + 1e-9;
    let mut on = vec![false; nb];
    let mut state = kick_raw[0] / p90 > 0.5;
    for k in 0..nb {
        let v = (kick_raw[k] / p90).clamp(0.0, 1.5);
        if state && v < 0.45 {
            state = false;
        } else if !state && v > 0.7 {
            state = true;
        }
        on[k] = state;
    }
    let mut i = 0;
    while i < nb {
        // a 1-bar state is a fill
        let mut j = i;
        while j < nb && on[j] == on[i] {
            j += 1;
        }
        if j - i < 2 && i > 0 {
            let previous = on[i - 1];
            for v in &mut on[i..j] {
                *v = previous;
            }
        }
        i = j;
    }
    let mut kick_change = vec![0.0; nb];
    let mut band_change = vec![0.0_f64; nb];
    let mut change = vec![0.0; nb];
    for k in 1..nb {
        kick_change[k] = if on[k] != on[k - 1] { 1.0 } else { 0.0 };
        for c in 0..3 {
            change[k] += (b3[k][c].ln_1p() - b3[k - 1][c].ln_1p()).abs();
        }
    }
    for k in 4..nb.saturating_sub(4) {
        for c in 0..3 {
            let before: f64 = (0..4).map(|i| b3[k - 4 + i][c] / 4.0).sum();
            let after: f64 = (0..4).map(|i| b3[k + i][c] / 4.0).sum();
            band_change[k] = band_change[k].max(((after + FLOOR) / (before + FLOOR)).ln().abs());
        }
    }
    // the phrase "1": the 8-bar offset where the bands change most
    let mut phase = 0;
    let mut best_vote = -1.0;
    for o in 0..8 {
        let picked: Vec<f64> = (o..nb).step_by(8).map(|k| change[k]).collect();
        let vote = if picked.is_empty() { 0.0 } else { picked.iter().sum::<f64>() / picked.len() as f64 };
        if vote > best_vote {
            best_vote = vote;
            phase = o;
        }
    }
    let ssm = self_similarity(&b3, &quarters);
    let nov4 = checker_novelty(&ssm, 4);
    let nov8 = checker_novelty(&ssm, 8);
    let rel = |k: usize| ((k as i64 - phase as i64) % 8 + 8) % 8;
    let nov: Vec<f64> = (0..nb).map(|k| 0.5 * nov4[k] + 0.5 * nov8[k]).collect();
    let bc: Vec<f64> = band_change.iter().map(|v| (v - 0.3).max(0.0)).collect();
    let score: Vec<f64> = (0..nb)
        .map(|k| {
            let grid = match rel(k) {
                0 => 1.0,
                4 => 0.75,
                _ => 0.35,
            };
            (nov[k] + 0.6 * kick_change[k] + 0.8 * bc[k]) * grid
        })
        .collect();
    let med = median(&score);
    let deviation: Vec<f64> = score.iter().map(|s| (s - med).abs()).collect();
    let threshold = med + 1.5 * median(&deviation) + 0.15;
    let mut order: Vec<usize> = (0..nb).collect();
    order.sort_by(|&a, &b| score[b].partial_cmp(&score[a]).unwrap_or(std::cmp::Ordering::Equal));
    let mut peaks: Vec<usize> = Vec::new();
    for k in order {
        if score[k] < threshold || k < 4 || k + 4 > nb {
            continue;
        }
        if peaks.iter().all(|&p| k.abs_diff(p) >= 8) {
            peaks.push(k);
        }
    }
    for k in 4..nb {
        if kick_change[k] > 0.0 && (rel(k) == 0 || rel(k) == 4) && peaks.iter().all(|&p| k.abs_diff(p) >= 4) {
            peaks.push(k);
        }
    }
    peaks.sort_unstable();
    peaks
        .into_iter()
        .filter(|&k| {
            let kick = kick_change[k.saturating_sub(1)] > 0.0
                || kick_change[k] > 0.0
                || (k + 1 < nb && kick_change[k + 1] > 0.0);
            kick || nov[k] >= 0.5 || bc[k] >= 0.35
        })
        .map(|k| bar_beat[k])
        .collect()
}

// The learned model (the app's testing/sections/learn/learn.py, 12.10.2026)
const V3_W: [f64; 20] = [
    -0.209382, 0.453735, 0.252804, -0.19666, 0.210246, 0.123065, -0.125752, 0.169679, -0.0496278, 0.0465346,
    -0.119272, -0.0208984, -0.0993343, 0.228287, 0.211971, -0.0247236, -0.0761221, -0.04336, -0.336709, 0.20421,
];
const V3_B: f64 = -0.17862991077174878;
const V3_MU: [f64; 20] = [
    0.280492, 0.208267, 0.162295, 0.173146, 0.191839, 0.275827, 0.267643, 0.168424, 0.250137, 0.240638, 0.170458,
    0.219792, 0.229267, 0.349417, 0.252799, 0.128049, 0.0658737, 0.0143942, 0.0143942, 4.58622,
];
const V3_SD: [f64; 20] = [
    0.258823, 0.205962, 0.18109, 0.195467, 0.280045, 0.298463, 0.354939, 0.281898, 0.292713, 0.332933, 0.27281,
    0.264326, 0.316374, 0.358401, 0.434617, 0.334144, 0.248061, 0.119109, 0.119109, 0.716047,
];
const V3_THRESHOLD: f64 = 0.5;
const V3_GAP: usize = 3;
const MAJOR_CHANGE_BY_LEVEL: [f64; 5] = [0.8, 0.65, 0.5, 0.4, 0.3];
const V3_THRESHOLD_BY_LEVEL: [f64; 5] = [0.75, 0.62, V3_THRESHOLD, 0.46, 0.43];
const PHRASE_MIN_CHANGE: f64 = 0.05;
const MAJOR_BARS: usize = 8;
const MAJOR_WEIGHT: [f64; 3] = [1.5, 1.0, 1.0];

fn energy_change(b3: &[Bands], starts: &[usize], i: usize) -> f64 {
    let nb = b3.len();
    let lo = if i > 0 { starts[i - 1] } else { 0 };
    let hi = starts.get(i + 1).copied().unwrap_or(nb);
    let k = starts[i];
    let from = lo.max(k.saturating_sub(MAJOR_BARS));
    let to = hi.min(k + MAJOR_BARS);
    let mut best = 0.0_f64;
    for c in 0..3 {
        let before: f64 = (from..k).map(|j| b3[j][c] / (k - from) as f64).sum();
        let after: f64 = (k..to).map(|j| b3[j][c] / (to - k) as f64).sum();
        best = best.max(MAJOR_WEIGHT[c] * ((after + FLOOR) / (before + FLOOR)).ln().abs());
    }
    best
}

/// The weakest change goes, again and again, until every start left changes a band by `min_change`
fn major_only(b3: &[Bands], mut starts: Vec<usize>, min_change: f64) -> Vec<usize> {
    let nb = b3.len();
    starts.retain(|&k| k > 0 && k < nb);
    while !starts.is_empty() {
        let (weakest, score) = (0..starts.len())
            .map(|i| (i, energy_change(b3, &starts, i)))
            .fold((0, f64::MAX), |a, b| if b.1 < a.1 { b } else { a });
        if score >= min_change {
            break;
        }
        starts.remove(weakest);
    }
    starts
}

/// ENERGY CHANGES / PHRASES / ENERGY ONLY (v3): a learned model on novelty and band changes; `level` 1..5
pub fn section_beats_v3(points: &[Bands], beats: &[f64], bpb: usize, algorithm: Algorithm, level: usize) -> Vec<usize> {
    let Some(BarData { bar_beat, b3, quarters, .. }) = bar_data(points, beats, bpb) else { return Vec::new() };
    let nb = b3.len();
    let ssm = self_similarity(&b3, &quarters);
    let nov = [checker_novelty(&ssm, 1), checker_novelty(&ssm, 2), checker_novelty(&ssm, 4), checker_novelty(&ssm, 8)];
    let change = |w: usize, k: usize, c: usize| {
        if k < w || k > nb - w {
            return 0.0;
        }
        let before: f64 = (0..w).map(|i| b3[k - w + i][c] / w as f64).sum();
        let after: f64 = (0..w).map(|i| b3[k + i][c] / w as f64).sum();
        ((after + FLOOR) / (before + FLOOR)).ln().abs()
    };
    let prob: Vec<f64> = (0..nb)
        .map(|k| {
            let mut x = [0.0; 20];
            for (i, n) in nov.iter().enumerate() {
                x[i] = n[k];
            }
            let mut c4max = 0.0_f64;
            for c in 0..3 {
                x[4 + c] = change(1, k, c);
                x[7 + c] = change(2, k, c);
                x[10 + c] = change(4, k, c);
                c4max = c4max.max(x[10 + c]);
            }
            x[13] = c4max;
            x[14] = if k % 4 == 0 { 1.0 } else { 0.0 };
            x[15] = if k % 8 == 0 { 1.0 } else { 0.0 };
            x[16] = if k % 16 == 0 { 1.0 } else { 0.0 };
            x[17] = if k < 2 { 1.0 } else { 0.0 };
            x[18] = if k + 3 > nb { 1.0 } else { 0.0 };
            x[19] = (b3[k][0].ln_1p() + b3[k][1].ln_1p() + b3[k][2].ln_1p()) / 3.0;
            let z = V3_B + (0..20).map(|i| V3_W[i] * (x[i] - V3_MU[i]) / V3_SD[i]).sum::<f64>();
            1.0 / (1.0 + (-z).exp())
        })
        .collect();
    let mut order: Vec<usize> = (0..nb).collect();
    order.sort_by(|&a, &b| prob[b].partial_cmp(&prob[a]).unwrap_or(std::cmp::Ordering::Equal));
    let level = level.clamp(1, 5) - 1;
    let threshold = if algorithm == Algorithm::Phrases { V3_THRESHOLD_BY_LEVEL[level] } else { V3_THRESHOLD };
    let mut peaks: Vec<usize> = Vec::new();
    for k in order {
        if prob[k] < threshold {
            break;
        }
        if peaks.iter().all(|&p| k.abs_diff(p) >= V3_GAP) {
            peaks.push(k);
        }
    }
    peaks.sort_unstable();
    if algorithm == Algorithm::EnergyOnly {
        peaks = (4..nb).step_by(4).collect();
    }
    if algorithm != Algorithm::Phrases {
        peaks = major_only(&b3, peaks, MAJOR_CHANGE_BY_LEVEL[level]);
    } else {
        peaks.retain(|&k| k > 0 && k < nb);
        let all = peaks.clone();
        peaks = (0..all.len()).filter(|&i| energy_change(&b3, &all, i) >= PHRASE_MIN_CHANGE).map(|i| all[i]).collect();
    }
    peaks.into_iter().map(|k| bar_beat[k]).collect()
}

/// The found beat indices named, as the app's detectSections: bars measured on the waveform (dB), then the names
/// of the page. Returns (seconds, name, bars).
pub fn name_found(points: &[Bands], beats_pts: &[f64], beat_secs: &[f64], found: &[usize], bpb: usize) -> Vec<(f64, &'static str, usize)> {
    let Some(&first) = found.first() else { return Vec::new() };
    let phase = first % bpb;
    let db = |v: f64| 20.0 * (v + 1.0).log10();
    let low_at = |point: f64| {
        let centre = point.round() as i64;
        (centre - 2..=centre + 2)
            .filter(|&k| k >= 0 && (k as usize) < points.len())
            .map(|k| points[k as usize][0])
            .fold(0.0_f64, f64::max)
    };
    let mut bars = Vec::new();
    let mut bar_beat = Vec::new();
    let mut b = phase;
    while b + bpb < beats_pts.len() {
        let from = beats_pts[b].max(0.0) as usize;
        let to = (beats_pts[b + bpb] as usize).min(points.len());
        let (mut sum, mut high) = (0.0, 0.0);
        for p in points.iter().take(to).skip(from) {
            sum += (p[0] + p[1] + p[2]) / 3.0;
            high += p[2];
        }
        let count = to.saturating_sub(from).max(1) as f64;
        let kick: f64 = (0..bpb).map(|k| low_at(beats_pts[b + k])).sum::<f64>() / bpb as f64;
        bars.push(Bar { energy: db(sum / count), kick: db(kick), high: db(high / count) });
        bar_beat.push(b);
        b += bpb;
    }
    let starts: Vec<usize> = found.iter().filter(|&&i| i >= phase).map(|&i| (i - phase) / bpb).collect();
    let named = name_sections(&bars, &starts);
    named
        .iter()
        .enumerate()
        .filter(|(_, (bar, _))| *bar < bar_beat.len())
        .map(|(i, &(bar, name))| {
            let to = named.get(i + 1).map_or(bars.len(), |n| n.0);
            let secs = if bar == 0 { 0.0 } else { beat_secs[bar_beat[bar]] };
            (secs, name, to - bar)
        })
        .collect()
}
