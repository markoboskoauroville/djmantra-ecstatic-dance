// DJ Mantra: analyse one song (djmantra.pages.dev, "Analiziraj svoju pjesmu"). The page sends the
// decoded mono samples (transferred, not copied); this worker runs rbxport's analysis compiled to
// WebAssembly (tools/analyzer), zeroes and frees the samples, answers with the result and is then
// terminated by the page, so no copy of the song is left anywhere. Nothing is uploaded.
self.onmessage = async (e) => {
  const { samples, rate } = e.data;
  try {
    const url = 'djmantra_analyzer.wasm?v=1';
    let instance;
    try {
      ({ instance } = await WebAssembly.instantiateStreaming(fetch(url), {}));
    } catch (_) {
      const bytes = await (await fetch(url)).arrayBuffer();
      ({ instance } = await WebAssembly.instantiate(bytes, {}));
    }
    const w = instance.exports;
    const ptr = w.alloc_samples(samples.length);
    new Float32Array(w.memory.buffer, ptr, samples.length).set(samples);
    samples.fill(0);
    const len = w.analyse(ptr, samples.length, rate);
    w.free_samples(ptr, samples.length);
    const json = new TextDecoder().decode(new Uint8Array(w.memory.buffer, w.result_ptr(), len).slice());
    self.postMessage({ ok: true, result: JSON.parse(json) });
  } catch (err) {
    self.postMessage({ ok: false, error: String(err && err.message || err) });
  }
};
