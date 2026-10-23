"""TAGS_ident - studio logo, exactly 10.1 s, D major.
0-2.3   night sky: celesta twinkles over a floating G-lydian chord (Gmaj7#11)
2.3-5.3 shooting star: bell-tree sparkle, accelerating harp glissando,
        rising violins, Em9 -> Bm7 -> A7sus4 -> A7, timpani roll + cymbal swell
5.3     logo lights up: full orchestra D major + tubular bells, crash, timpani
5.55 6.1 6.55 7.2 7.75  firework sparkles (glock, celesta, harp, triangle)
then the chord rings out and fades to silence by 10.1 s."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orch import Part, PERC, build, export, save_score, spectral_flux_onset, decode, ogg_peak_db, n

T_HIT = 5.3
FW = [5.55, 6.10, 6.55, 7.20, 7.75]
LEN = 10.1

cel = Part('celesta', ('gm', 8), level=-23, pan=-0.3, send=0.45)
for t, p in [(0.12, 'B5'), (0.38, 'F#6'), (0.62, 'D6'), (0.86, 'A6'), (1.10, 'C#7'), (1.38, 'B6'),
             (1.62, 'F#6'), (1.90, 'A6'), (2.16, 'D7')]:
    cel.add(t, p, 0.7, 64)
for t, p, v in [(2.62, 'E6', 58), (3.10, 'G6', 62), (3.58, 'B6', 66), (4.02, 'D7', 70), (4.42, 'E7', 74), (4.80, 'G7', 78)]:
    cel.add(t, p, 0.5, v)
cel.add(T_HIT, ['D6', 'A6', 'D7'], 1.2, 104)
for t, ps in zip(FW, [['A6', 'E7'], ['D7', 'F#7'], ['B6', 'F#7'], ['E7', 'A7'], ['D7', 'A7']]):
    cel.add(t, ps, 0.8, 92)
for t, p, v in [(8.30, 'D7', 60), (8.62, 'A6', 54), (8.95, 'F#6', 50), (9.30, 'D6', 44)]:
    cel.add(t, p, 0.8, v)

harp = Part('harp', 'Harp', level=-19, pan=-0.55, send=0.4, align=T_HIT)
for i, p in enumerate(['G2', 'D3', 'B3', 'F#4', 'C#5']):
    harp.add(0.00 + i * 0.07, p, 2.0, 58 + i * 2)
for i, p in enumerate(['D4', 'F#4', 'A4', 'C#5', 'E5']):
    harp.add(1.25 + i * 0.07, p, 1.5, 50 + i * 2)
# shooting-star glissando: D major, D3 -> D7, accelerating, getting louder
scale = [p for p in range(n('D3'), n('D7') + 1) if (p - n('D3')) % 12 in (0, 2, 4, 5, 7, 9, 11)]
k = len(scale)
for i, p in enumerate(scale):
    u = i / (k - 1)
    harp.add(2.30 + 2.80 * u ** 0.62, p, 0.6, 46 + 60 * u)
for i, p in enumerate([p for p in scale if p >= n('D5')]):
    harp.add(4.62 + i * 0.045, p, 0.5, 70 + i * 2)
harp.add(T_HIT, ['D2', 'D3', 'A3', 'D4', 'F#4', 'D5'], 2.5, 118)
for t, p in zip(FW, ['A5', 'D6', 'F#5', 'B5', 'D6']):
    harp.add(t, p, 1.0, 82)
for i, p in enumerate(['D3', 'A3', 'E4', 'F#4', 'B4', 'D5']):
    harp.add(8.15 + i * 0.09, p, 1.8, 52)

glock = Part('glock', 'Glockenspiel', level=-24, pan=0.3, send=0.45, align=T_HIT)
glock.add(0.95, 'A6', 1.0, 34).add(1.95, 'E6', 1.0, 30)
glock.add(T_HIT, ['F#6', 'A6'], 1.5, 110)
for t, p in zip(FW, ['F#6', 'A6', 'B6', 'E6', 'D6']):
    glock.add(t, p, 1.0, 96)
glock.add(7.75, 'A6', 1.0, 96)

bells = Part('bells', 'TubularBells', level=-21, pan=0.2, send=0.5, align=T_HIT)
bells.add(T_HIT, ['A4', 'D5'], 4.0, 112)

perc = Part('perc', 'perc', level=-20, pan=0.05, send=0.45, align=T_HIT)
perc.add(2.28, PERC['tree2'], 2.0, 100)                       # the star appears
perc.add(T_HIT - 3.81, PERC['swell_m'], 4.2, 110)             # cymbal roll peaks at the hit
perc.add(T_HIT, PERC['crash'], 3.0, 124).add(T_HIT, PERC['bd'], 2.0, 120).add(T_HIT, PERC['tri6'], 1.0, 110)
perc.add(5.55, PERC['tri6'], 1.0, 90).add(6.55, PERC['tri3'], 1.0, 90).add(7.75, PERC['tri6m'], 1.0, 90)
perc.add(6.10, PERC['tree3'], 1.5, 80).add(7.20, PERC['cym'], 2.0, 40).add(5.55, PERC['cym'], 1.5, 36)

timp = Part('timpani', 'Timpani', level=-17, pan=-0.1, send=0.35, align=T_HIT)
timp.add(T_HIT, 'D2', 2.0, 127).add(6.10, 'A2', 1.5, 52).add(7.20, 'D2', 1.5, 46)
troll = Part('timp_roll', 'TimpaniRolls', level=-21, pan=-0.1, send=0.35,
             env=[(4.25, -24), (5.25, 0), (5.32, -60)])
troll.add(4.25, 'A2', 1.08, 100)

# strings
vln_trem = Part('vln_trem', 'ViolinEnsTrem', level=-27, pan=-0.35, send=0.5,
                env=[(0, -14), (1.2, -6), (2.3, -6), (2.9, -30)])
vln_trem.add(0.0, ['F#5', 'C#6'], 2.9, 40)
vln = Part('violins', 'ViolinEnsSusVib', level=-19, pan=-0.35, send=0.4, align=T_HIT,
           env=[(2.3, -10), (5.25, 0), (6.0, -1), (8.0, -8), (9.6, -30)])
for t, p, d, v in [(2.30, 'B4', .55, 55), (2.80, 'D5', .55, 60), (3.30, 'F#5', .55, 66), (3.80, 'A5', .55, 72),
                   (4.30, 'B5', .40, 80), (4.65, 'C#6', .40, 88), (5.00, 'E6', .34, 96)]:
    vln.add(t, p, d, v)
vln.add(T_HIT, ['A5', 'D6'], 4.0, 112)
vla = Part('violas', 'ViolaEnsSusVib', level=-21, pan=0.15, send=0.4, align=T_HIT,
           env=[(0, -8), (2.3, -6), (5.25, 0), (6.0, -1), (8.0, -8), (9.6, -30)])
vla.add(0.0, ['B3', 'D4'], 2.75, 45)
vla.add(2.3, ['G4', 'B4'], 1.05, 55).add(3.3, ['F#4', 'A4'], 1.05, 62).add(4.3, ['E4', 'A4'], 0.55, 72).add(4.8, ['E4', 'G4'], 0.55, 85)
vla.add(T_HIT, ['F#4', 'A4', 'D5'], 4.0, 110)
vc = Part('cellos', 'CelloEnsSusVib', level=-20, pan=0.3, send=0.35, align=T_HIT,
          env=[(0, -8), (2.3, -5), (5.25, 0), (6.0, -1), (8.0, -8), (9.6, -30)])
vc.add(0.0, 'G2', 2.75, 45).add(2.3, 'E3', 1.05, 55).add(3.3, 'D3', 1.05, 62).add(4.3, 'A2', 1.05, 75)
vc.add(T_HIT, ['D3', 'A3'], 4.0, 112)
cb = Part('basses', 'ContrabassSusVB', level=-22, pan=0.4, send=0.3, align=T_HIT,
          env=[(0, -8), (2.3, -5), (5.25, 0), (6.0, -1), (8.0, -8), (9.6, -30)])
cb.add(0.0, 'G1', 2.75, 40).add(2.3, 'E2', 1.05, 50).add(3.3, 'B1', 1.05, 58).add(4.3, 'A1', 1.05, 72)
cb.add(T_HIT, 'D2', 4.0, 112)

# winds
fl = Part('flute', 'FluteSusVib', level=-23, pan=-0.1, send=0.4, align=T_HIT, env=[(5.3, 0), (6.5, -4), (7.8, -14)])
for i, p in enumerate(['A5', 'B5', 'C#6', 'D6', 'E6', 'F#6', 'G6']):
    fl.add(4.80 + i * 0.07, p, 0.09, 70 + i * 6)
fl.add(T_HIT, 'A6', 2.0, 110)
cl = Part('clarinet', 'ClarinetSus', level=-27, pan=0.15, send=0.4,
          env=[(0, -10), (1.0, -4), (2.3, -6), (5.3, 0), (7.5, -12)])
cl.add(0.2, 'D4', 2.5, 40).add(T_HIT, 'F#5', 2.0, 100)
ob = Part('oboe', 'OboeSusVib', level=-26, pan=0.05, send=0.4, align=T_HIT, env=[(5.3, 0), (7.5, -12)])
ob.add(T_HIT, 'A5', 2.0, 100)
bsn = Part('bassoon', 'BassoonSus', level=-27, pan=0.25, send=0.35, align=T_HIT, env=[(5.3, 0), (7.5, -12)])
bsn.add(T_HIT, 'D3', 2.0, 100)

# brass
hn = Part('horns', 'FHornSus', level=-18, pan=-0.15, send=0.45, align=T_HIT,
          env=[(4.3, -8), (5.25, 0), (6.2, -2), (8.0, -10), (9.4, -30)])
hn.add(4.30, ['A3', 'E4'], 0.55, 70).add(4.80, ['C#4', 'G4'], 0.55, 88)
hn.add(T_HIT, ['D4', 'F#4', 'A4', 'D5'], 3.6, 118)
tpt = Part('trumpets', 'TrumpetSus', level=-19, pan=0.2, send=0.45, align=T_HIT, env=[(5.3, 0), (6.4, -6), (7.6, -20)])
tpt.add(T_HIT, ['A4', 'D5', 'F#5'], 2.0, 112)
tbn = Part('trombones', 'TromboneSus', level=-20, pan=0.35, send=0.4, align=T_HIT, env=[(5.3, 0), (6.6, -6), (8.0, -20)])
tbn.add(T_HIT, ['D3', 'A3', 'D4'], 2.4, 110)
tba = Part('tuba', 'TubaSus', level=-22, pan=0.4, send=0.35, align=T_HIT, env=[(5.3, 0), (6.6, -6), (8.0, -20)])
tba.add(T_HIT, 'D2', 2.4, 108)

PARTS = [cel, harp, glock, bells, perc, timp, troll, vln_trem, vln, vla, vc, cb, fl, cl, ob, bsn, hn, tpt, tbn, tba]

if __name__ == '__main__':
    out = sys.argv[1]
    y, rep = build('TAGS_ident', PARTS, LEN, os.path.join(out, 'build'), reverb=(72, 40, 100, 100, 25, 0), wet=0.38,
                   fade=(8.4, 10.05))
    wav, ogg = export(y, out, 'TAGS_ident')
    save_score(PARTS, os.path.join(out, 'TAGS_ident.mid'))
    y = decode(ogg)                         # measure on the delivered file
    rep['length_samples'] = len(y)
    rep['ogg_peak_dbfs'] = round(ogg_peak_db(ogg), 2)
    rep['accents'] = {str(t): round(spectral_flux_onset(y, t), 4) for t in [T_HIT] + FW}
    json.dump(rep, open(os.path.join(out, 'TAGS_ident_report.json'), 'w'), indent=1)
    print(json.dumps(rep, indent=1))
