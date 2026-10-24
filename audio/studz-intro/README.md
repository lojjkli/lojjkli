# Studz intro music

Two short orchestral cues for the Roblox game **Studz**, played with real recorded
instrument samples (no synthesis). Each part is written as MIDI, rendered through
the sample libraries, then mixed and mastered.

| File | Length | Main accent (target → measured in the .ogg) |
|---|---|---|
| `TAGS_ident.ogg` | 10.100 s (445 410 samples) | 5.300 → 5.302 s |
| `Studz_fanfare.ogg` | 14.800 s (652 680 samples) | 10.000 → 10.004 s |

Both are Ogg Vorbis, 44.1 kHz stereo, `oggenc -q 7`, peaking at about -1 dBFS and ending in
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
  - strings: violin, viola, cello and contrabass ensembles (sustain/vibrato, tremolo), violin spiccato, harp
  - winds: flute, piccolo, oboe, clarinet, bassoon
  - brass: F horn, trumpet, tenor trombone, tuba
  - percussion: timpani hits and rolls, tubular bells, glockenspiel, bass drum, crash and suspended cymbals (mallet, crescendo rolls, bowed), gong, bell tree, triangles. The one-shot percussion has no SFZ upstream; a small one is embedded in `scripts/orch.py`.
- **GeneralUser GS 2.0.3** (S. Christian Collins, free for any use), commit `684543d`: celesta only, because VSCO-2 has no celesta.

## Tools

- sfizz `sfizz_render` (built from commit `f5c6e29`) for the SFZ instruments; FluidSynth 2.3.4 for the celesta.
- Python 3 with mido, numpy, soundfile and matplotlib: score, mixing, alignment and checks.
- SoX 14.4.2 hall reverb (wet send), and FFmpeg 6.1 for the master: high-pass, gentle EQ, 2:1 compression.
- vorbis-tools 1.4.2 (`oggenc -q 7`).

## Files

- `TAGS_ident.ogg`, `Studz_fanfare.ogg`: the deliverables.
- `wav/`: 24-bit masters.
- `midi/*.mid`: full score of each piece (one track per part). `midi/parts/<piece>/`: the exact per-part MIDI that was rendered.
- `scripts/`:
  - `orch.py`: render, align, mix and master toolkit
  - `tags_ident.py`, `studz_fanfare.py`: the compositions
  - `plot_check.py`: the waveform, spectrogram and loudness plots
- `reports/`: stem shifts, levels, measured accents and the plots.

## Rebuild

```sh
git clone -b SFZ https://github.com/sgossner/VSCO-2-CE vsco      # ~2 GB of samples are used
git clone https://github.com/mrbumpy409/GeneralUser-GS gugs
git clone --recursive https://github.com/sfztools/sfizz && cmake -S sfizz -B sfizz/build -DSFIZZ_JACK=OFF -DSFIZZ_RENDER=ON && cmake --build sfizz/build
sudo apt install fluidsynth sox ffmpeg vorbis-tools && pip install mido numpy soundfile matplotlib
export VSCO_DIR=$PWD/vsco GUGS_SF2=$PWD/gugs/GeneralUser-GS.sf2 SFIZZ=$PWD/sfizz/build/library/bin/sfizz_render
python3 scripts/tags_ident.py out && python3 scripts/studz_fanfare.py out
```
