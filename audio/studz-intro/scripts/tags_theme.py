"""TAGS_theme - 16.0 s studio intro in the dark blockbuster style, shaped after
measurements of a modern Paramount logo sequence from a robot-action film:
1 s of silence, then a low sub/brass growl that dives in pitch, a falling
'downer' sweep, metal clanks, a fast mechanical ticking pulse (~0.19 s) and a
low drone - sound design more than melody, dark (centroid 500-900 Hz), sub
always present. All music and sound design is original.

160 bpm (8th = 0.1875 s, the same rate as the measured mechanical pulse), D minor.

0.0-1.0   silence
1.0-5.0   the build: low growl + sub, rumble, string tremolo crescendo, a downer at
          2.5 s, metal clanks, mechanical ticks speeding up, noise riser and a
          reverse swell sucked into a 70 ms gap
5.0       BRAAM: low brass + synth braam + sub impact + downer + crash
5.0-8.0   the beat: spiccato string ostinato (3-3-2), bass drum / metal backbeat,
          brass stabs, choir; Dm - Bb - C - A
8.0-9.4   beat down: everything drops into one falling hit, only a low drone,
          slow ticks and a metal ring are left (Bb, then Gm)
9.4-10.0  riser: ticks accelerate, timpani roll, strings climb, reverse swell, gap
10.0      MEGA UP: biggest braam + gong, the heroic theme on trumpets/violins,
          the beat comes back doubled; Dm - Bb - C - A, drum fill into
12.5      the final D major braam; from 13.0 it slowly sinks to silence by 16.0."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orch import Part, PERC, build, export, save_score, accent_time, decode, ogg_peak_db, n
import fx
import numpy as np

LEN = 16.0
OPEN, HIT, DOWN, RISE, MEGA, FINAL = 1.0, 5.0, 8.0, 9.4, 10.0, 12.5
GAP = 0.07                             # silent 'inhale' before the two big hits
E = 60 / 160 / 2                       # eighth note
Q = 2 * E
FADE = [(FINAL, 0), (13.0, -1), (14.3, -9), (15.9, -50)]
ACC = (0, 3, 6)                        # 3-3-2 accents inside a bar of 8 eighths
HOT = [(0, -3), (DOWN - 0.03, -3), (DOWN, -60), (MEGA - 0.01, -60), (MEGA, 2)] + FADE   # on for the two loud sections
BIGGER = [(0, -3), (MEGA - 0.01, -3), (MEGA, 0)]        # the first beat holds back so MEGA can jump

# (start, end, root, chord tones low -> high)
PROG = [(HIT, 6.5, 'D', ['D2', 'A2', 'D3', 'F3', 'A3', 'D4']), (6.5, 7.25, 'Bb', ['Bb1', 'F2', 'Bb2', 'D3', 'F3', 'Bb3']),
        (7.25, 7.625, 'C', ['C2', 'G2', 'C3', 'E3', 'G3', 'C4']), (7.625, DOWN, 'A', ['A1', 'E2', 'A2', 'C#3', 'E3', 'A3']),
        (MEGA, 10.75, 'D', ['D2', 'A2', 'D3', 'F3', 'A3', 'D4']), (10.75, 11.5, 'Bb', ['Bb1', 'F2', 'Bb2', 'D3', 'F3', 'Bb3']),
        (11.5, 12.0, 'C', ['C2', 'G2', 'C3', 'E3', 'G3', 'C4']), (12.0, FINAL, 'A', ['A1', 'E2', 'A2', 'C#3', 'E3', 'A3']),
        (FINAL, 15.9, 'D', ['D2', 'A2', 'D3', 'F#3', 'A3', 'D4'])]


def chord_at(t):
    for s, e, r, tones in PROG:
        if s <= t < e:
            return r, tones
    return None


def in_oct(root, lo, hi):
    """MIDI number of pitch class `root` inside [lo, hi]."""
    pc = n(root + '4') % 12
    return next(p for p in range(n(lo), n(hi) + 1) if p % 12 == pc)


def grid(t0, t1, step):
    out, t = [], t0
    while t < t1 - 1e-6:
        out.append(round(t, 5)); t += step
    return out


def pumped(env, depth, tau=0.18):
    """Duck a sustained part after every chord attack in the loud sections
    (full on the hit, `depth` dB down soon after), so the hits punch out
    instead of sitting on a flat plateau."""
    ts = np.arange(0, LEN + 0.005, 0.01)
    db = np.interp(ts, [p[0] for p in env], [p[1] for p in env])
    starts = [s for s, *_ in PROG if s < FINAL]
    for s, e in zip(starts, starts[1:] + [FINAL]):
        k = (ts >= s) & (ts < e)
        db[k] += depth * (1 - np.exp(-(ts[k] - s) / tau))
    return list(zip(ts, db))


A_BEAT = grid(HIT, DOWN, E)            # 16 eighths
B_BEAT = grid(MEGA, 12.0, E)           # the first bar and a bit, then the fill
FILL = grid(12.0, FINAL, E / 2)        # 16ths into the final hit
BACK = [5.375, 6.125, 6.875, 7.625, 10.375, 11.125, 11.875]       # backbeat
ACCENTED = [t for beats in (A_BEAT, B_BEAT) for i, t in enumerate(beats) if i % 8 in ACC]

# ======================= synthesized sound design
sub = fx.Buf(LEN)                      # sub impacts
fx.impact(sub, OPEN, f0=55, f1=30, dur=2.5, tau=0.9, gain=0.18)
fx.impact(sub, HIT, gain=0.8)
fx.impact(sub, DOWN, f0=70, f1=24, dur=2.0, tau=0.6, gain=0.6)
fx.impact(sub, MEGA, f0=70, f1=24, dur=2.6, tau=0.8, gain=1.0)
fx.impact(sub, FINAL, f0=66, f1=26, dur=3.4, tau=1.3, gain=1.0)
for t in ACCENTED:
    if t not in (HIT, MEGA):
        fx.impact(sub, t, f0=80, f1=40, dur=0.5, tau=0.12, gain=0.3)
grit = fx.Buf(LEN)                     # synth braam layers
fx.braam(grit, OPEN, [36.71, 55.0], dur=3.6, tau=1.6, bright=900, dive=3, gain=0.2)
fx.braam(grit, HIT, [36.71, 73.42, 110.0], dur=1.5, tau=0.8, bright=2600, dive=1, gain=0.8)
fx.braam(grit, MEGA, [36.71, 55.0, 73.42, 110.0, 146.8], dur=2.2, tau=1.2, bright=3400, dive=2, gain=1.0)
fx.braam(grit, FINAL, [36.71, 55.0, 73.42, 110.0, 146.8, 185.0], dur=3.6, tau=1.6, bright=3000, gain=1.0)
dn = fx.Buf(LEN)                       # falling 'downer' sweeps
fx.downer(dn, 2.5, 1100, 90, 1.2, gain=0.6, pan=-0.2)
fx.downer(dn, HIT, 1500, 60, 1.3, gain=0.9, pan=0.15)
fx.downer(dn, DOWN, 900, 45, 1.8, gain=1.0)
fx.downer(dn, MEGA, 1800, 55, 1.6, gain=1.0, pan=-0.15)
fx.downer(dn, FINAL + 0.7, 700, 40, 3.0, gain=0.5)
rs = fx.Buf(LEN)                       # risers and reverse swells, cut dead into the hits
fx.riser(rs, 2.6, HIT - GAP, gain=0.8)
fx.reverse_swell(rs, HIT - GAP, 1.4, gain=0.7)
fx.riser(rs, RISE - 0.4, MEGA - GAP, f0=400, f1=11000, tone=(300, 2400), gain=1.0, start_db=-30)
fx.reverse_swell(rs, MEGA - GAP, 1.0, gain=0.9)
fx.reverse_swell(rs, FINAL, 0.5, gain=0.5)
tk = fx.Buf(LEN)                       # mechanical ticks
build_ticks = [3.0 + Q * i for i in range(4)] + grid(4.5, 4.5 + 4 * E, E) + grid(4.5 + 4 * E, HIT - GAP, E / 2)
for i, t in enumerate(build_ticks):
    fx.tick(tk, t, 'click', gain=0.35 + 0.65 * (t - 3.0) / 2.0, pan=(-0.5, 0.5)[i % 2])
for i, t in enumerate(A_BEAT + B_BEAT):
    fx.tick(tk, t, 'click', gain=1.0 if t in ACCENTED else 0.6, pan=(-0.6, 0.6)[i % 2])
for t in B_BEAT:                                               # 16ths in the mega section
    fx.tick(tk, t + E / 2, 'click', gain=0.45, pan=0.3)
for t in BACK:
    fx.tick(tk, t, 'clunk', gain=1.0)
for t in grid(DOWN + 0.2, RISE, Q):
    fx.tick(tk, t, 'click', gain=0.45)
for i, t in enumerate(grid(RISE, MEGA - GAP - 0.2, E / 2) + grid(MEGA - GAP - 0.2, MEGA - GAP, E / 4)):
    fx.tick(tk, t, 'click', gain=0.5 + 0.5 * (t - RISE) / 0.6, pan=(-0.5, 0.5)[i % 2])
for t in (3.6, 9.2):
    fx.tick(tk, t, 'servo', gain=0.6)
mt = fx.Buf(LEN)                       # metal hits
fx.metal(mt, 3.0, 290, gain=0.7, pan=-0.3)
fx.metal(mt, 3.9, 410, 2.0, 0.5, gain=0.8, pan=0.35)
fx.metal(mt, 4.4, 230, 2.0, 0.6, gain=0.9, pan=-0.1)
fx.metal(mt, HIT, 180, 3.0, 1.0, gain=0.8)
fx.metal(mt, DOWN, 150, 3.5, 1.4, gain=1.0)
fx.metal(mt, MEGA, 170, 3.0, 1.1, gain=0.9, pan=0.2)
fx.metal(mt, FINAL, 140, 4.0, 1.8, gain=1.0)
rb = fx.Buf(LEN)                       # low rumble / drone on D
fx.rumble(rb, OPEN, 15.9, 36.71, env=[(OPEN, -18), (2.0, -10), (4.9, 0), (HIT, -6), (DOWN, -6), (8.2, 0), (RISE, 0),
                                      (MEGA, -6), (FINAL, -4), (13.0, -2), (15.9, -40)])

FX = [Part('fx_sub', sub, level=-9, send=0.05), Part('fx_braam', grit, level=-14, send=0.25),
      Part('fx_downer', dn, level=-19, send=0.4), Part('fx_riser', rs, level=-17, send=0.35),
      Part('fx_ticks', tk, level=-21, send=0.25), Part('fx_metal', mt, level=-22, send=0.5),
      Part('fx_rumble', rb, level=-22, send=0.1)]

# ======================= strings
trem_env = [(OPEN, -30), (2.5, -18), (4.0, -7), (HIT - GAP, 0), (HIT - 0.03, -60)]
vct = Part('cello_trem', 'CelloEnsTrem', level=-17, pan=0.3, send=0.4, env=trem_env)
vct.add(OPEN, ['D2', 'A2'], 3.95, 110)
vlt = Part('viola_trem', 'ViolaEnsTrem', level=-19, pan=0.1, send=0.45, env=trem_env)
vlt.add(2.5, ['D3', 'F3'], 1.5, 104).add(4.0, ['E3', 'A3'], 0.95, 116)
vnt = Part('violin_trem', 'ViolinEnsTrem', level=-20, pan=-0.35, send=0.5,
           env=[(3.5, -20), (HIT - GAP, 0), (HIT - 0.03, -60), (RISE - 0.01, -60), (RISE, -14), (MEGA - GAP, 0), (MEGA - 0.03, -60)])
vnt.add(3.5, ['D5', 'A5'], 0.95, 104).add(4.4, ['E5', 'C#6'], 0.55, 118)
for i, p in enumerate(['A4', 'C5', 'E5', 'A5']):
    vnt.add(RISE + i * 0.14, [p, n(p) - 12], 0.18, 100 + i * 8)

# spiccato ostinato: 3-3-2 accents, octave leaps
osc_vc = Part('cello_spic', 'CelloEnsSpic', level=-14, pan=0.3, send=0.25, env=BIGGER)
osc_cb = Part('bass_spic', 'ContrabassSpic', level=-15, pan=0.4, send=0.2, env=BIGGER)
osc_va = Part('viola_spic', 'ViolaEnsSpic', level=-19, pan=0.05, send=0.3)
PAT = [0, 0, 12, 0, 0, 12, 0, 12]
for beats in (A_BEAT, B_BEAT):
    for i, t in enumerate(beats):
        r, _ = chord_at(t)
        v = 124 if i % 8 in ACC else 96
        osc_vc.add(t, in_oct(r, 'C2', 'B2') + PAT[i % 8], E * 0.9, v)
        osc_cb.add(t, in_oct(r, 'C1', 'B1'), E * 0.9, v)
        if beats is B_BEAT:
            osc_va.add(t, in_oct(r, 'C3', 'B3') + PAT[i % 8], E * 0.9, v)
for i, t in enumerate(FILL):
    osc_vc.add(t, n('A2') + (12 if i % 2 else 0), E * 0.45, 100 + i * 2)
    osc_va.add(t, n('A3') + (12 if i % 2 else 0), E * 0.45, 100 + i * 2)

low_env = [(0, -60), (DOWN - 0.01, -60), (DOWN, 0), (RISE, -2), (MEGA - GAP, -6), (MEGA - 0.03, -60)]
vc = Part('cellos', 'CelloEnsSusVib', level=-19, pan=0.3, send=0.4, env=low_env)
cb = Part('basses', 'ContrabassSusVB', level=-19, pan=0.4, send=0.3, env=low_env)
vc.add(DOWN, ['Bb2', 'D3'], 0.75, 90).add(8.75, ['Bb2', 'D3'], 0.65, 84).add(RISE, ['A2', 'E3'], 0.6, 110)
cb.add(DOWN, 'Bb1', 0.75, 92).add(8.75, 'G1', 0.65, 86).add(RISE, 'A1', 0.6, 110)

vln = Part('violins', 'ViolinEnsSusVib', level=-15, pan=-0.35, send=0.45, align=HIT, env=pumped(HOT, -5))
for t, p, d in [(HIT, 'D5', 1.5), (6.5, 'F5', 0.75), (7.25, 'E5', 0.375), (7.625, 'C#5', 0.36)]:
    vln.add(t, [p, n(p) - 12], d + 0.03, 120)
THEME = [(MEGA, 'A5', 0.75), (10.75, 'Bb5', 0.375), (11.125, 'A5', 0.375), (11.5, 'G5', 0.5), (12.0, 'A5', 0.25),
         (12.25, 'C#6', 0.25), (FINAL, 'D6', 3.4)]
for t, p, d in THEME:
    vln.add(t, [p, n(p) - 12], d + 0.03, 126)

# ======================= brass: the low growl of the opening, then the braams
hn = Part('horns', 'FHornSus', level=-12, pan=-0.15, send=0.45, align=HIT, env=pumped([(OPEN, -22), (3.0, -14), (4.9, -5), (HIT, -3)] + HOT[1:], -9))
tbn = Part('trombones', 'TromboneSus', level=-12, pan=0.35, send=0.4, align=HIT, env=pumped([(OPEN, -24), (3.0, -15), (4.9, -6), (HIT, -3)] + HOT[1:], -9))
tba = Part('tuba', 'TubaSus', level=-15, pan=0.4, send=0.3, align=HIT, env=pumped([(OPEN, -24), (4.9, -6), (HIT, -3)] + HOT[1:], -8))
hn.add(OPEN, ['D3', 'A3'], 3.95, 70)
tbn.add(OPEN, ['D2', 'A2'], 3.95, 76)
tba.add(OPEN, 'D2', 3.95, 76)
for s, e, r, tones in PROG:
    d = e - s + (0.03 if e < FINAL else 0)
    hn.add(s, [p for p in tones if n('C3') <= n(p) <= n('A4')][-3:] + (['F#4'] if s == FINAL else []), d, 127)
    tbn.add(s, [p for p in tones if n('A#1') <= n(p) <= n('E3')][:3], d, 127)
    tba.add(s, in_oct(r, 'F1', 'E2'), d, 127)
tpt = Part('trumpets', 'TrumpetSus', level=-12, pan=0.2, send=0.45, align=MEGA, env=pumped(HOT, -4))
for t, p, d in THEME:
    tpt.add(t, n(p) - 12, d + 0.03, 127)
tpt.add(FINAL, ['F#4', 'A4'], 3.4, 124)
stab_hn = Part('horn_stabs', 'FHornStac', level=-15, pan=-0.15, send=0.4, split=True, thresh=0.6, env=BIGGER)
stab_tb = Part('trombone_stabs', 'TromboneStac', level=-15, pan=0.35, send=0.35, split=True, thresh=0.6, env=BIGGER)
for t in ACCENTED:
    if t not in (HIT, MEGA):
        r, tones = chord_at(t)
        stab_hn.add(t, [p for p in tones if n('C3') <= n(p) <= n('A4')][-2:], 0.15, 118)
        stab_tb.add(t, [p for p in tones if n('A#1') <= n(p) <= n('E3')][:2], 0.18, 118)

choir = Part('choir', ('gm', 52), level=-18, pan=-0.05, send=0.55, env=pumped([(3.5, -20), (4.9, -8), (HIT, -3)] + HOT[1:], -7))
choir.add(3.5, ['D3', 'A3', 'D4'], 1.45, 90)
for s, e, r, tones in PROG:
    choir.add(s, [p for p in tones if n('D3') <= n(p) <= n('A4')] + (['D5'] if s >= MEGA else []), e - s + 0.03, 124)

# ======================= drums
drum = Part('bass_drum', 'perc', level=-12, send=0.25, split=True, env=BIGGER)
timp = Part('timpani', 'Timpani', level=-14, pan=-0.15, send=0.3, split=True)
snr = Part('snare', 'perc', level=-17, pan=0.1, send=0.3, split=True, env=BIGGER)
metal_k = Part('metal_hits', 'perc', level=-19, pan=-0.25, send=0.4, split=True)
for beats in (A_BEAT, B_BEAT):
    for i, t in enumerate(beats):
        r, tones = chord_at(t)
        if i % 8 in ACC:
            drum.add(t, PERC['bd'], 1.5, 127 if t in (HIT, MEGA) else 116)
            timp.add(t, in_oct(r, 'C2', 'B2'), 1.0, 124)
        elif beats is B_BEAT and i % 2 == 0:
            drum.add(t, PERC['bdd'], 0.6, 100)
for t in BACK:
    snr.add(t, PERC['snare'], 0.5, 118)
    metal_k.add(t, PERC['brake'], 0.5, 110)
for t in (3.0, 4.4, DOWN):
    metal_k.add(t, PERC['anvil'], 1.0, 120)
for i, t in enumerate(FILL):
    snr.add(t, PERC['snare'], 0.2, 90 + i * 2)
    if i % 2 == 0:
        timp.add(t, n('A2') if i % 4 else n('E2'), 0.4, 112)
for t in (OPEN, DOWN, FINAL):
    drum.add(t, PERC['bd'], 2.5, 96 if t == OPEN else 127)
timp.add(DOWN, 'Bb2', 1.5, 120).add(FINAL, ['D2', 'A2'], 2.5, 127)
troll = Part('timp_roll', 'TimpaniRolls', level=-16, pan=-0.15, send=0.35,
             env=[(3.8, -30), (HIT - GAP, 0), (HIT - 0.03, -60), (RISE - 0.01, -60), (RISE, -16), (MEGA - GAP, 0), (MEGA - 0.03, -60)])
troll.add(3.8, 'A2', 1.2, 110).add(RISE, 'A2', 0.6, 116)
cym = Part('cymbals', 'perc', level=-18, pan=0.15, send=0.45, split=True)
cym.add(HIT, PERC['crash'], 3.0, 127).add(MEGA, PERC['crash'], 3.0, 127).add(FINAL, PERC['crash'], 3.0, 127)
cym.add(6.5, PERC['crash'], 1.5, 100).add(10.75, PERC['crash'], 1.5, 104).add(11.5, PERC['crash'], 1.5, 104)
gong = Part('gong', 'perc', level=-19, pan=-0.1, send=0.5, split=True, env=[(0, 0)] + FADE)
gong.add(DOWN, PERC['gong'], 1.4, 100).add(MEGA, PERC['gong'], 2.5, 124).add(FINAL, PERC['gong'], 3.4, 127)
ratchet = Part('ratchet', 'perc', level=-24, pan=0.45, send=0.35, env=[(0, -6), (4.9, 0), (HIT - 0.05, -60)])
ratchet.add(4.0, PERC['ratchet_fast'], 0.93, 110)

PARTS = FX + [vct, vlt, vnt, osc_vc, osc_cb, osc_va, vc, cb, vln, hn, tbn, tba, tpt, stab_hn, stab_tb, choir,
              drum, timp, snr, metal_k, troll, cym, gong, ratchet]
ACCENTS = [OPEN, HIT, DOWN, MEGA, FINAL]

if __name__ == '__main__':
    out = sys.argv[1]
    y, rep = build('TAGS_theme', PARTS, LEN, os.path.join(out, 'build'), reverb=(80, 50, 100, 100, 30, 0), wet=0.3,
                   fade=(14.8, 15.95))
    wav, ogg = export(y, out, 'TAGS_theme')
    save_score([p for p in PARTS if not callable(p.inst)], os.path.join(out, 'TAGS_theme.mid'))
    y = decode(ogg)
    rep['length_samples'] = len(y)
    rep['ogg_peak_dbfs'] = round(ogg_peak_db(ogg), 2)
    rep['accents'] = {str(round(t, 2)): round(accent_time(y, t), 4) for t in ACCENTS}
    json.dump(rep, open(os.path.join(out, 'TAGS_theme_report.json'), 'w'), indent=1)
    print(json.dumps(rep['accents']))
