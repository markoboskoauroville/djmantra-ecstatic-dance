//! Native check: `ffmpeg -i song.mp3 -ac 1 -ar 44100 -f f32le - | cargo run --release --example analyse_file`
use std::io::Read;
fn main() {
    let mut bytes = Vec::new();
    std::io::stdin().read_to_end(&mut bytes).expect("stdin");
    let samples: Vec<f32> = bytes.chunks_exact(4).map(|c| f32::from_le_bytes([c[0], c[1], c[2], c[3]])).collect();
    println!("{}", djmantra_analyzer::analyse_json(&samples, 44100));
}
