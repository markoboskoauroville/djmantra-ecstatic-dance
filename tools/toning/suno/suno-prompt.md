# Suno: the toning choir (requests 75–77, 21.10.2026)

Audio reference: toning-guide-mix.mp3 (5:55; marks in toning-guide-mix.json: intro 0:00, A 0:30, U 1:15, I 2:00,
O 2:45, A-U-I-O 3:30, AUM 4:30, silence 5:15). Rules: MANTRA_MANIFEST modules/suno-song.md.

## Style
```
Sacred ambient meditation, vowel toning. A deep male monastic choir in the Tibetan chant tradition, very low and slow, many voices on one long held note, throat-sung overtones ringing above, breath audible between phrases. Croatian pure vowels, no diphthongs: A as open ah, U as round oo, I as bright ee, O as open oh, AUM as a-u-m. Under the choir: warm analog pads, a soft sub drone, distant singing bowls, a slow gong swell, a few felt piano notes far away. C major, free time, no beat, around 60 BPM. One vowel per section, each with its element: earth low and heavy; water flowing and soft; fire brighter, a quiet frame drum pulse; air open and wide, the heart; throat all four vowels gliding in one breath with clear overtones; AUM the deepest and widest; the end pads and bowls only, fading into silence. Long cathedral reverb, intimate, unquantized, analog warmth.
```

## Lyrics
```
[Intro]
[warm pads and a soft drone, no voices, 30 seconds]

[Earth]
[deep male choir, very low and heavy, one long held vowel A, the Croatian open ah]
Aaaaaaaaaa
Aaaaaaaaaa

[Water]
[the choir softer and flowing, one long held vowel U, the Croatian round oo]
Uuuuuuuuuu
Uuuuuuuuuu

[Fire]
[the choir brighter, projecting outward, a quiet frame drum pulse, vowel I, the Croatian bright ee]
Iiiiiiiiii
Iiiiiiiiii

[Air]
[the choir open and wide, the heart, vowel O, the Croatian open oh]
Oooooooooo
Oooooooooo

[Throat]
[the choir glides slowly A to U to I to O in one unbroken breath, overtones ringing above]
Aaaa uuuu iiii oooo
Aaaa uuuu iiii oooo

[Third Eye]
[the deepest choir, the sacred syllable AUM held long, a-u-m]
Aaaa uuuu mmmm
Aaaa uuuu mmmm

[Outro]
[the voices stop, pads and singing bowls only, fading into silence]
```

## Exclude Styles
```
English words, lyrics with words, pop vocals, female lead, solo singer, rap, spoken word, autotune, pop vibrato, drum kit, electronic beat, four on the floor, bass drop, EDM, trap, guitar solo, electric guitar, tempo change, key change, build-up, crescendo, fast tempo, call and response
```

---

# v52: the same song again, the vowels spelled as their sound (Marko, 21.10.2026)

Marko: *"English pronunciation is not okay. It should be like Croatian one ... the right sound for the right letter,
not the spelling sound"*, then *"Yes, redo Suno song with the same spelling ... using reference track already
created."* Suno sang "Uuuu" as "you" and "Iiii" as "eye"; the lyrics now spell the sound (as tools/toning/readings/say.json
does for the voice): A = Aaah, U = Oooo (as in moon), I = Eeee (as in see), O = Ohhh (as in more), AUM = Aaah oooo mmmm.

**Reference:** Marko's own song "Toning A U I O DJ MANTRA WEB PAGE" (the WAV in ~/Downloads on the Mac; the page's
background since v49): Suno **Cover** (or Upload → Cover) of it with the lyrics below, Audio Influence about 60 %
(v47's cura prox covers used 59 %), the Style and Exclude Styles above unchanged plus the line below. Its length
stays near the reference (4:25). Two takes; Marko chooses by ear.

## Style (add to the end of the v47 style)
```
Sing only these open sounds, never letter names: ah, oo as in moon, ee as in see, oh as in more, mm hummed.
```

## Lyrics
```
[Intro]
[warm pads and a soft drone, no voices]

[Earth]
[deep male choir, very low and heavy, one long held open ah]
Aaaaaaaah
Aaaaaaaah

[Water]
[the choir softer and flowing, one long held round oo, as in moon]
Oooooooo
Oooooooo

[Fire]
[the choir brighter, projecting outward, a quiet frame drum pulse, one long held bright ee, as in see]
Eeeeeeee
Eeeeeeee

[Air]
[the choir open and wide, the heart, one long held open oh, as in more]
Ohhhhhhh
Ohhhhhhh

[Throat]
[the choir glides slowly from ah to oo to ee to oh in one unbroken breath, overtones ringing above]
Aaaah oooo eeee ohhh
Aaaah oooo eeee ohhh

[Third Eye]
[the deepest choir, ah gliding to oo and closing into a long hum]
Aaaah oooo mmmmmm
Aaaah oooo mmmmmm

[Outro]
[the voices stop, pads and singing bowls only, fading into silence]
```

**After:** download the chosen take in the best quality Suno gives (WAV), keep the WAV on the Mac, encode with
`ffmpeg -i take.wav -c:a aac_at -b:a 320k -aac_at_mode cbr -movflags +faststart toning-auio-djmantra-v2.m4a`, push it
as tools/toning/suno/toning-auio-djmantra-v2.m4a. The cloud then cuts it per element (build_bg.py) and renders the
download again.
