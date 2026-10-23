# Suno: toning song v6, Marko's template as a Cover (request 105, 23.10.2026)

Marko: *"Tibetan choir singing it with a lot of reverb like in a church atmosphere ... a cappella, no other
instruments. Very strong voices, male choir only. And timing should be followed because it's aligned exactly with the
voice."* Then: *"you don't adjust timings. You need to give Suno a prompt to have silence between vowels and sounds.
There should be silence so I can edit manually inside my application."*

**Reference:** takes/toning-v6-template.wav (from ~/Desktop/Audio 2_001_2ICB6Z.wav, 4:25.6, mono 48 kHz 24-bit, peak
-8 dBFS, clean). Upload → **Cover**, Audio Influence **90 %** (the timing is the template's), Weirdness **5 %**, the
length stays the template's. Two takes, renamed "v6 take 1", "v6 take 2". Nothing is edited afterwards: the recording
through BlackHole is the whole take, Marko places it in his own editor.

The map of the template (librosa, silence under -38 dB; chapters of meditation voice v5):

| Voice v5 | Template, sung phrases | Pitch |
|---|---|---|
| intro 0:00 | silence to 0:20 | |
| A, earth 0:17 | 2 × A, ~10 s (0:20, 0:35) | ~78 Hz, low |
| U, water 0:42 | 3 × U, 8–13 s (0:46, 1:02, 1:16) | ~93 Hz |
| I, fire 1:22 | 5 × I, ~4.5 s (1:26–1:54) | ~138 Hz, higher |
| O, air 1:51 | 6 × O, ~4.5 s (1:55–2:23) | ~91 Hz |
| A-U-I-O, throat 2:21 | the glide a-o-ee-oh twice in ~2 s sounds (2:27–2:51), then 5 long ones, ~7 s (2:51–3:31) | ~91 Hz |
| silence | 3:31–3:45 | |
| AUM, third eye 3:37 | 3 × AUM, ~8 s (3:45, 3:54, 4:03) | ~88 Hz |
| silence, crown 4:08 | silence 4:12 → 4:25 | |

## Style (count: ≤ 1000)
```
A cappella sacred vowel toning. A powerful Tibetan monastic male choir only, many very strong deep male voices in unison, chest voice, throat-sung overtones ringing above the drone. Croatian pure vowels, no diphthongs: A as open ah, U as round oo, I as bright ee, O as open oh, AUM as ah-oo-mm. Every sung sound is followed by full silence: the choir breathes, stops completely, then sings the next sound. Follow the timing of the reference exactly: sing only where the reference sings, stay silent where it is silent. No instruments at all: no pads, no drone synth, no bowls, no gong, no drums, no piano. Free time, no beat. Long church cathedral reverb, stone hall, the reverb tail dying into silence between sounds. Natural, unquantized, intimate yet huge.
```

## Lyrics
```
[Intro]
[silence, no voices, no instruments]

[Earth]
[a cappella male choir, very low and strong, one long held open ah, then silence]
Aaaaaaaah
[silence]
Aaaaaaaah
[silence]

[Water]
[the choir round and deep, one long held oo as in moon, silence between]
Oooooooo
[silence]
Oooooooo
[silence]
Oooooooo
[silence]

[Fire]
[the choir higher and bright, short strong ee as in see, silence between]
Eeeee
[silence]
Eeeee
[silence]
Eeeee
[silence]
Eeeee
[silence]
Eeeee
[silence]

[Air]
[the choir open and wide, short oh as in more, silence between]
Ohhh
[silence]
Ohhh
[silence]
Ohhh
[silence]
Ohhh
[silence]
Ohhh
[silence]
Ohhh
[silence]

[Throat]
[the choir glides ah, oo, ee, oh, each sound short, silence between, then long glides with overtones]
Aah [silence] Ooo [silence] Eee [silence] Ohh [silence]
Aah [silence] Ooo [silence] Eee [silence] Ohh [silence]
Aaah oooo eeee ohhh
[silence]
Aaah oooo eeee ohhh
[silence]
Aaah oooo eeee ohhh
[silence]
Aaah oooo eeee ohhh
[silence]
Aaah oooo eeee ohhh
[long silence]

[Third Eye]
[the deepest choir, ah gliding to oo and closing into a long hum, silence between]
Aaah oooo mmmm
[silence]
Aaah oooo mmmm
[silence]
Aaah oooo mmmm

[Outro]
[only the cathedral reverb tail dying away, then complete silence]
```

## Exclude Styles
```
instruments, synth pads, drone synth, singing bowls, gong, drums, percussion, piano, strings, guitar, bass, beat, female voice, solo singer, English words, pop vocals, vibrato, autotune, spoken word, rap, electronic, EDM, build-up, crescendo, tempo change, key change, continuous drone under the silences
```

**After:** each take recorded through BlackHole with sox (the whole take, nothing cut), 24-bit WAV kept on the Mac
(takes/toning-v6-take1.wav, take2), AAC 320 CBR with aac_at as toning-auio-djmantra-v6-take1.m4a / take2. The audio
output put back to the device it was on before (audio-back-home.md).

## What was made (23.10.2026, morning)

- Upload: the template as a 256k MP3 (the WAV is 38 MB; Chrome uploads at most 10 MB), "toning-v6-template" in Suno.
  Remix → Cover from its menu, styles kept, the lyrics above typed over Suno's own guess.
- Settings: v6 model, Vocal Gender Male, Weirdness 4 %, Style Influence 50 %, Audio Influence 91 %.
- Pair 1, Duration Auto: 3:33 and 3:13, shorter than the template, so they cannot sit under the voice. Kept, not used.
- Pair 2, Duration Custom 4:25 (265 s, the template is 265.6 s): **take 1** and **take 2**, recorded whole through
  BlackHole with sox, nothing cut (Marko places them in his editor).

## Discarded, and v7 (23.10.2026)

Marko: take 1 "too enthusiastic and too loud", take 2 "has music"; "it needs to follow my audio 100% ... no music ...
accompaniment by different male voices to make it everything sound larger and bigger and big echo."
v7 = the same Cover, Audio Influence 100 %, Weirdness 0 %, Style Influence 70 %, Duration 4:25, Male.

Style v7:
```
A cappella, human voices only, no music. Follow the reference voice exactly: the same notes, the same timing, the same quiet calm dynamics, the same silences between sounds. A soft meditative male choir joins the reference voice in unison and in the low octave, many calm male voices singing quietly together to make it sound larger and wider, never louder, never excited. Pure held vowels ah, oo, ee, oh, aum. Very big echo and a long cathedral reverb, a huge stone church. No instruments at all: no pads, no drone, no synth, no bowls, no gong, no drums, no piano, no strings, no bass. Free time, no beat, no build-up.
```
Exclude v7: `music, instrumental, instruments, synth pads, drone, singing bowls, gong, drums, percussion, piano, strings, guitar, bass, beat, energetic, powerful, loud, epic, dramatic, crescendo, belting, female voice, English words, pop vocals, vibrato, autotune, electronic, build-up, tempo change`
Lyrics v7: as above, every stage note "calm male voices, soft".
