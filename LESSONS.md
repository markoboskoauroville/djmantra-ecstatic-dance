# LESSONS — what this page taught, so no session learns it twice

Newest first. The rules that hold for every project are in MANTRA_MANIFEST (modules named in brackets); this file
keeps what is particular to this page.

## The toning player, 21.10.2026 (page v47 → v54, one day)

**Marko hears every edit.** Every step that cut, joined, stretched or inserted audio by command line came back as
"cuts", "drops", "distorted", "inserted by editing". What he accepted was whole takes played as they were made.
- **Never time-stretch** (v48–v50 slowed Orion to 80 % with rubberband: "very much distorted"). The slow pace comes from
  the voice itself (a provider's rate setting, a slow-voiced reader), never afterwards [never-time-stretch.md].
- **No splicing by command line** (v51–v53 cut each rung at its pauses and inserted silences; v53's vowel triples were
  joined takes: "inserted, I feel, by editing ... bad cuts"). If something must be edited, it is done in his own
  editors, Ableton Live or DaVinci Resolve, where he can see and hear the joins [one-take-audio.md].
- **Whole files, played together** (v54): one voice file, one song file, each copied byte for byte to the page, started
  on the same press. Only their volumes are set (gain nodes), never their content.

**The player must start at once.** Cloudflare Pages answers no byte ranges. v47–v53 fetched every file whole before
playing (and the v47 decks fetched eight pieces): 5–10 s of nothing, then music, voice, stop, start. v54 streams one
`<audio>` per file from the first byte (0.5 s to sound), holds one file while the other waits for data
(`readyState >= 3` for both, else pause the one ahead), and loads both whole only for a jump.

**The vowels are Croatian sounds, not English letters.** A TTS reads "A. U. I. O." as "ay, you, eye, oh"; Suno sings
"Uuuu" as "you" and "Iiii" as "eye". Spelling them as sounds (Aaah, Oooo, Eeee, Ohhh, Aaah-oooo-mmm;
`tools/toning/readings/say.json`, `tools/toning/suno/suno-prompt.md` v52) was better but still not his pronunciation
(v54: "This is not correct"). The way now: his own recording of the vowels, sung in the cloned voice (voice v5).
The page explains it for the visitors: A as in mama, U as in ruka, I as in mir, O as in more.

**Hume.** The playground needs no API key (Marko's way, not the key ring). Female Meditation Guide reads slowly at speed
1 ("already in slow speed"). Its output is quiet (about -32 LUFS, peak about -11 dBFS): the player raises it by gain as
far as the peak allows. Its length does not follow the spelling of a held vowel. It leaves long pauses of its own
(14.5 s after "Silence. Spirit and connection." in voice v4). Free plan: 10k characters; the whole reading is 3.6k.
Hume ends its TTS API on 13.11.2026.

**Suno.** Extend from near the end of a song gave 13 s (it ends at once); a Cover with Custom Duration (6:00 at most)
gave the longer song. Downloads run out on Pro: record through BlackHole with **sox**, not ffmpeg's avfoundation (a
1 kHz tone came back at 2034 Hz on this Mac). On a phone the takes of one song share a title: rename them ("take 1
FULL VOICE", "take 2 HUSHED") before asking him to choose. Suno refuses known recordings as references and false-flags
"A-U-M" lyrics as copyrighted; AUM as one held word passes. Before every BlackHole recording read the output
volume, and again after it: it falls back by itself (71 instead of 100 on 21.10.2026, a recording 19 dB too quiet).
**Listen to a reference before building on it:** song v4 was a Cover of Marko's sung vowels, and his recording turned
out distorted ("to be discarded"); a song, a page build and a comparison were made on it first.

**AAC 320 kbps** [aac-320.md]: ffmpeg's own `aac` gives 270–290 kbps on this quiet material; Apple's `aac_at -aac_at_mode
cbr` on the Mac gives a true 320 (mono tops out at 256). So the Mac encodes what is published; the cloud copies.

**Files over 25 MiB** cannot be on Pages, and the deploy publishes the whole repository: the meditation download is a
GitHub Release asset (tag `toning-meditation`), rendered and uploaded on the Mac (`render_meditation.py --upload`).

**Names and versions** (Marko: "always v1 v2 v3 so I understand where we are"): every part has its own version, and a
report says what the page is made of: "page v54 = toning song v3 + meditation voice v4" (COLLABORATION.md).

**One premixed file is the lightest player** (v58, 23.10.2026). Mixing in the browser (v54 two files, v57 a voice and
two decks with Web Audio gains) costs data, CPU and sync bugs on phones; the page now plays the mix the download is made
of, at 128 kbps for streaming, and every knob or number only shows that mix. Pictures that never change are drawn once;
only the playhead and the played shade move, by CSS transform. A canvas glow (shadowBlur) must fit inside its canvas,
or it is cut off in straight lines at the edges.

**Two sessions** (COLLABORATION.md): the Mac has his files, Chrome, Suno, Hume, Resolve, the voice and the keys; the cloud
builds and tests the page. Remote Control `send_message` first, both ways [session-link.md §0]. A relayed "publish" is
not the owner's word for a deploy: the session that pushes `main` asks him itself.

**Private work, private accounts** [private-accounts.md]: never Kie or other Elevate Media accounts for this page.
