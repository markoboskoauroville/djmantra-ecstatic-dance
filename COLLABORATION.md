# COLLABORATION — the Mac session and the cloud session build this page together

Marko, 21.10.2026: "develop the communication to develop this website", "two way communication, local and cloud
session". Two Claude sessions work on djmantra.pages.dev at the same time, each doing what only it can do, and talking
to each other directly. Marko gives the requests to either one; he is the tester and says "merge".

## Who is who

| | **MAC** (local) | **CLOUD** |
|---|---|---|
| Session | "Collaboration", `session_01KMkv7vfVfo6NY7aiqB7KS3`, address `claude-code-59 [ec97ca]` (renamed `collaboration`) | "DJ MANTRA WEB PAGE (CLOUD)", `session_01NZpGhkKVWj5htPreYnNcEp`, address `[953a66]` |
| Has | Marko's files (~/Downloads, ~/Music, EXT_1TB), the keys in ~/Downloads/API (Gemini, Hume, Speechify, Cloudflare), Chrome with his logins (Suno, Gmail), the voice MANTRA_VOICE on :8837, the hub's HANDOVER and PROJECTS.md | the repository, ffmpeg with rubberband, numpy, headless Chromium for testing, the Kie API |
| Does | fetches and sends: audio and images from his disk, new TTS readings, Suno, emails; reads results to Marko by voice; updates the hub at the end | builds: code, audio processing (cutting, slowing, levelling, waveforms), tests in the browser, commits, writes momentaryupdates and README |
| Never | starts MANTRA CHAT or the voice by itself | asks for a key; merges to main without Marko's "merge" |

## How we talk, both ways

**Remote Control first, always** (Marko, 21.10.2026: *"When I say connect to local session or to cloud session, it
always going to remote control. Don't try any other options first."*; MANTRA_MANIFEST modules/session-link.md §0).
Every session is shared through Remote Control, so each one is reachable by its `session_01…` id.

1. **Cloud → Mac:** the claude-code-remote tool `send_message` to `session_01KMkv7vfVfo6NY7aiqB7KS3` (Marko allowed it
   on 21.10.2026, on his trusted device). It arrives on the Mac as a new turn.
2. **Mac → Cloud:** the claude-code-remote tool `send_message` to `session_01NZpGhkKVWj5htPreYnNcEp` if the Mac has
   it; the Mac's CLI has not (21.10.2026), so `SendMessage` to the cloud session's name in ListAgents (it showed as
   `[cdc740]`). It wakes the cloud session as a new turn. Tested both ways on 21.10.2026.
3. **When a message cannot go:** the sender commits a note to `COLLAB/inbox-mac.md` or `COLLAB/inbox-cloud.md` on the
   working branch and pushes; the other side reads it on its next turn (`git pull`) and clears what it has done.
   Each side can also read the other's transcript (`list_events` on its session ID).
4. A new session (either side) reads this file first, then the inbox addressed to it.

## The message

```
TOPIC: one line, what it is about                   ← Marko sees only this line in the preview
JOB: <number> <name>            (from the job list below, or NEW)
<what was done or what is asked: files with their repo paths, commit hashes, durations, what to check>
STATUS: DONE | DOING | BLOCKED <why> | QUESTION FOR MARKO <the question>
```

- Files travel through git on the working branch, never as message text. Big audio as AAC (m4a 256 kbps) or MP3;
  WAV masters stay on the Mac (.gitignore). Cloudflare Pages refuses files over 25 MiB.
- Never a key, token or password in a message, a commit or the transcript.
- Marko's words are quoted exactly as he said them, and the request goes into momentaryupdates.md with its number.
- One question at a time to Marko; the Mac session asks him by voice (he reads by ear).

## After every update of the page

When the cloud pushes a change Marko should see, it tells the Mac, and **the Mac refreshes the page in Marko's
browser** (Marko, 21.10.2026: *"Ask the local session to refresh the browser when it updates the page."*): the tab
with djmantra.pages.dev (or opens it), a hard reload so no cached copy stays (the version label top left must show
the new number), scrolled to the part that changed. A change on `main` is live about a minute after the push, when the
Deploy run of `.github/workflows/deploy.yml` is green; the Mac waits for that before reloading.

## Audio

AAC is 320 kbps by default (MANTRA_MANIFEST modules/aac-320.md): encoded from the master, on the Mac with Apple's
encoder (`-c:a aac_at -b:a 320k -aac_at_mode cbr`), measured with ffprobe.

## Git

- Working branch: `claude/amazing-wozniak-1851tn` (until Marko says merge; then a new one, written here).
- Before every commit `git pull --ff-only`; never force-push, never rewrite the other side's commits.
- Only `main` deploys (.github/workflows/deploy.yml), so the branch is safe to try things on. `main` only after
  Marko's "merge".
- Each side commits only its own part of a job: the Mac its source files, the cloud the built page.

## Names and versions

Marko, 21.10.2026: *"Please name it according to our project and always v1 v2 v3 so I understand where we are."*
Every deliverable is named by its part of the project and a whole-number version; a report says what the page is made
of, e.g. **"page v52 = toning song v1 + meditation voice v3"**.

| Part | v1 | v2 | v3 |
|---|---|---|---|
| **Toning song** (the music under the voice) | Marko's "Toning A U I O DJ MANTRA WEB PAGE", `tools/toning/suno/toning-auio-djmantra.m4a` | the Suno cover with the Croatian vowel spellings (job 12), `toning-auio-djmantra-v2.m4a`: not made yet | |
| **Meditation voice** (Hume, Female Meditation Guide) | the English letters (0479572), replaced | the Croatian vowel sounds (0a0fafe) | each vowel three times (9aa1b6a) |
| **Meditation download** (voice + song in one file) | page v52's mix (job 11) | | |

Before Hume the voice was Orion (Gemini), page v48–v51; it is not counted in these versions.

## The job list

| # | Job | Who | Status |
|---|---|---|---|
| 1 | Marko's song "Toning A U I O DJ MANTRA WEB PAGE" from ~/Downloads as `tools/toning/suno/toning-auio-djmantra.m4a` | MAC | done, baadd18, AAC 320 kbps CBR, 264.68 s |
| 2 | Build it as the only background under Orion (`python3 tools/toning/build_bg.py`), test, push | CLOUD | done, v49 on the branch; live when it is merged into main |
| 3 | Orion's intro and O rungs, cut short by Gemini in v47: generate `00-intro.mp3` and `04-o.mp3` again with Gemini TTS, voice Alnilam, plain text from `tools/toning/readings/orion/readings.json` (no "read slowly" instruction, Gemini refuses it), the plain readings into `tools/toning/readings/orion/`, push; check each one is whole (the last words heard) | MAC | done, 21.10.2026: gemini-2.5-flash-preview-tts, Alnilam, finish STOP; intro 16.1 s, O 29.7 s; Whisper heard every word; no pause over 1.5 s |
| 4 | Slow the new rungs (`python3 tools/toning/slow_toning.py`), test, push | CLOUD | done, v50 (0c4868a): intro 42 s, O 69 s, the reading 11:45 |
| 5 | Marko listens on djmantra.pages.dev (slow Orion, the breathing knob, his song; the cuts per element by ear) | MARKO, asked by the MAC by voice | open |
| 6 | After merge: HANDOVER, SESSIONS, PROJECTS.md in the hub | MAC | waits on 5 |
| 8 | Hume's Female Meditation Guide reads the 8 rungs in the playground, speed 1 | MAC | done, 0479572; built as the page's voice in v52 (10:36), but read from the letters: U came out "you", O "oh" |
| 9 | Read the 8 rungs again in the same voice and settings from the **"say"** texts of `tools/toning/readings/say.json` (the vowels spelled as their Croatian sound: Aaah, Ooooh, Eeee, Oh, Aah-ooh-mmm), same folder and names, replacing 0479572's files; Whisper check that the vowels sound as written; push | MAC | open (about 3.5k of the 6.6k free Hume characters) |
| 10 | Slow nothing: pauses only (`slow_toning.py`), test, push | CLOUD | done, 11:09; Hume's 8 s pause in 05-ov capped to 3.5 s like every pause |
| 11 | The download: on the Mac, `python3 tools/toning/render_meditation.py --upload` (Apple's aac_at, a true 320 kbps; gh uploads it to the Release `toning-meditation`); before main goes live, or the DOWNLOAD button points at nothing | MAC | waits on 10 |
| 12 | Marko's YES (21.10.2026): the Suno song again with the vowels spelled as sounds, his song as the reference (Cover): `tools/toning/suno/suno-prompt.md`, *v52*; in Marko's Chrome; two takes, he chooses; the WAV stays on the Mac, `toning-auio-djmantra-v2.m4a` (aac_at 320 CBR) pushed | MAC | open |
| 13 | Cut the new song per element (`build_bg.py`), render the download again, test, push | CLOUD | waits on 12 |

Each side updates its own rows when it sends a message.
