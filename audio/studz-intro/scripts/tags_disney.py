"""TAGS_disney - 16.0 s magical studio intro made only from metal sounds, on the
measured shape of a modern animation-studio intro (one long crescendo from
silence, the bass arriving late, a whole-step key change at the big moment, hits
about once a second, a quiet minor-iv dip, a second, bigger lift and a slow
ring-out). The melody is the TAGS tune; everything is original.

Metal only:
- tuned from VSCO-2 CE recordings: bowed cymbal (glassy chord pads), a ringing
  metal bar (the melody), gongs (tuned bass, booming hits, a slowed roar under the
  loud parts), slowed brake drum and anvil (clangs), bowed-cymbal risers
- played as instruments: tubular bells and glockenspiel (VSCO-2), celesta
  (GeneralUser GS), cymbal swells, crash, bell tree
Every recording is re-pitched to the chord by changing its playback speed.

0.0-5.0   from silence, one long crescendo in B-flat; the gong bass only from 2.5 s,
          the roar only in the last 1.5 s
5.0       KEY CHANGE UP TO C: tuned gong hit, bells take the melody
5.0-8.0   hits at 5.0 5.9 6.8 7.7 (C - Am - F - G)
8.0-9.4   the dip: soft glass pads, F -> Fm
9.4-10.0  riser: a bowed cymbal screams upward, glockenspiel run, cymbal swell
10.0      MEGA UP: key change up to D, hits at 10.0 10.75 11.5 12.0 12.25
12.5      final D major chord; from 13.0 it slowly fades to silence by 16.0."""
import sys, os, json
import numpy as np, soundfile as sf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orch import Part, PERC, SR, VSCO, build, export, save_score, accent_time, decode, ogg_peak_db, n

LEN = 16.0
LIFT, DIP, RISE, MEGA, FINAL = 5.0, 8.0, 9.4, 10.0, 12.5
HITS1 = [5.0, 5.9, 6.8, 7.7]
HITS2 = [10.0, 10.75, 11.5, 12.0, 12.25]
FADE = [(FINAL, 0), (13.0, -1), (14.3, -9), (15.9, -50)]
HUSH = [(0, 0), (7.95, 0), (8.25, -16), (9.9, -16), (10.0, 0)] + FADE     # ringing tails cleared out of the dip
SHAPE = [(0.3, -32), (1.5, -25), (2.5, -19), (3.5, -13), (4.5, -6), (4.95, -3), (5.0, 0), (5.4, -2), (7.95, -2), (8.15, -15), (9.3, -15),
         (9.95, -4), (10.0, 2), (12.5, 2)] + [(t, d + 2) for t, d in FADE[1:]]


def env(*extra):
    return sorted(SHAPE + list(extra))


PROG = [(0.3, 1.8, 'Bb', ['Bb2', 'F3', 'D4', 'F4', 'C5']), (1.8, 3.0, 'Eb', ['Bb2', 'G3', 'Eb4', 'G4', 'Bb4']),
        (3.0, 3.8, 'G', ['G2', 'D3', 'Bb3', 'F4', 'Bb4']), (3.8, 4.4, 'Eb', ['Eb2', 'Bb2', 'G3', 'Eb4', 'G4']),
        (4.4, 4.75, 'F', ['F2', 'C3', 'A3', 'F4', 'A4']), (4.75, 4.95, 'Ab', ['Ab2', 'Eb3', 'C4', 'Eb4', 'Ab4']),
        (4.95, 5.0, 'Bb', ['Bb2', 'F3', 'D4', 'F4', 'Bb4']),
        (5.0, 5.9, 'C', ['C2', 'G2', 'E3', 'C4', 'G4']), (5.9, 6.8, 'A', ['A1', 'E2', 'C3', 'A3', 'E4']),
        (6.8, 7.7, 'F', ['F1', 'C2', 'A2', 'F3', 'C4']), (7.7, 8.0, 'G', ['G1', 'D2', 'B2', 'G3', 'D4']),
        (8.0, 8.7, 'F', ['F2', 'C3', 'A3', 'C4', 'F4']), (8.7, 9.4, 'F', ['F2', 'C3', 'Ab3', 'C4', 'F4']),
        (9.4, 10.0, 'G', ['G2', 'D3', 'B3', 'D4', 'G4']),
        (10.0, 11.0, 'D', ['D2', 'A2', 'F#3', 'D4', 'A4']), (11.0, 11.75, 'G', ['G1', 'D2', 'B2', 'G3', 'D4']),
        (11.75, 12.5, 'A', ['A1', 'E2', 'C#3', 'A3', 'E4']), (12.5, 15.9, 'D', ['D2', 'A2', 'F#3', 'D4', 'A4'])]


def chord(t):
    for s, e, r, tones in PROG:
        if s <= t < e:
            return r, tones
    return PROG[-1][2], PROG[-1][3]


MEL1 = [(0.9, 'F4', .5), (1.4, 'C5', .6), (2.0, 'D5', .3), (2.3, 'C5', .3), (2.6, 'Bb4', .5),
        (3.1, 'D5', .4), (3.5, 'F5', .5), (4.0, 'G5', .3), (4.3, 'F5', .3), (4.6, 'A5', .3), (4.82, 'Bb5', .2)]
MEL2 = [(5.0, 'C6', .9), (5.9, 'B5', .3), (6.2, 'A5', .3), (6.5, 'E5', .3), (6.8, 'F5', .45), (7.25, 'A5', .45),
        (7.7, 'D6', .3), (7.85, 'B5', .17)]
MEL_DIP = [(8.05, 'A4', .5), (8.55, 'G4', .2), (8.75, 'Ab4', .6), (9.35, 'G4', .1)]
MEL3 = [(10.0, 'D6', .75), (10.75, 'C#6', .3), (11.05, 'B5', .45), (11.5, 'A5', .5), (12.0, 'B5', .25), (12.25, 'C#6', .25),
        (12.5, 'D6', 3.0)]


# ======================= a tiny sampler for the metal recordings
def load(name):
    x, sr = sf.read(os.path.join(VSCO, 'Percussion', name), always_2d=True)
    assert sr == SR
    return np.repeat(x, 2, axis=1) if x.shape[1] == 1 else x[:, :2]


def hz(p):
    return 440.0 * 2 ** ((n(p) - 69) / 12)


class Metal:
    """One stem of re-pitched metal recordings (an orch Part calls it for its audio)."""
    def __init__(self, src, src_hz, start=0.0, att=0.01, rel=0.25):
        self.src, self.src_hz, self.start, self.att, self.rel = src, src_hz, start, att, rel
        self.x = np.zeros((int((LEN + 8) * SR), 2))
        self.__name__ = 'metal'

    def __call__(self):
        return self.x

    def add(self, t, pitch, dur, gain=1.0, pan=0.0, glide=None, reverse=False):
        """Play the recording so its main partial sounds `pitch` (or glide from
        pitch to `glide`), for dur seconds plus the release."""
        L = int((dur + self.rel) * SR)
        r0 = hz(pitch) / self.src_hz
        r1 = hz(glide) / self.src_hz if glide else r0
        rate = r0 * (r1 / r0) ** (np.arange(L) / L)
        pos = self.start * SR + np.concatenate([[0], np.cumsum(rate)[:-1]])
        pos = pos[pos < len(self.src) - 2]
        i = pos.astype(int); f = (pos - i)[:, None]
        y = self.src[i] * (1 - f) + self.src[i + 1] * f
        e = np.ones(len(y))
        a = max(1, int(self.att * SR)); e[:a] = np.linspace(0, 1, min(a, len(e)))[:len(e[:a])]
        k = int(dur * SR)
        if k < len(e):
            e[k:] *= np.linspace(1, 0, len(e) - k)
        y = y * e[:, None]
        if reverse:                                  # played backwards and swelling into t
            y = y[::-1] * (np.linspace(0, 1, len(y)) ** 3)[:, None]
            t = t - len(y) / SR
        g = np.array([np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)]) * np.sqrt(2) * gain
        i0 = int(round(t * SR)); i1 = min(len(self.x), i0 + len(y))
        self.x[i0:i1] += y[:i1 - i0] * g
        return self


bow4, bow3 = load('susCymb1-bow-4.wav'), load('susCymb1-bow-3.wav')
bar = load('vibraring_v1_rr1.wav')
gong_p, gong_fff, gong_f = load('gongHit_p.wav'), load('gongHit_fff.wav'), load('gongHit_f.wav')
brake, anvil, bd = load('BrakeDrum1_Hammer_v3_Sum.wav'), load('Anvil_Hit1_v3_Sum.wav'), load('BDrumNewhit_v7_rr1_Sum.wav')

# ---- glassy chord pads: bowed cymbal (a near-pure 560 Hz partial) tuned to each chord tone
glass = Metal(bow4, 560.0, start=1.0, att=0.12, rel=0.18)
warm = Metal(bow3, 652.0, start=1.5, att=0.15, rel=0.2)
for s, e, r, tones in PROG:
    for k, p in enumerate(tones[2:]):
        glass.add(s, p, e - s, gain=1.0 if k else 0.8, pan=(-0.4, 0.0, 0.4)[k])
    if s >= 1.8:
        for k, p in enumerate(tones[1:3]):
            warm.add(s, p, e - s, gain=0.9, pan=(-0.25, 0.25)[k])

# ---- the melody: a ringing metal bar (341 Hz) re-pitched note by note
mel = Metal(bar, 341.4, att=0.003, rel=0.5)
for t, p, d in MEL1 + MEL2 + MEL_DIP + MEL3:
    mel.add(t, p, d + 0.1, gain=1.0 if t >= LIFT and not (DIP <= t < MEGA) else 0.8, pan=-0.1)

# ---- tuned gong bass (the soft gong's 144 Hz partial on each chord root), late; a slowed roar under the loud parts
gbass = Metal(gong_p, 143.8, att=0.005, rel=0.6)
roar = Metal(gong_fff, 415.8, start=0.05, att=0.3, rel=0.5)
for s, e, r, tones in PROG:
    if s >= 2.5 or s == 1.8:
        gbass.add(max(s, 2.5), tones[0], e - max(s, 2.5) + 0.2, gain=1.0 if s >= LIFT else 0.7)
for s, e, r, tones in PROG:
    if s >= 3.5 and not (DIP <= s < RISE):
        roar.add(s, n(tones[0]) + (12 if n(tones[0]) < n('C2') else 0), e - s + 0.1, pan=0.05)
roar.add(3.5, 'G2', 0.3).add(3.8, 'Eb2', 0.6)

# ---- hits: a fresh loud-gong strike tuned to the chord root, slowed brake drum + anvil clangs, a slowed kick
boom = Metal(gong_fff, 415.8, att=0.002, rel=1.5)
clang = Metal(brake, 1043.6, att=0.001, rel=1.0)
anv = Metal(anvil, 6990.0, att=0.001, rel=1.0)
kick = Metal(bd, 55.0, att=0.001, rel=1.0)
for t in HITS1 + HITS2 + [FINAL]:
    r, tones = chord(t)
    big = t in (LIFT, MEGA, FINAL)
    boom.add(t, n(tones[0]) + 24 if n(tones[0]) < n('C2') else n(tones[0]) + 12, 2.5 if big else 1.0, gain=1.0 if big else 0.6)
    clang.add(t, n(tones[-1]), 0.6, gain=0.8 if big else 0.5, pan=0.3)
    kick.add(t, 'A1' if big else 'C2', 1.2, gain=1.0 if big else 0.6)
    if big:
        anv.add(t, n(tones[-1]) + 24, 1.0, pan=-0.3)

# ---- risers: bowed cymbal played backwards into the lifts, and screaming upward 9.4-10.0
rise = Metal(bow3, 652.0, start=0.5, att=0.4, rel=0.02)
rise.add(LIFT, 'Bb3', 1.8, reverse=True).add(MEGA, 'G3', 1.0, reverse=True)
rise.add(RISE, 'G4', 0.58, gain=0.9, glide='G5', pan=0.2)

parts_metal = [
    Part('glass_pads', glass, level=-17, pan=0.0, send=0.55, env=env((4.98, -3), (5.0, 1))),
    Part('warm_pads', warm, level=-21, pan=0.0, send=0.5, env=env((1.75, -40), (1.8, -14))),
    Part('metal_bar_melody', mel, level=-15, pan=0.0, send=0.5, env=[(0.8, -18), (2.0, -14), (3.0, -9), (4.0, -5), (4.9, -1), (5.0, 0), (8.0, 0), (8.2, -7), (9.4, -7), (10.0, 0)] + FADE),
    Part('gong_bass', gbass, level=-15, pan=0.0, send=0.3, env=env((8.2, -21), (9.2, -21))),
    Part('gong_roar', roar, level=-19, pan=0.0, send=0.3, env=env((3.45, -60), (3.5, -24))),
    Part('gong_hits', boom, level=-14, pan=0.0, send=0.45, env=HUSH),
    Part('brake_clangs', clang, level=-21, pan=0.0, send=0.5, env=HUSH),
    Part('anvil_clangs', anv, level=-24, pan=0.0, send=0.5, env=[(0, 0)] + FADE),
    Part('slowed_kick', kick, level=-15, pan=0.0, send=0.2, env=HUSH),
    Part('cymbal_risers', rise, level=-20, pan=0.0, send=0.55),
]

# ======================= metal instruments
bells = Part('tubular_bells', 'TubularBells', level=-17, pan=0.2, send=0.55, split=True, env=HUSH)
for t, p, d in MEL2 + MEL3:
    if t < FINAL:
        bells.add(t, n(p) - 12, d + 0.5, 112)
for t in [LIFT, MEGA]:
    r, tones = chord(t)
    bells.add(t, [p for p in tones if n('C4') <= n(p) <= n('G5')], 2.5, 118)
bells.add(FINAL, ['D4', 'A4', 'D5', 'F#5'], 3.4, 124)
glock = Part('glock', 'Glockenspiel', level=-21, pan=0.3, send=0.5, split=True, env=[(0.8, -16), (2.5, -11), (4.0, -5), (4.9, -2), (5.0, 0), (7.95, 0), (8.25, -10), (9.35, -10), (9.4, 0)])
for t, p, d in MEL1:
    glock.add(t, n(p) + 12, 0.6, 70 + int(t * 6))
for t, p, d in MEL2 + MEL3:
    glock.add(t, p, 0.6, 100)
for i, p in enumerate([p for p in range(n('G5'), n('G7') + 1) if p % 12 in (7, 9, 11, 2)]):
    glock.add(RISE + 0.55 * (i / 9) ** 0.8, p, 0.4, 80 + i * 4)
cel = Part('celesta', ('gm', 8), level=-21, pan=-0.3, send=0.55, env=[(0.3, -14), (1.5, -9), (2.6, -4), (3.0, 0), (5.0, -4), (8.0, 2), (9.4, 0), (10.0, -2)] + FADE)
for i, t in enumerate([0.35, 0.6, 0.85, 1.1, 1.35, 1.6, 1.85, 2.1, 2.35, 2.6]):
    cel.add(t, ['F6', 'Bb6', 'D7', 'C7', 'F7', 'D7', 'Bb6', 'Eb7', 'G7', 'Bb7'][i], 0.5, 54 + (i % 3) * 6)
for t in HITS1 + HITS2:
    r, tones = chord(t)
    cel.add(t, [n(tones[-1]) + 24, n(tones[-2]) + 24], 0.8, 92)
for i, p in enumerate(['C7', 'Ab6', 'F6', 'C6']):
    cel.add(8.1 + i * 0.3, p, 0.7, 70)
cym = Part('cymbals', 'perc', level=-19, pan=0.15, send=0.45, split=True, env=HUSH)
cym.add(LIFT, PERC['crash'], 3.0, 124).add(MEGA, PERC['crash'], 3.0, 127).add(FINAL, PERC['crash'], 3.0, 124)
cym.add(0.3, PERC['bow'], 4.0, 96)
swell = Part('cym_swell', 'perc', level=-21, pan=0.1, send=0.5, thresh=0.001)
swell.add(LIFT - 3.81, PERC['swell_m'], 3.85, 120).add(MEGA - 1.53, PERC['swell_s'], 1.55, 124)
tree = Part('bell_tree', 'perc', level=-24, pan=-0.2, send=0.6, split=True, env=[(0, -8), (3.0, -8), (5.0, 0)] + HUSH[1:])
tree.add(0.3, PERC['tree4'], 2.0, 80).add(LIFT, PERC['tree1'], 2.0, 110).add(MEGA, PERC['tree1'], 2.0, 116).add(FINAL, PERC['tree2'], 2.0, 110)

PARTS = parts_metal + [bells, glock, cel, cym, swell, tree]
ACCENTS = [LIFT, DIP, MEGA, FINAL]

if __name__ == '__main__':
    out = sys.argv[1]
    y, rep = build('TAGS_disney', PARTS, LEN, os.path.join(out, 'build'), reverb=(78, 38, 100, 100, 28, 0), wet=0.36,
                   fade=(14.6, 15.95))
    wav, ogg = export(y, out, 'TAGS_disney')
    save_score([p for p in PARTS if not callable(p.inst)], os.path.join(out, 'TAGS_disney.mid'))
    y = decode(ogg)
    rep['length_samples'] = len(y)
    rep['ogg_peak_dbfs'] = round(ogg_peak_db(ogg), 2)
    rep['accents'] = {str(round(t, 2)): round(accent_time(y, t), 4) for t in ACCENTS}
    json.dump(rep, open(os.path.join(out, 'TAGS_disney_report.json'), 'w'), indent=1)
    print(json.dumps(rep['accents']), rep['length_samples'], rep['ogg_peak_dbfs'])
