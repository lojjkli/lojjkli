"""TAGS_intro - 16.0 s 'purple, agentic' synth intro. Fully synthesized here
(numpy/SciPy) and original: lush E-flat Lydian chords, digital 'thinking' blips,
a pulsing arpeggio, a build, a drop at 8 s and a three-note signature chime.

120 bpm (beat 0.5 s), E-flat Lydian.
0-2    a glassy pad fades in from silence, digital blips (an AI thinking)
2-6    the arpeggio starts and opens up; a soft sub pulse and ticks join at 4 s
6-8    build: filter sweeps open, a stutter speeds up, a riser, a short silent gap
8      DROP: sub hit, wide chord, the signature chime (Bb - Eb - Bb - A)
8-12   groove: kick, pumping chords and sub, arpeggio; one chord per second
12     final hit: the chime again over Ebmaj9(#11), then a glitchy echo tail
13-16  slowly fades to silence."""
import sys, os, json
import numpy as np
from scipy import signal as ss
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orch import SR, n, sox_reverb, master, export, decode, ogg_peak_db, accent_time

LEN = 16.0
DROP, FINAL = 8.0, 12.0
B = 0.5                                 # one beat at 120 bpm
N = int((LEN + 6) * SR)
rng = np.random.default_rng(11)

# chords: (start, end, bass, pad tones)
CH = {'Eb': ('Eb2', ['Bb3', 'D4', 'F4', 'G4', 'A4']),     # Ebmaj9(#11) - the purple one
      'Cm': ('C2', ['Bb3', 'D4', 'Eb4', 'F4', 'G4']),      # Cm11
      'Ab': ('Ab1', ['G3', 'C4', 'D4', 'Eb4', 'Bb4']),     # Abmaj9(#11)
      'Bb': ('Bb1', ['C4', 'F4', 'Ab4', 'Bb4', 'D5'])}     # Bb9sus
PROG = [(0.0, 2.0, 'Eb'), (2.0, 4.0, 'Cm'), (4.0, 6.0, 'Ab'), (6.0, 8.0, 'Bb'),
        (8.0, 9.0, 'Eb'), (9.0, 10.0, 'Cm'), (10.0, 11.0, 'Ab'), (11.0, 12.0, 'Bb'), (12.0, LEN, 'Eb')]
CHIME = ['Bb4', 'Eb5', 'Bb5', 'A5']


def hz(p):
    return 440.0 * 2 ** ((n(p) - 69) / 12) if isinstance(p, str) else 440.0 * 2 ** ((p - 69) / 12)


def T(d):
    return np.arange(int(d * SR)) / SR


def saw(f, d, phase=None):
    """Band-limited (polyBLEP) sawtooth."""
    dt = f / SR
    ph = ((phase if phase is not None else rng.random()) + dt * np.arange(int(d * SR))) % 1.0
    y = 2 * ph - 1
    a = ph < dt; x = ph[a] / dt; y[a] -= x + x - x * x - 1
    b = ph > 1 - dt; x = (ph[b] - 1) / dt; y[b] -= x * x + x + x + 1
    return y


def lp(y, fc, order=2):
    return ss.sosfilt(ss.butter(order, min(fc, SR * 0.45), fs=SR, output='sos'), y, axis=0)


def hp(y, fc, order=2):
    return ss.sosfilt(ss.butter(order, fc, 'high', fs=SR, output='sos'), y, axis=0)


def sweep_lp(x, cut):
    """Time-varying lowpass (STFT mask); cut: Hz per output sample."""
    f, tt, Z = ss.stft(x, SR, nperseg=2048, noverlap=1536, axis=0)
    idx = np.clip((tt * SR).astype(int), 0, len(cut) - 1)
    m = 1 / np.sqrt(1 + (np.maximum(f, 1)[:, None] / cut[idx][None, :]) ** 6)
    if Z.ndim == 3:
        m = m[:, None, :]
    _, y = ss.istft(Z * m, SR, nperseg=2048, noverlap=1536, time_axis=-1, freq_axis=0)
    y = np.moveaxis(y, -1, 0) if y.ndim == 2 else y
    return y[:len(x)]


def curve(pts, length=N):
    t = np.arange(length) / SR
    return np.interp(t, [p[0] for p in pts], [p[1] for p in pts])


def db(pts, length=N):
    return 10 ** (curve(pts, length) / 20)


class Stem:
    def __init__(self, name, level, pan=0.0, wet=0.3):
        self.name, self.level, self.pan, self.wet = name, level, pan, wet
        self.x = np.zeros((N, 2))

    def put(self, t, y, pan=0.0, gain=1.0):
        if y.ndim == 1:
            a = (pan + 1) * np.pi / 4
            y = np.stack([y * np.cos(a), y * np.sin(a)], 1) * np.sqrt(2)
        i = int(round(t * SR)); e = min(N, i + len(y))
        if e > i:
            self.x[i:e] += y[:e - i] * gain


def env_ad(d, a=0.005, tau=0.2):
    t = T(d)
    e = np.minimum(1, t / a) * np.exp(-np.maximum(0, t - a) / tau)
    e[-min(len(e), 200):] *= np.linspace(1, 0, min(len(e), 200))
    return e


def fm_bell(f, d, idx=2.5, ratio=3.5, tau=0.9):
    t = T(d)
    mod = idx * np.exp(-t / (tau * 0.4)) * np.sin(2 * np.pi * f * ratio * t)
    return np.sin(2 * np.pi * f * t + mod) * env_ad(d, 0.002, tau)


def pingpong(st, time=0.375, fb=0.45, mix=0.5, lowcut=6000):
    """Stereo ping-pong echo on a stem (dotted-eighth)."""
    d = int(time * SR); x = st.x
    out = x.copy(); tap = x.copy()
    for k in range(1, 7):
        tap = lp(np.roll(tap, d, axis=0)[:, ::-1], lowcut) * fb
        tap[:d] = 0
        out += tap * mix
    st.x = out


stems = []

# ---- pad: detuned saws per chord tone, slowly opening lowpass, + a glass sine an octave up
pad = Stem('pad', -18, wet=0.5); stems.append(pad)
glass = Stem('glass', -24, wet=0.6); stems.append(glass)
for s, e, c in PROG:
    d = e - s + 0.25
    fade = np.minimum(1, T(d) / 0.12) * np.minimum(1, (d - T(d)) / 0.2)
    for k, p in enumerate(CH[c][1]):
        f = hz(p)
        y = np.stack([sum(saw(f * 2 ** (c_ / 1200), d) for c_ in (-14, -5, 7)),
                      sum(saw(f * 2 ** (c_ / 1200), d) for c_ in (-9, 4, 13))], 1) / 3
        pad.put(s, y * fade[:, None])
        glass.put(s, np.sin(2 * np.pi * 2 * f * T(d)) * fade * (0.6 if k % 2 else 1.0), pan=(-0.5, 0.5)[k % 2])
pad.x = sweep_lp(pad.x, curve([(0, 300), (2, 600), (4, 900), (6, 1300), (7.9, 6000), (8.0, 3200), (12.0, 7000), (12.5, 4000), (15.9, 500)]))

# ---- digital 'thinking' blips: short sine pings, Lydian notes, ping-pong echoes
blip = Stem('blips', -24, wet=0.35); stems.append(blip)
POOL = ['Bb5', 'D6', 'F6', 'G6', 'A6', 'C7', 'Eb6', 'A5']
times = sorted(set(np.round(np.concatenate([rng.choice(np.arange(0.4, 6.0, 0.125), 22, replace=False),
                                             rng.choice(np.arange(8.25, 11.9, 0.125), 10, replace=False)]), 3)))
for t in times:
    f = hz(rng.choice(POOL))
    d = rng.choice([0.04, 0.06, 0.09])
    y = np.sin(2 * np.pi * f * T(d)) * env_ad(d, 0.001, d / 3)
    if rng.random() < 0.35:                      # a little two-tone 'chirp'
        y = np.concatenate([y, np.sin(2 * np.pi * f * 1.5 * T(d)) * env_ad(d, 0.001, d / 3)])
    blip.put(t, y, pan=rng.uniform(-0.7, 0.7), gain=rng.uniform(0.5, 1.0))
pingpong(blip)

# ---- arpeggio: 16th-note plucks over the chord tones, opening up into the drop
arp = Stem('arp', -20, wet=0.3); stems.append(arp)
PAT = [0, 2, 4, 1, 3, 4, 2, 1]
ARP_CUT = [(2, 700), (4, 1200), (6, 1800), (7.9, 6500), (8, 3500), (12, 5000)]
for s, e, c in PROG:
    if not (2.0 <= s < FINAL):
        continue
    tones = sorted(n(p) for p in CH[c][1])
    t, i = s, 0
    while t < e - 1e-6:
        p = tones[PAT[i % 8]] + (12 if (i // 8) % 2 else 0)
        f = hz(p); d = 0.22
        y = lp(saw(f, d) * 0.6 + np.sign(np.sin(2 * np.pi * f * T(d))) * 0.25, np.interp(t, [q[0] for q in ARP_CUT], [q[1] for q in ARP_CUT]))
        arp.put(t, y * env_ad(d, 0.002, 0.07) * (1.0 if i % 4 == 0 else 0.7), pan=(-0.35, 0.35)[i % 2])
        t += B / 4; i += 1
pingpong(arp, fb=0.3, mix=0.35, lowcut=4000)

# ---- sub bass: sine on the root (pulsing on 8ths 4-8, held and pumping 8-12)
sub = Stem('sub', -17, wet=0.0); stems.append(sub)
for s, e, c in PROG:
    if s < 4.0:
        continue
    f = hz(CH[c][0])
    if s < DROP:
        for t in np.arange(s, e - 1e-6, B / 2):
            d = 0.22; sub.put(t, np.tanh(1.5 * np.sin(2 * np.pi * f * T(d))) * env_ad(d, 0.004, 0.12) * 0.7)
    else:
        d = e - s + (2.5 if s >= FINAL else 0.02)
        y = np.tanh(1.4 * np.sin(2 * np.pi * f * T(d)))
        y *= np.minimum(1, T(d) / 0.01) * np.minimum(1, (d - T(d)) / 0.05)
        sub.put(s, y)

# ---- drums: kick, ticks / hats, the build stutter, impacts
drums = Stem('drums', -14, wet=0.12); stems.append(drums)
def kick(gain=1.0, d=0.5):
    t = T(d); f = 45 + 110 * np.exp(-t / 0.03)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.18)
    y[:int(0.004 * SR)] += hp(rng.standard_normal(int(0.004 * SR)), 2000) * 0.4
    return np.tanh(1.6 * y) * gain
for t in np.arange(DROP, FINAL - 1e-6, B):
    drums.put(t, kick())
drums.put(FINAL, kick(1.0, 1.2))
hats = Stem('ticks', -26, wet=0.2); stems.append(hats)
def hat(d=0.03):
    return hp(rng.standard_normal(int(d * SR)), 7000, 4) * env_ad(d, 0.001, d / 4)
for t in np.arange(4.0, DROP - 0.1, B / 4):
    hats.put(t, hat(), pan=0.3, gain=0.5 + 0.3 * ((t * 4) % 2 == 0))
for t in np.arange(DROP, FINAL - 1e-6, B):
    hats.put(t + B / 2, hat(0.09), pan=-0.2, gain=1.0)
    hats.put(t + B / 4, hat(), pan=0.3, gain=0.4); hats.put(t + 3 * B / 4, hat(), pan=0.3, gain=0.4)
build = Stem('build', -20, wet=0.3); stems.append(build)
st = [6.0 + k * B / 2 for k in range(8)] + [7.0 + k * B / 4 for k in range(6)] + [7.75 + k * B / 8 for k in range(3)]
for k, t in enumerate(st):                       # digital stutter: band-passed noise, rising
    d = 0.06
    y = ss.sosfilt(ss.butter(2, [800 + k * 120, 4000 + k * 300], 'band', fs=SR, output='sos'), rng.standard_normal(int(d * SR)))
    build.put(t, y * env_ad(d, 0.001, 0.025), gain=0.4 + 0.6 * k / len(st), pan=(-0.3, 0.3)[k % 2])
GAP = DROP - 0.06
riser = Stem('riser', -21, wet=0.4); stems.append(riser)
d = GAP - 5.6; u = T(d) / d
nz = sweep_lp(rng.standard_normal((len(u), 2)), 400 * (40 ** u ** 1.5)) * (10 ** (-30 * (1 - u) ** 1.4 / 20))[:, None]
tone = np.sin(2 * np.pi * np.cumsum(200 * (8 ** u ** 1.3)) / SR) * (10 ** (-24 * (1 - u) / 20))
riser.put(5.6, nz / np.abs(nz).max() + 0.25 * tone[:, None])
riser.x[int(GAP * SR):int(DROP * SR)] = 0
impact = Stem('impact', -13, wet=0.35); stems.append(impact)
for t, g, dd in ((DROP, 1.0, 1.8), (FINAL, 1.0, 3.0)):
    tt = T(dd)
    boom = np.sin(2 * np.pi * np.cumsum(30 + 60 * np.exp(-tt / 0.25)) / SR) * np.exp(-tt / (dd / 3))
    wash = lp(rng.standard_normal(len(tt)), 3000) * np.exp(-tt / 0.35) * 0.25
    impact.put(t, np.tanh(1.5 * boom) + wash, gain=g)
    rv = hp(rng.standard_normal(int(1.0 * SR)), 3000) * np.exp(-T(1.0) / 0.25)
    impact.put(t - 1.0, rv[::-1] * 0.12, pan=0.2)

# ---- stabs in the groove: short wide chords on the off-beats
stab = Stem('stabs', -21, wet=0.35); stems.append(stab)
for s, e, c in PROG:
    if DROP <= s < FINAL:
        for t in (s + B * 0.5, s + B * 1.5):
            d = 0.18
            y = sum(saw(hz(p) * 2 ** (dc / 1200), d) for p in CH[c][1] for dc in (-8, 8))
            stab.put(t, lp(y, 3500) * env_ad(d, 0.003, 0.08), pan=0.0)

# ---- the signature chime (FM bells + glass), at the drop and at the end, plus a glitchy echo tail
chime = Stem('chime', -16, wet=0.45); stems.append(chime)
for t0, g in ((7.0, 0.35), (DROP, 0.9), (FINAL, 1.0)):
    for k, p in enumerate(CHIME):
        d = 2.5 if k == 3 else 0.8
        f = hz(p)
        chime.put(t0 + k * B / 2, fm_bell(f, d, 2.0, 3.5, 1.0 if k == 3 else 0.4) + 0.4 * np.sin(2 * np.pi * 2 * f * T(d)) * env_ad(d, 0.002, 0.5),
                  pan=(-0.25, 0.25, -0.1, 0.1)[k], gain=g)
for k in range(6):                              # beat-repeat glitch of the last chime note
    t = FINAL + 1.5 + k * 0.375 / (1 + k * 0.15)
    chime.put(t, fm_bell(hz('A5'), 0.12, 1.5, 3.5, 0.05), pan=(-0.6, 0.6)[k % 2], gain=0.5 * 0.75 ** k)
pingpong(chime, fb=0.35, mix=0.3)

# ---- sidechain pump on the pad, stabs and sub in the groove, from the kick
pump = np.ones(N)
for t in np.arange(DROP, FINAL - 1e-6, B):
    i = int(t * SR); L = int(0.42 * SR)
    pump[i:i + L] = np.minimum(pump[i:i + L], 1 - 0.65 * np.exp(-np.arange(L) / (0.09 * SR)))
for s_ in (pad, sub, stab, glass):
    s_.x *= pump[:, None]

# ---- overall shape: silence -> fade in -> build -> drop -> final -> fade
SHAPE = {'pad': [(0, -60), (0.3, -30), (2, -14), (4, -9), (6, -6), (7.93, 0), (7.94, -60), (8.0, -3), (12, -3), (12.01, 0), (13, -1), (15.9, -50)],
         'glass': [(0, -60), (0.5, -24), (2, -12), (6, -6), (7.93, -2), (7.94, -60), (8.0, 0), (13, 0), (15.9, -50)],
         'arp': [(2, -14), (4, -8), (6, -4), (7.93, 0), (7.94, -60), (8.0, 0), (12, 0)],
         'sub': [(4, -10), (6, -6), (7.93, -2), (7.94, -60), (8.0, 0), (13, 0), (15.0, -30)],
         'blips': [(0, -14), (2, -8), (6, 0), (8, -2)], 'ticks': [(4, -12), (7.9, 0), (8, 0)],
         'chime': [(0, 0), (13.5, 0), (15.9, -40)]}
for s_ in stems:
    if s_.name in SHAPE:
        s_.x *= db(SHAPE[s_.name])[:, None]

ACCENTS = [DROP, FINAL]

if __name__ == '__main__':
    out = sys.argv[1]
    wd = os.path.join(out, 'build', 'TAGS_intro'); os.makedirs(wd, exist_ok=True)
    L = int(LEN * SR)
    dry = np.zeros((N, 2)); send = np.zeros((N, 2)); levels = {}
    for s_ in stems:
        k = int(0.1 * SR)
        rms = np.sqrt(np.convolve((s_.x ** 2).mean(1), np.ones(k) / k, 'same')).max()
        x = s_.x / max(rms, 1e-9) * 10 ** (s_.level / 20)
        dry += x; send += x * s_.wet; levels[s_.name] = s_.level
    rv = sox_reverb(send, (70, 45, 100, 100, 25, 0), wd)
    M = min(len(rv), N)
    mix = (dry[:M] + rv[:M] * 0.32)[:L]
    y = master(mix, os.path.join(out, 'build'), 'TAGS_intro', (14.8, 15.95), True)
    wav, ogg = export(y, out, 'TAGS_intro')
    y = decode(ogg)
    rep = dict(length_samples=len(y), ogg_peak_dbfs=round(ogg_peak_db(ogg), 2), stem_levels=levels,
               accents={str(t): round(accent_time(y, t), 4) for t in ACCENTS})
    json.dump(rep, open(os.path.join(out, 'TAGS_intro_report.json'), 'w'), indent=1)
    print(json.dumps(rep['accents']), rep['length_samples'], rep['ogg_peak_dbfs'])
