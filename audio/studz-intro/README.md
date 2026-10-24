# Studz intro music

Orchestral cues for the Roblox game **Studz**, played with real recorded
instrument samples. Each part is written as MIDI, rendered through the sample
libraries, then mixed and mastered. TAGS_theme is pure sound design instead: real
metal recordings from the same library, slowed down and layered. TAGS_disney uses
those same metal recordings, but tuned so they play the chords and the melody.

| File | Length | Main accent (target → measured in the .ogg) |
|---|---|---|
| `TAGS_ident.ogg` | 10.100 s (445 410 samples) | 5.300 → 5.302 s |
| `Studz_fanfare.ogg` | 14.800 s (652 680 samples) | 10.000 → 10.004 s |
| `TAGS_theme.ogg` | 10.000 s (441 000 samples) | big hit 2.600 → 2.604 s, clangs 4.000 → 3.990 s and 4.400 → 4.448 s, deep hit 8.000 → 8.002 s |
| `TAGS_disney.ogg` | 16.000 s (705 600 samples) | lift 5.000 → 5.004 s, MEGA UP 10.000 → 10.002 s, final chord 12.500 → 12.500 s |

All are Ogg Vorbis, 44.1 kHz stereo, `oggenc -q 7`, peaking at about -1 dBFS and ending in
digital silence. 24-bit WAVs of the same masters are in `wav/`.

## TAGS_ident (studio logo, magical castle-intro style, D-flat major)

Inspired by the feel of a modern animation-studio castle intro: string-led, lyrical and
sparkling. The melody is original, not a quotation.

| Time | What happens |
|---|---|
| 0–2.3 s | Night sky over the water. Celesta and harp twinkle over a soft string pad (D♭maj9 → G♭maj7♯11). A solo flute sings the first phrase. |
| 2.3 s | The star appears (bell tree). |
| 2.3–5.2 s | The shooting star draws its arc: the violins carry the melody higher over E♭m9 → G♭maj7 → Amaj7 (the "magic" lift) → A♭9sus4 → A♭7. An accelerating harp glissando rises with the star and horns sing a warm counter-line. The build stays held back, then a quick inhale while the flute run, timpani roll and cymbal swell sweep up into the drop. |
| 5.3 s | The drop: the castle lights up. Full orchestra fortissimo on D♭ major, about 10 dB above the build: the violins peak on high D♭, trumpets sing the melody in thirds, with horns, trombones, tuba, timpani, bass drum, crash, tubular bells, glockenspiel and bell tree. It stays big through the fireworks. |
| 5.55, 6.10, 6.55, 7.20, 7.75 s | Fireworks: glockenspiel, celesta, harp, triangle and piccolo sparkles, with timpani and full brass on each one. The whole orchestra sings the cadence D♭ → B♭m7 → G♭maj7 → G♭m6 (the wistful minor iv) → D♭. A timpani roll leads into the grand final chord at 7.75 (crash, bass drum). |
| after 7.75 s | It rings out with a last celesta and harp arpeggio and fades to silence by 10.1 s. |

Fireworks measured at 5.560, 6.104, 6.554, 7.204 and 7.754 s.

## TAGS_theme (10 s dark metal intro, no music)

This is the dark, heavy feel of the Paramount logo sequence from a modern robot-action
film, made only from real metal recordings. There's no melody and no beat. The
reference audio is not included; only measurements of it were used:

- its loudness every 0.25 s
- its brightness (spectral centroid)
- how much of its energy sits below 250 Hz
- where its hits and groans fall

Those measurements were made with `scripts/analyze_ref.py` and `scripts/compare.py`.

Every sound comes from the VSCO-2 CE percussion recordings: gong hits and scrape, bowed
cymbal, bass-drum rubs, brake drum, anvil, ratchet and kick. Each is slowed down 2–8×
with a sliding playback speed, so a gong becomes a giant metal roar and a bowed cymbal
becomes a groan or a screech.

| Time | What happens |
|---|---|
| 0–1.2 s | Silence |
| 1.2–1.6 s | A fast swell into a deep metal roar (two gongs slowed 3–4×, a bass-drum rub slowed 2×). Its pitch drifts. |
| 1.4–2.0 s | A metal screech sliding down |
| **2.6 s** | **The biggest hit:** a fresh gong strike, brake drum, anvil and kick, all slowed down. A bowed-cymbal screech rises from 2.4 to 3.5 s. |
| 3.7–4.7 s | Two metal groans (about 240 and 285 Hz) with slowed clangs at 4.0 and 4.4 s |
| 4.7–5.5 s | Dip, with a gong scrape |
| 5.4–6.6 s | A swell with faint mechanical clicks (ratchet) and a bass-drum rub groaning upward. A slowed bowed-cymbal texture runs underneath until the end. |
| 7.0–7.5 s | Dip |
| 7.5–8.0 s | A reversed gong rises into **8.0 s**, a deep hit, with a gong groan falling in pitch. |
| 8.2–10 s | A dark tail into silence |

How close it is to the reference, by `scripts/compare.py` from 1 to 9 s, after matching levels:

| Measure | Reference | TAGS_theme |
|---|---|---|
| Loudness-curve correlation | | 0.93 |
| Average gap every 0.25 s | | about 3 dB |
| Brightness (power-weighted spectral centroid) | 239 Hz | 284 Hz |
| Energy below 250 Hz | 73% | 77% |

`reports/TAGS_theme_vs_reference_shape.png` shows both spectrograms and loudness curves.
This piece has no MIDI because it is not written as notes.

## TAGS_disney (16 s magical intro made from metal, B♭ → C → D)

This intro has the shape of a modern animation-studio intro, measured with
`scripts/analyze_ref.py`. The reference audio is not included. Its shape:

- one long crescendo from silence
- the bass arriving late
- a whole-step key change at the big moment
- hits about once a second
- a quiet minor-iv dip, then a second, bigger lift and a slow ring-out

The difference is that every sound is metal. The melody is the TAGS tune.

The metal recordings come from the VSCO-2 CE percussion set. Each one is tuned to the
chords by changing its playback speed, so its main pitch lands on the right note:

| Recording | Main pitch | Becomes |
|---|---|---|
| Bowed cymbal | 560 Hz, nearly a pure tone | the glassy chord pads |
| A second bowed-cymbal take | 652 Hz | the warmer pads, and the risers (played backwards into the lifts, and screaming upward at 9.4 s) |
| Ringing metal bar | 341 Hz | the melody, re-pitched note by note |
| Soft gong | 144 Hz | the bass on each chord root, from 2.5 s |
| Loud gong | 416 Hz | slowed into a roar under the loud parts, and struck on each hit, tuned to the chord |
| Brake drum and anvil, slowed | | the clangs on the hits |
| Kick, slowed | | weight under the hits |

Played as instruments on top: tubular bells and glockenspiel (VSCO-2), celesta (GeneralUser GS), cymbal
swells, crash and bell tree.

| Time | What happens |
|---|---|
| 0–5.0 s | From silence, one long crescendo in B♭ (B♭ – E♭/B♭ – Gm7 – E♭ – F – A♭ – B♭). Glass pads, celesta, and the melody on the metal bar and glockenspiel. The gong bass enters at 2.5 s, the roar only in the last 1.5 s, with a cymbal swell into the lift. |
| 5.0 s | Key change up to C: a tuned gong hit, and the tubular bells take the melody. |
| 5.0–8.0 s | Hits at 5.0, 5.9, 6.8 and 7.7 s (C – Am – F – G). |
| 8.0–9.4 s | The dip, about 10 dB quieter: soft glass pads, F → Fm. |
| 9.4–10.0 s | Riser: the bowed cymbal screams upward, with a glockenspiel run and a cymbal swell. |
| 10.0 s | MEGA UP: key change up to D. Hits at 10.0, 10.75, 11.5, 12.0 and 12.25 s (D – G – A). |
| 12.5 s | Final D major chord. |
| 13–16 s | It slowly fades to silence. |

Measured: lift 5.004 s, MEGA UP 10.002 s, final chord 12.500 s.
Loudness every 0.5 s: -55, -44, -39, -39, -34, -32, -31, -28, -24, -21 dB, then -17 at the lift, -26 to -28 in the dip and -16 at MEGA UP.

`midi/TAGS_disney.mid` holds the instrument parts. The tuned metal recordings are placed by `scripts/tags_disney.py` itself.

## Studz_fanfare (game logo, B-flat major)

| Time | What happens |
|---|---|
| 0–4 s | Dusk over the lake: rippling harp, soft strings, bowed cymbal shimmer. Two runs of skipping bricks (celesta + harp, each skip quieter and closer together) end in splashes at 2.22 s and 3.86 s (bell tree, soft cymbal, harp drip, timpani "plop"). |
| 4–9.5 s | Rising through the clouds: horn theme, then strings, winds, trombones and tuba join. Trumpets answer at 7.25 s. Timpani, and a long cymbal swell into the landing. |
| 8.8–10 s | Letters fly in one by one at 8.80, 9.04, 9.28, 9.52 and 9.76 s: rising trumpet thirds, timpani steps and glockenspiel. A flourish (violin spiccato run, flute run, harp glissando) runs underneath. |
| 10.0 s | Logo lands: B-flat tutti with tubular bells, crash, gong, bass drum and timpani. |
| 10–14.8 s | Held chord decays to silence. |

Measured: splashes at 2.224 and 3.916 s; letters at 8.804, 9.044, 9.282, 9.524 and 9.758 s. The second splash is soft (mallet cymbal, bell tree, harp drip), so its attack builds gradually and measures later than its scheduled 3.86 s.

Accent times are measured on the decoded .ogg: the 2 ms frame where the energy above 1.5 kHz
rises most steeply. See `reports/*.json` and `reports/*.png`.

Every track is shifted by its own measured attack delay, so the accents land on the requested
times. Slow-speaking strings and brass get up to 300 ms. For staccato and pizzicato stabs,
each chord is timed on its own (the `split` option in `scripts/orch.py`).

## Instruments and samples

- **VSCO-2 Community Edition** (Versilian Studios, CC0), SFZ branch, commit `6dd651d`:
  - strings: violin, viola, cello and contrabass ensembles (sustain/vibrato, tremolo, spiccato), harp
  - winds: flute, piccolo, oboe, clarinet, bassoon
  - brass: F horn, trumpet, tenor trombone, tuba (sustain; trumpet and trombone staccato)
  - percussion: timpani hits and rolls, tubular bells, glockenspiel, bass drum, snare, ratchet, anvil, brake drum, crash and suspended cymbals (mallet, crescendo rolls, bowed), gong hits and scrape, bass-drum rubs, bell tree, triangles. The one-shot percussion has no SFZ upstream; a small one is embedded in `scripts/orch.py`.
- **GeneralUser GS 2.0.3** (S. Christian Collins, free for any use), commit `684543d`: celesta and choir "aahs" only (VSCO-2 has neither).

## Tools

- sfizz `sfizz_render` (built from commit `f5c6e29`) for the SFZ instruments; FluidSynth 2.3.4 for the celesta and choir.
- Python 3 with mido, numpy, SciPy, soundfile and matplotlib: score, sound design, mixing, alignment and checks; librosa for `analyze_ref.py` and `compare.py`.
- SoX 14.4.2 hall reverb (wet send), and FFmpeg 6.1 for the master: high-pass, gentle EQ, 2:1 compression.
- vorbis-tools 1.4.2 (`oggenc -q 7`).

## Files

- `TAGS_ident.ogg`, `Studz_fanfare.ogg`, `TAGS_theme.ogg`, `TAGS_disney.ogg`: the deliverables.
- `wav/`: 24-bit masters.
- `midi/*.mid`: full score of TAGS_ident, Studz_fanfare and TAGS_disney (one track per part). `midi/parts/<piece>/`: the exact per-part MIDI that was rendered.
- `scripts/`:
  - `orch.py`: render, align, mix and master toolkit
  - `tags_ident.py`, `studz_fanfare.py`, `tags_theme.py`, `tags_disney.py`: the compositions
  - `plot_check.py`: the waveform, spectrogram and loudness plots
  - `analyze_ref.py`: measures a reference intro (loudness curve, frequency bands, hits, tempo, chords)
  - `compare.py`: compares a render with a reference every 0.25 s (loudness, brightness, low-end share)
- `reports/`: stem shifts, levels, measured accents and the plots.

## Rebuild

```sh
git clone -b SFZ https://github.com/sgossner/VSCO-2-CE vsco      # ~2 GB of samples are used
git clone https://github.com/mrbumpy409/GeneralUser-GS gugs
git clone --recursive https://github.com/sfztools/sfizz && cmake -S sfizz -B sfizz/build -DSFIZZ_JACK=OFF -DSFIZZ_RENDER=ON && cmake --build sfizz/build
sudo apt install fluidsynth sox ffmpeg vorbis-tools && pip install mido numpy scipy soundfile matplotlib librosa
export VSCO_DIR=$PWD/vsco GUGS_SF2=$PWD/gugs/GeneralUser-GS.sf2 SFIZZ=$PWD/sfizz/build/library/bin/sfizz_render
python3 scripts/tags_ident.py out && python3 scripts/studz_fanfare.py out && python3 scripts/tags_theme.py out && python3 scripts/tags_disney.py out
```
