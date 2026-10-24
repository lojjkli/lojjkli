"""TAGS_theme - 16.0 s studio intro. Shaped after measurements of a modern
animation-studio intro (one long crescendo from silence, bass weight arriving
late, a whole-step key change at the big moment, rhythmic orchestral hits about
once a second instead of a drum beat, a quiet minor-iv dip, a second, bigger
lift and a slow ring-out). All music is original; the melody is the TAGS tune.

0.0-5.0   from silence, one continuous crescendo in B-flat: strings, celesta, harp,
          flute with the TAGS melody, choir; cellos/basses only from 2.5 s, the sub
          weight (timpani roll, bass drum, tuba) only in the last 1.5 s;
          Bb - Eb/Bb - Gm7 - Eb - F - Ab - Bb  ->  lift
5.0       KEY CHANGE UP TO C: full orchestra and choir, the melody soars
5.0-8.0   loud plateau: brass + timpani hits about every 0.9 s; C - Am - F - G
8.0-9.4   the dip: soft strings, harp and celesta, F -> Fm (minor iv)
9.4-10.0  riser: timpani roll, harp glissando, strings climb, cymbal swell
10.0      MEGA UP: key change up to D, everything bigger; hits speed up
          (10.0 10.75 11.5 12.0 12.25) into D - G - A - D
12.5      final grand D major chord, held; from 13.0 it slowly fades to silence by 16.0."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orch import Part, PERC, build, export, save_score, accent_time, decode, ogg_peak_db, n

LEN = 16.0
LIFT, DIP, RISE, MEGA, FINAL = 5.0, 8.0, 9.4, 10.0, 12.5
HITS1 = [5.0, 5.9, 6.8, 7.7]
HITS2 = [10.0, 10.75, 11.5, 12.0, 12.25]
FADE = [(FINAL, 0), (13.0, -1), (14.3, -9), (15.9, -50)]

# global dynamic shape (dB): silence -> long crescendo -> plateau -> dip -> mega -> ring-out
SHAPE = [(0.3, -32), (1.5, -25), (2.5, -19), (3.5, -13), (4.5, -6), (4.95, -3), (5.0, 0), (7.95, 0), (8.15, -12), (9.3, -12),
         (9.95, -4), (10.0, 2), (12.5, 2)] + [(t, d + 2) for t, d in FADE[1:]]


def env(*extra):
    return SHAPE + list(extra) if not extra else sorted(SHAPE + list(extra))


# ---- harmony: (start, end, root, chord tones low->high)
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


# ======================= melody (the TAGS tune, adapted)
MEL1 = [(0.9, 'F4', .5), (1.4, 'C5', .6), (2.0, 'D5', .3), (2.3, 'C5', .3), (2.6, 'Bb4', .5),
        (3.1, 'D5', .4), (3.5, 'F5', .5), (4.0, 'G5', .3), (4.3, 'F5', .3), (4.6, 'A5', .3), (4.82, 'Bb5', .2)]
MEL2 = [(5.0, 'C6', .9), (5.9, 'B5', .3), (6.2, 'A5', .3), (6.5, 'E5', .3), (6.8, 'F5', .45), (7.25, 'A5', .45),
        (7.7, 'D6', .3), (7.85, 'B5', .17)]
MEL_DIP = [(8.05, 'A4', .5), (8.55, 'G4', .2), (8.75, 'Ab4', .6), (9.35, 'G4', .1)]
MEL3 = [(10.0, 'D6', .75), (10.75, 'C#6', .3), (11.05, 'B5', .45), (11.5, 'A5', .5), (12.0, 'B5', .25), (12.25, 'C#6', .25),
        (12.5, 'D6', 3.0)]

fl = Part('flute', 'FluteSusVib', level=-18, pan=-0.1, send=0.45, env=[(0.8, -8), (2.0, -4), (3.0, -1), (4.0, 2), (4.9, 2), (5.0, 0), (8.0, 0), (8.2, 3), (9.4, 3), (10.0, 0)] + FADE)
for t, p, d in MEL1 + MEL_DIP:
    fl.add(t, p, d + 0.04, 82)
for t, p, d in MEL3:
    if t < FINAL:
        fl.add(t, n(p) + 12 if n(p) + 12 <= 96 else n(p), d + 0.03, 118)
fl.add(FINAL, 'D6', 3.0, 116)
vln = Part('violins', 'ViolinEnsSusVib', level=-14, pan=-0.35, send=0.45, align=LIFT, env=env())
for t, p, d in MEL1[5:] + MEL2 + MEL3:
    vln.add(t, p, d + 0.04, 90 if t < LIFT else 124)
vln_soft = Part('violins_soft', 'ViolinEnsSusVib-Quiet', level=-20, pan=-0.3, send=0.55, env=[(0.3, -16), (1.5, -10), (2.5, -5), (3.5, -2), (4.5, 0), (5.0, -40)])
for s, e, r, tones in PROG:
    if s < LIFT:
        vln_soft.add(s, tones[-2:], e - s + 0.05, 60)
vla = Part('violas', 'ViolaEnsSusVib', level=-18, pan=0.15, send=0.4, align=LIFT, env=env())
vc = Part('cellos', 'CelloEnsSusVib', level=-15, pan=0.3, send=0.35, align=LIFT, env=env((2.4, -40), (2.5, -16)))
cb = Part('basses', 'ContrabassSusVB', level=-16, pan=0.4, send=0.3, align=LIFT, env=env((2.4, -40), (2.5, -20)))
for s, e, r, tones in PROG:
    d = e - s + 0.04
    hot = s >= LIFT
    vla.add(s, [p for p in tones if n('Bb3') <= n(p) <= n('A4')][:2] or [tones[2]], d, 118 if hot else 72)
    if s >= 2.4:
        vc.add(s, [p for p in tones if n('C2') <= n(p) <= n('D3')][:2], d, 122 if hot else 80)
        lo = n(tones[0]) - 12 if n(tones[0]) - 12 >= n('C1') else n(tones[0])
        cb.add(s, lo, d, 122 if hot else 76)
trem = Part('violin_trem', 'ViolinEnsTrem', level=-21, pan=-0.4, send=0.5,
            env=[(9.3, -60), (9.4, -14), (9.95, 0), (10.0, -60)])
for i, p in enumerate(['D5', 'E5', 'F#5', 'G5']):
    trem.add(9.4 + i * 0.15, [p, n(p) - 12], 0.2, 96 + i * 8)

# ======================= choir
choir = Part('choir', ('gm', 52), level=-18, pan=-0.05, send=0.55, env=env((1.75, -40), (1.8, -20)))
for s, e, r, tones in PROG:
    if s >= 1.8:
        choir.add(s, [p for p in tones if n('F3') <= n(p) <= n('A4')], e - s + 0.04, 120 if s >= LIFT else 84)

# ======================= sparkle
cel = Part('celesta', ('gm', 8), level=-21, pan=-0.3, send=0.55, env=[(0.3, -14), (1.5, -9), (2.6, -4), (3.0, 0), (5.0, -4), (8.0, 2), (9.4, 0), (10.0, -2)] + FADE)
for i, t in enumerate([0.35, 0.6, 0.85, 1.1, 1.35, 1.6, 1.85, 2.1, 2.35, 2.6]):
    cel.add(t, ['F6', 'Bb6', 'D7', 'C7', 'F7', 'D7', 'Bb6', 'Eb7', 'G7', 'Bb7'][i], 0.5, 54 + (i % 3) * 6)
for t in HITS1 + HITS2:
    r, tones = chord(t)
    cel.add(t, [n(tones[-1]) + 24, n(tones[-2]) + 24], 0.8, 92)
for i, p in enumerate(['C7', 'Ab6', 'F6', 'C6']):
    cel.add(8.1 + i * 0.3, p, 0.7, 70)
harp = Part('harp', 'Harp', level=-17, pan=-0.55, send=0.45, split=True, env=[(0, -14), (1.5, -10), (2.5, -7), (3.5, -4), (4.5, 0)])
for s, e, r, tones in PROG[:5]:
    for i, p in enumerate(tones):
        harp.add(s + i * 0.08, p, 1.5, 58 + i * 2 + int(s * 3))
sweep = [p for p in range(n('Bb3'), n('C7') + 1) if p % 12 in (10, 0, 2, 3, 5, 7, 9)]
for i, p in enumerate(sweep):
    harp.add(4.35 + 0.6 * (i / len(sweep)) ** 0.8, p, 0.4, 70 + i * 2)
for i, p in enumerate(['F2', 'C3', 'Ab3', 'C4', 'F4', 'Ab4']):
    harp.add(8.05 + i * 0.12, p, 1.5, 70)
for i, p in enumerate([p for p in range(n('G3'), n('D7') + 1) if p % 12 in (7, 9, 11, 0, 2, 4, 6)]):
    harp.add(9.4 + i * 0.022, p, 0.4, 76 + i)
harp.add(LIFT, ['C2', 'G2', 'C3', 'E3', 'G3', 'C4'], 2.0, 124)
harp.add(MEGA, ['D2', 'A2', 'D3', 'F#3', 'A3', 'D4'], 2.0, 124).add(FINAL, ['D2', 'A2', 'D3', 'F#3', 'A3', 'D4', 'F#4'], 3.0, 124)
glock = Part('glock', 'Glockenspiel', level=-23, pan=0.3, send=0.5, split=True)
for t in HITS1 + HITS2 + [FINAL]:
    r, tones = chord(t)
    glock.add(t, [n(tones[-1]) + 12 if n(tones[-1]) + 12 <= 96 else n(tones[-1])], 1.0, 104)

# ======================= brass
hn = Part('horns', 'FHornSus', level=-12, pan=-0.15, send=0.45, align=LIFT, env=env((3.7, -40), (3.8, -16)))
tpt = Part('trumpets', 'TrumpetSus', level=-12, pan=0.2, send=0.45, align=LIFT, env=env())
tbn = Part('trombones', 'TromboneSus', level=-13, pan=0.35, send=0.4, align=LIFT, env=env((4.3, -40), (4.4, -12)))
tba = Part('tuba', 'TubaSus', level=-16, pan=0.4, send=0.3, align=LIFT, env=env((4.3, -40), (4.4, -12)))
for s, e, r, tones in PROG:
    if s >= 3.8:
        d = e - s + 0.04
        hot = s >= LIFT
        hn.add(s, [p for p in tones if n('C3') <= n(p) <= n('G4')][-3:], d, 124 if hot else 90)
        if s >= 4.4:
            tbn.add(s, [p for p in tones if n('A#1') <= n(p) <= n('E3')][:3], d, 124 if hot else 96)
            lo = tones[0] if n(tones[0]) >= n('F1') else n(tones[0]) + 12
            tba.add(s, lo, d, 124 if hot else 96)
for t, p, d in MEL2 + MEL3:                                     # trumpets: the melody an octave down
    if t < FINAL:
        tpt.add(t, n(p) - 12, d + 0.03, 124)
tpt.add(FINAL, ['A4', 'D5', 'F#5'], 3.0, 127)
# rhythmic brass hits (staccato) on the hit grid
tpt_st = Part('trumpet_hits', 'TrumpetStac', level=-15, pan=0.2, send=0.4, split=True, thresh=0.6)
tbn_st = Part('trombone_hits', 'TromboneStac', level=-15, pan=0.35, send=0.35, split=True, thresh=0.6)
for t in HITS1[1:] + HITS2[1:]:
    r, tones = chord(t)
    tpt_st.add(t, [p for p in tones if n('E4') <= n(p) <= n('A5')][:2] or [n(tones[-1])], 0.15, 112)
    tbn_st.add(t, [p for p in tones if n('A#1') <= n(p) <= n('E3')][:2], 0.18, 112)

# ======================= weight: timpani, bass drum, cymbals, gong, bells
timp = Part('timpani', 'Timpani', level=-13, pan=-0.15, send=0.3, split=True)
for t in HITS1 + HITS2 + [FINAL]:
    r, tones = chord(t)
    low = [p for p in tones if n('C2') <= n(p) <= n('A2')][:2] or [n(tones[0]) + 12]
    timp.add(t, low, 1.2, 127 if t in (LIFT, MEGA, FINAL) else 110)
troll = Part('timp_roll', 'TimpaniRolls', level=-16, pan=-0.15, send=0.35,
             env=[(3.5, -30), (4.95, 0), (4.99, -60), (9.39, -60), (9.4, -14), (9.95, 0), (9.99, -60), (12.24, -60), (12.25, -6), (12.48, 0), (12.5, -60)])
troll.add(3.5, 'F2', 1.5, 110).add(9.4, 'A2', 0.6, 110).add(12.25, 'A2', 0.27, 110)
drum = Part('bass_drum', 'perc', level=-13, pan=0.0, send=0.3, split=True)
for t in HITS1 + HITS2 + [FINAL]:
    drum.add(t, PERC['bd'], 2.5, 127 if t in (LIFT, MEGA, FINAL) else 108)
cym = Part('cymbals', 'perc', level=-18, pan=0.15, send=0.45, split=True)
cym.add(LIFT, PERC['crash'], 3.0, 127).add(MEGA, PERC['crash'], 3.0, 127).add(FINAL, PERC['crash'], 3.0, 124)
for t in (6.8, 11.5):
    cym.add(t, PERC['crash'], 2.0, 96)
cym.add(0.3, PERC['bow'], 4.0, 100)
swell = Part('cym_swell', 'perc', level=-21, pan=0.1, send=0.5, thresh=0.001)
swell.add(LIFT - 3.81, PERC['swell_m'], 3.85, 120).add(MEGA - 1.53, PERC['swell_s'], 1.55, 124)
gong = Part('gong', 'perc', level=-20, pan=-0.1, send=0.5, split=True, env=[(0, 0)] + FADE)
gong.add(MEGA, PERC['gong'], 2.5, 110).add(FINAL, PERC['gong'], 3.4, 124)
bells = Part('bells', 'TubularBells', level=-21, pan=0.2, send=0.55, split=True)
bells.add(LIFT, ['G4', 'C5'], 3.0, 116).add(MEGA, ['A4', 'D5'], 2.5, 120).add(FINAL, ['A4', 'D5', 'F#5'], 3.4, 124)
tree = Part('bell_tree', 'perc', level=-24, pan=-0.2, send=0.6, split=True)
tree.add(0.3, PERC['tree4'], 2.0, 80).add(LIFT, PERC['tree1'], 2.0, 110).add(MEGA, PERC['tree1'], 2.0, 116).add(FINAL, PERC['tree2'], 2.0, 110)

PARTS = [fl, vln, vln_soft, vla, vc, cb, trem, choir, cel, harp, glock, hn, tpt, tbn, tba, tpt_st, tbn_st,
         timp, troll, drum, cym, swell, gong, bells, tree]
ACCENTS = [LIFT, DIP, MEGA, FINAL]

if __name__ == '__main__':
    out = sys.argv[1]
    y, rep = build('TAGS_theme', PARTS, LEN, os.path.join(out, 'build'), reverb=(78, 38, 100, 100, 28, 0), wet=0.36,
                   fade=(14.6, 15.95))
    wav, ogg = export(y, out, 'TAGS_theme')
    save_score(PARTS, os.path.join(out, 'TAGS_theme.mid'))
    y = decode(ogg)
    rep['length_samples'] = len(y)
    rep['ogg_peak_dbfs'] = round(ogg_peak_db(ogg), 2)
    rep['accents'] = {str(round(t, 2)): round(accent_time(y, t), 4) for t in ACCENTS}
    json.dump(rep, open(os.path.join(out, 'TAGS_theme_report.json'), 'w'), indent=1)
    print(json.dumps(rep['accents']))
