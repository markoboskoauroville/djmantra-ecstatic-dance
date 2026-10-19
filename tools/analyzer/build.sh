#!/bin/sh
# Builds the analyzer to WebAssembly and copies it next to the page's worker.
# Needs: rustup target add wasm32-unknown-unknown
set -e
cd "$(dirname "$0")"
cargo build --release --lib --target wasm32-unknown-unknown
cp target/wasm32-unknown-unknown/release/djmantra_analyzer.wasm ../../assets/analyzer/
ls -l ../../assets/analyzer/djmantra_analyzer.wasm
