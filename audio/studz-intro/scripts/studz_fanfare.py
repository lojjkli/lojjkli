"""Studz_fanfare - game logo, exactly 14.8 s, B-flat major, warm brass + strings.
0-4     dusk over a calm lake: rippling harp, soft strings, bowed cymbal shimmer;
        two runs of skipping bricks (celesta/harp, each skip quieter and faster)
        ending in splashes (bell tree, soft cymbal, harp drip, timpani plop)
4-9.5   rising through the clouds: horn theme, strings and winds build,
        trombones/tuba join, trumpets answer, timpani, long cymbal swell
8.8-10  letters fly in one by one: 5 trumpet/timpani/glock steps + rising
        flourish (violin spiccato, flute, harp glissando)
10.0    logo lands: B-flat tutti with tubular bells, crash, gong, timpani
10-14.8 held chord decays to silence."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orch import Part, PERC, build, export, save_score, spectral_flux_onset, decode, ogg_peak_db, n

T_HIT = 10.0
LETTERS = [8.80, 9.04, 9.28, 9.52, 9.76]
LEN = 14.8
BB = [0, 2, 4, 5, 7, 9, 10]                       # B-flat major degrees from Bb


def bb_scale(lo, hi):
    return [p for p in range(n(lo), n(hi) + 1) if (p - n('Bb0')) % 12 in BB]


SKIM1 = [(1.10, 'C7', 74), (1.42, 'A6', 66), (1.70, 'F6', 58), (1.94, 'D6', 52)]
SKIM2 = [(2.95, 'D7', 76), (3.22, 'Bb6', 68), (3.45, 'G6', 62), (3.64, 'Eb6', 56)]
SPLASH = [2.22, 3.86]

# ---- keyboards / mallets / harp
cel = Part('celesta', ('gm', 8), level=-23, pan=-0.3, send=0.45)
cel.add(0.40, 'F6', 0.6, 46).add(0.75, 'C7', 0.6, 42)
for t, p, v in SKIM1 + SKIM2:
    cel.add(t, p, 0.35, v)
cel.add(T_HIT, ['D6', 'F6', 'Bb6'], 1.5, 100)

harp = Part('harp', 'Harp', level=-19, pan=-0.55, send=0.4, align=T_HIT)
rip1 = ['Bb2', 'F3', 'D4', 'A4', 'C5', 'F5', 'A4', 'D4']
rip2 = ['Eb2', 'Bb2', 'G3', 'D4', 'F4', 'A4', 'G4', 'D4']
for i in range(10):
    harp.add(0.02 + i * 0.2, rip1[i % 8], 1.2, 52 + (i % 3) * 4)
for i in range(10):
    harp.add(2.02 + i * 0.19, rip2[i % 8], 1.2, 52 + (i % 3) * 4)
for t, p, v in SKIM1 + SKIM2:
    harp.add(t + 0.005, n(p) - 12, 0.4, v - 6)
for t0, top in zip(SPLASH, ['C7', 'D7']):           # drip-down after each splash
    down = [p for p in bb_scale('C5', top)][::-1]
    for i, p in enumerate(down):
        harp.add(t0 + 0.02 + i * 0.022, p, 0.5, 72 - i)
up = bb_scale('Bb3', 'Bb6')                          # flourish glissando up to the landing
for i, p in enumerate(up):
    u = i / (len(up) - 1)
    harp.add(8.80 + 1.12 * u ** 0.8, p, 0.6, 70 + 40 * u)
harp.add(T_HIT, ['Bb1', 'Bb2', 'F3', 'Bb3', 'D4', 'F4', 'Bb4'], 3.0, 120)

glock = Part('glock', 'Glockenspiel', level=-24, pan=0.3, send=0.45, align=T_HIT)
glock.add(0.62, 'F6', 1.0, 40).add(1.60, 'C7', 1.0, 36).add(2.22, 'F6', 1.0, 60).add(3.86, 'Bb6', 1.0, 66)
for t, p in zip(LETTERS, ['F6', 'G6', 'A6', 'Bb6', 'C7']):
    glock.add(t, p, 0.8, 92)
glock.add(T_HIT, ['D6', 'Bb6'], 2.0, 114)

bells = Part('bells', 'TubularBells', level=-21, pan=0.2, send=0.5, align=T_HIT)
bells.add(T_HIT, ['F4', 'Bb4'], 4.5, 120)

perc = Part('perc', 'perc', level=-19, pan=0.05, send=0.45, align=T_HIT)
perc.add(0.10, PERC['bow'], 4.0, 100)                       # lake shimmer
perc.add(SPLASH[0], PERC['tree2'], 2.0, 90).add(SPLASH[0], PERC['cym'], 1.5, 40)
perc.add(SPLASH[1], PERC['tree3'], 2.0, 100).add(SPLASH[1], PERC['cym'], 1.5, 64)
perc.add(T_HIT - 7.20, PERC['swell_l'], 7.4, 110)           # long roll peaks at the landing
perc.add(T_HIT, PERC['crash'], 4.0, 127).add(T_HIT, PERC['bd'], 3.0, 124).add(T_HIT, PERC['gong'], 4.5, 96)

timp = Part('timpani', 'Timpani', level=-16, pan=-0.1, send=0.35, align=T_HIT)
timp.add(SPLASH[1], 'Bb2', 1.0, 36)                          # the splash "plop"
for t, p, v in [(4.0, 'Bb2', 62), (5.0, 'G2', 58), (5.75, 'Eb2', 60), (6.5, 'C3', 66), (7.25, 'F2', 72)]:
    timp.add(t, p, 0.9, v)
for i, (t, p) in enumerate(zip(LETTERS, ['F2', 'G2', 'A2', 'Bb2', 'C3'])):
    timp.add(t, p, 0.4, 96 + i * 5)
timp.add(T_HIT, ['F2', 'Bb2'], 3.0, 127)
troll = Part('timp_roll', 'TimpaniRolls', level=-20, pan=-0.1, send=0.35, env=[(8.0, -20), (8.78, -5), (8.82, -60)])
troll.add(8.0, 'F2', 0.85, 100)

# ---- strings
END = [(T_HIT, 0), (11.0, -2), (12.8, -11), (14.4, -40)]
vtrem = Part('vln_trem', 'ViolinEnsTrem', level=-28, pan=-0.35, send=0.5,
             env=[(0, -12), (1.0, -6), (3.6, -6), (4.2, -30), (8.0, -16), (9.95, -2), (10.1, -60)])
vtrem.add(0.15, ['A5', 'D6'], 4.1, 34).add(8.0, ['A5', 'C6'], 2.1, 90)
vlnq = Part('violins_soft', 'ViolinEnsSusVib-Quiet', level=-25, pan=-0.35, send=0.45, env=[(0, -8), (1.0, 0), (4.3, -1), (5.2, -40)])
vlnq.add(0.0, ['D5', 'A5'], 2.15, 44).add(2.0, ['Bb4', 'G5'], 3.1, 44)
vln = Part('violins', 'ViolinEnsSusVib', level=-18, pan=-0.35, send=0.4, align=T_HIT, env=[(4.7, -12), (5.6, -9), (6.3, -5), (7.5, -4), (9.0, -1)] + END)
for t, ps, d, v in [(5.0, ['D5', 'G5'], .8, 70), (5.75, ['Eb5', 'G5'], .8, 74), (6.5, ['Eb5', 'G5'], .8, 80),
                    (7.25, ['F5', 'Bb5'], .8, 86), (8.0, ['Eb5', 'Bb5'], .84, 92), (8.8, ['Eb5', 'A5'], 1.22, 98)]:
    vln.add(t, ps, d, v)
vln.add(T_HIT, ['F5', 'Bb5', 'D6'], 3.4, 120)
vspic = Part('violins_run', 'ViolinEnsSpic', level=-21, pan=-0.3, send=0.45)
for i, p in enumerate(bb_scale('Bb4', 'D6')):
    vspic.add(9.02 + i * 0.094, p, 0.12, 84 + i * 3)
vla = Part('violas', 'ViolaEnsSusVib', level=-21, pan=0.15, send=0.4, align=T_HIT, env=[(0, -6), (3.9, -6), (4.2, -7), (6.3, -3), (9.0, 0)] + END)
vla.add(0.0, ['F4', 'C5'], 2.15, 42).add(2.0, ['Eb4', 'Bb4'], 2.1, 44)
for t, ps, d, v in [(4.0, ['D4', 'F4'], 1.02, 62), (5.0, ['D4', 'G4'], .8, 66), (5.75, ['Eb4', 'G4'], .8, 70), (6.5, ['Eb4', 'G4'], .8, 76),
                    (7.25, ['Eb4', 'Bb4'], .8, 82), (8.0, ['F4', 'Bb4'], .84, 88), (8.8, ['F4', 'A4'], 1.22, 96)]:
    vla.add(t, ps, d, v)
vla.add(T_HIT, ['D4', 'F4', 'Bb4'], 3.4, 118)
vc = Part('cellos', 'CelloEnsSusVib', level=-19, pan=0.3, send=0.35, align=T_HIT, env=[(0, -6), (4.0, -3), (9.0, 0)] + END)
vc.add(0.0, 'Bb2', 2.15, 44).add(2.0, 'Eb3', 2.0, 44)
for t, p, d, v in [(3.95, 'Bb2', 1.07, 62), (5.0, 'G2', .8, 66), (5.75, 'Eb2', .8, 70), (6.5, 'C2', .8, 76),
                   (7.25, 'F2', .8, 82), (8.0, 'F2', .84, 88), (8.8, 'F2', 1.22, 96)]:
    vc.add(t, p, d, v)
vc.add(T_HIT, ['Bb2', 'F3'], 3.4, 120)
cb = Part('basses', 'ContrabassSusVB', level=-21, pan=0.4, send=0.3, align=T_HIT, env=[(0, -6), (4.0, -3), (9.0, 0)] + END)
cb.add(0.0, 'Bb1', 2.15, 40).add(2.0, 'Eb2', 2.0, 40)
for t, p, d, v in [(3.95, 'Bb1', 1.07, 58), (5.0, 'G1', .8, 62), (5.75, 'Eb1', .8, 66), (6.5, 'C1', .8, 72),
                   (7.25, 'F1', .8, 78), (8.0, 'F1', .84, 84), (8.8, 'F1', 1.22, 94)]:
    cb.add(t, p, d, v)
cb.add(T_HIT, 'Bb1', 3.4, 120)

# ---- winds
MELODY = [(4.00, 'Bb3', .48, 82), (4.45, 'F4', .48, 86), (4.90, 'Bb4', .92, 92), (5.80, 'A4', .27, 84), (6.05, 'G4', .27, 84),
          (6.30, 'F4', .62, 90), (6.90, 'Eb4', .32, 86), (7.20, 'F4', .32, 90), (7.50, 'G4', .32, 94), (7.80, 'Bb4', 1.02, 104)]
fl = Part('flute', 'FluteSusVib', level=-23, pan=-0.1, send=0.45, align=T_HIT, env=[(7.2, -4), (9.0, 0)] + END)
fl.add(7.25, 'F5', .8, 70).add(8.0, 'Eb6', .82, 84)
for i, p in enumerate(bb_scale('F5', 'Bb6')):
    fl.add(9.0 + i * 0.085, p, 0.1, 78 + i * 3)
fl.add(T_HIT, ['Bb5', 'D6'], 3.0, 112)
picc = Part('piccolo', 'PiccoloSus', level=-28, pan=-0.05, send=0.45, align=T_HIT, env=END)
picc.add(T_HIT, 'F6', 2.5, 104)
cl = Part('clarinet', 'ClarinetSus', level=-26, pan=0.15, send=0.4, env=[(4.0, -2), (8.0, 0)] + END)
for t, p, d, v in MELODY:
    cl.add(t, p, d, v - 14)
cl.add(T_HIT, 'D5', 3.0, 108)
ob = Part('oboe', 'OboeSusVib', level=-26, pan=0.05, send=0.4, align=T_HIT, env=END)
ob.add(8.0, 'Eb5', .82, 80).add(8.8, 'Eb5', 1.15, 90).add(T_HIT, 'F5', 3.0, 108)
bsn = Part('bassoon', 'BassoonSus', level=-27, pan=0.25, send=0.35, align=T_HIT, env=END)
for t, p, d, v in [(5.0, 'G2', .8, 70), (5.75, 'Eb2', .8, 72), (6.5, 'C2', .8, 78), (7.25, 'F2', .8, 82), (8.0, 'F2', .84, 88), (8.8, 'F2', 1.15, 94)]:
    bsn.add(t, p, d, v)
bsn.add(T_HIT, 'Bb2', 3.0, 110)

# ---- brass
BEND = [(T_HIT, 0), (10.8, -3), (12.4, -12), (13.6, -40)]
hn = Part('horns', 'FHornSus', level=-17, pan=-0.15, send=0.45, align=T_HIT, env=[(4.0, -3), (4.85, -3), (5.0, -8), (6.2, -6), (7.8, -1), (9.0, 0)] + BEND)
for t, p, d, v in MELODY:
    hn.add(t, p, d, v)
hn.add(8.8, ['A3', 'C4', 'Eb4'], 1.15, 104)
hn.add(T_HIT, ['Bb3', 'D4', 'F4', 'Bb4'], 3.2, 122)
hn2 = Part('horns2', 'FHornSus', level=-21, pan=-0.2, send=0.45, env=[(4.9, -12), (6.2, -7), (8.0, 0)])
for t, p, d, v in [(4.90, 'F4', .92, 80), (5.80, 'Eb4', .52, 78), (6.30, 'C4', .62, 82), (6.90, 'Bb3', .32, 80),
                   (7.20, 'C4', .32, 84), (7.50, 'Eb4', .32, 88), (7.80, 'F4', .22, 92), (8.0, ['F3', 'C4', 'Eb4'], .82, 96)]:
    hn2.add(t, p, d, v)
tpt = Part('trumpets', 'TrumpetSus', level=-18, pan=0.2, send=0.45, align=T_HIT, env=[(7.2, -4), (9.0, 0)] + BEND)
tpt.add(7.25, 'F4', .25, 88).add(7.50, 'Bb4', .25, 92).add(7.75, 'D5', .27, 96).add(8.0, ['Bb4', 'Eb5'], .76, 98)
for i, (t, ps) in enumerate(zip(LETTERS, [['F4', 'A4'], ['G4', 'Bb4'], ['A4', 'C5'], ['Bb4', 'D5'], ['C5', 'Eb5']])):
    tpt.add(t, ps, 0.17, 100 + i * 3)
tpt.add(T_HIT, ['Bb4', 'D5', 'F5'], 2.8, 124)
tbn = Part('trombones', 'TromboneSus', level=-19, pan=0.35, send=0.4, align=T_HIT, env=[(6.5, -4), (9.0, 0)] + BEND)
for t, ps, d, v in [(6.5, ['C3', 'G3'], .8, 78), (7.25, ['Eb3', 'Bb3'], .8, 84), (8.0, ['F3', 'Bb3', 'Eb4'], .82, 92),
                    (8.8, ['F3', 'A3', 'Eb4'], 1.15, 104)]:
    tbn.add(t, ps, d, v)
tbn.add(T_HIT, ['Bb2', 'F3', 'D4'], 3.0, 122)
tba = Part('tuba', 'TubaSus', level=-21, pan=0.4, send=0.35, align=T_HIT, env=[(6.5, -4), (9.0, 0)] + BEND)
for t, p, d, v in [(6.5, 'C2', .8, 78), (7.25, 'Eb2', .8, 82), (8.0, 'F1', .82, 90), (8.8, 'F1', 1.15, 100)]:
    tba.add(t, p, d, v)
tba.add(T_HIT, 'Bb1', 3.0, 120)

PARTS = [cel, harp, glock, bells, perc, timp, troll, vtrem, vlnq, vln, vspic, vla, vc, cb, fl, picc, cl, ob, bsn,
         hn, hn2, tpt, tbn, tba]

if __name__ == '__main__':
    out = sys.argv[1]
    y, rep = build('Studz_fanfare', PARTS, LEN, os.path.join(out, 'build'), reverb=(65, 45, 100, 100, 22, 0), wet=0.34,
                   fade=(12.6, 14.75))
    wav, ogg = export(y, out, 'Studz_fanfare')
    save_score(PARTS, os.path.join(out, 'Studz_fanfare.mid'))
    y = decode(ogg)                         # measure on the delivered file
    rep['length_samples'] = len(y)
    rep['ogg_peak_dbfs'] = round(ogg_peak_db(ogg), 2)
    rep['accents'] = {str(t): round(spectral_flux_onset(y, t), 4) for t in SPLASH + LETTERS + [T_HIT]}
    json.dump(rep, open(os.path.join(out, 'Studz_fanfare_report.json'), 'w'), indent=1)
    print(json.dumps(rep['accents']))
