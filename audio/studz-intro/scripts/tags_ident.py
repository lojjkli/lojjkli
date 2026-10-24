"""TAGS_ident - studio logo, exactly 10.1 s, D-flat major.
In the spirit of a classic animation-studio castle intro (an original melody,
not a quotation): string-led, lyrical and magical.
0-2.3   night sky over the water: celesta and harp twinkle, a soft string pad
        (Dbmaj9 -> Gbmaj7#11/Db), solo flute sings the first phrase
2.3-5.3 the shooting star draws its arc: the violins take the melody higher,
        Ebm9 -> Gbmaj7 -> Amaj7 (the "magic" lift) -> Ab9sus4 -> Ab7, the harp
        glissando rises with the star, horns sing a warm counter-line, flutes
        run up, timpani roll and cymbal swell
5.3     the castle lights up: full orchestra on D-flat major with bells,
        glockenspiel, bell tree, crash and timpani; the violin melody peaks
5.55 6.1 6.55 7.2 7.75  fireworks: sparkles (glockenspiel, celesta, harp,
        triangle, piccolo) while the strings sing the cadence
        Db -> Bbm7 -> Gbmaj7 -> Gbm6 (the wistful minor iv) -> Db
then it rings out and fades to silence by 10.1 s."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orch import Part, PERC, build, export, save_score, accent_time, decode, ogg_peak_db, n

T_HIT = 5.3
FW = [5.55, 6.10, 6.55, 7.20, 7.75]
LEN = 10.1
DB = [1, 3, 5, 6, 8, 10, 0]                                  # D-flat major pitch classes


def db_scale(lo, hi):
    return [p for p in range(n(lo), n(hi) + 1) if p % 12 in DB]


RING = [(T_HIT, 0), (7.6, -3), (7.8, -2), (8.8, -9), (9.9, -40)]

# ---- the melody
PHRASE1 = [(0.60, 'Ab4', .40), (1.00, 'Eb5', .50), (1.50, 'F5', .28), (1.78, 'Eb5', .28), (2.06, 'Db5', .50)]
PHRASE2 = [(2.30, 'Bb4', .42), (2.72, 'F5', .50), (3.22, 'Gb5', .30), (3.52, 'F5', .30), (3.82, 'Eb5', .36),
           (4.18, 'Ab5', .30), (4.48, 'Bb5', .30), (4.78, 'C6', .50)]
CADENCE = [(T_HIT, 'Db6', .80), (6.10, 'C6', .45), (6.55, 'Ab5', .65), (7.20, 'A5', .55), (7.75, 'Ab5', 1.8)]

fl = Part('flute', 'FluteSusVib', level=-19, pan=-0.1, send=0.45, env=[(0.5, -3), (2.0, 0), (2.4, -4), (4.9, 0)] + RING)
for t, p, d in PHRASE1:
    fl.add(t, p, d, 78)
for i, p in enumerate(db_scale('Ab5', 'C7')):                 # run up into the hit
    fl.add(4.92 + i * 0.046, p, 0.06, 80 + i * 4)
fl.add(T_HIT, 'Db6', 2.0, 112)
picc = Part('piccolo', 'PiccoloSus', level=-26, pan=-0.05, send=0.5, split=True)
for t, p in zip(FW, ['F6', 'Eb6', 'Db6', 'C6', 'F6']):
    picc.add(t, p, 0.25, 100)

vln = Part('violins', 'ViolinEnsSusVib', level=-15, pan=-0.35, send=0.45, align=T_HIT,
           env=[(2.2, -6), (3.9, -2), (4.8, 0)] + RING)
for i, (t, p, d) in enumerate(PHRASE2):
    vln.add(t, p, d + 0.04, 72 + i * 5)
for t, p, d in CADENCE:
    vln.add(t, p, d + 0.04, 120 if t == T_HIT else 104)
vln2 = Part('violins2', 'ViolinEnsSusVib', level=-19, pan=-0.2, send=0.45, align=T_HIT, env=[(2.2, -8), (4.8, 0)] + RING)
for t, p, d in [(2.30, 'Gb4', .9), (3.22, 'Db5', .72), (3.95, 'C#5', .45), (4.40, 'Eb5', .35), (4.78, 'Eb5', .5)]:
    vln2.add(t, p, d, 78)
for t, p, d in [(T_HIT, 'Ab5', .8), (6.10, 'F5', .45), (6.55, 'F5', .65), (7.20, 'Gb5', .55), (7.75, 'F5', 1.8)]:
    vln2.add(t, p, d, 116 if t == T_HIT else 98)
vsoft = Part('violins_soft', 'ViolinEnsSusVib-Quiet', level=-24, pan=-0.3, send=0.5, env=[(0, -8), (0.8, 0), (2.3, -2), (2.7, -40)])
vsoft.add(0.0, ['F5', 'C6'], 1.05, 44).add(1.0, ['F5', 'Bb5', 'C6'], 1.7, 46)
vtrem = Part('vln_trem', 'ViolinEnsTrem', level=-29, pan=-0.4, send=0.55, env=[(0, -10), (1.0, -4), (2.2, -4), (2.7, -40)])
vtrem.add(0.0, 'Db6', 2.7, 36)
vla = Part('violas', 'ViolaEnsSusVib', level=-19, pan=0.15, send=0.4, align=T_HIT, env=[(0, -8), (2.3, -5), (4.8, 0)] + RING)
for t, ps, d, v in [(0.0, ['Ab3', 'Eb4'], 1.05, 46), (1.0, ['Bb3', 'Db4'], 1.35, 48), (2.30, ['Gb3', 'Db4'], .95, 60),
                    (3.22, ['Bb3', 'Db4'], .76, 66), (3.95, ['C#4', 'E4'], .48, 72), (4.40, ['Db4', 'Eb4'], .38, 78),
                    (4.78, ['C4', 'Gb4'], .55, 86), (T_HIT, ['Db4', 'F4', 'Ab4'], .82, 118), (6.10, ['Db4', 'F4'], .47, 98),
                    (6.55, ['Db4', 'Bb4'], .67, 98), (7.20, ['Db4', 'Eb4'], .57, 98), (7.75, ['Db4', 'Ab4'], 1.9, 100)]:
    vla.add(t, ps, d, v)
vc = Part('cellos', 'CelloEnsSusVib', level=-17, pan=0.3, send=0.35, align=T_HIT, env=[(0, -8), (2.3, -4), (4.8, 0)] + RING)
for t, ps, d, v in [(0.0, 'Db3', 2.35, 50), (2.30, 'Eb3', .95, 62), (3.22, 'Gb2', .76, 68), (3.95, 'A2', .48, 74),
                    (4.40, 'Ab2', .9, 82), (T_HIT, ['Db3', 'Ab3'], .82, 120), (6.10, 'Bb2', .47, 100),
                    (6.55, 'Gb2', .67, 100), (7.20, 'Gb2', .57, 100), (7.75, ['Db3', 'Ab3'], 1.9, 104)]:
    vc.add(t, ps, d, v)
cb = Part('basses', 'ContrabassSusVB', level=-19, pan=0.4, send=0.3, align=T_HIT, env=[(0, -8), (2.3, -4), (4.8, 0)] + RING)
for t, p, d, v in [(0.0, 'Db2', 2.35, 46), (2.30, 'Eb2', .95, 58), (3.22, 'Gb1', .76, 64), (3.95, 'A1', .48, 70),
                   (4.40, 'Ab1', .9, 80), (T_HIT, 'Db2', .82, 120), (6.10, 'Bb1', .47, 100), (6.55, 'Gb1', .67, 100),
                   (7.20, 'Gb1', .57, 100), (7.75, 'Db2', 1.9, 104)]:
    cb.add(t, p, d, v)

cl = Part('clarinet', 'ClarinetSus', level=-24, pan=0.15, send=0.4, align=T_HIT, env=[(2.3, -4)] + RING)
cl.add(2.30, 'Db5', .9, 66).add(3.22, 'Bb4', .72, 70).add(3.95, 'C#5', .45, 74).add(4.40, 'Bb4', .35, 78).add(4.78, 'C5', .5, 84)
cl.add(T_HIT, 'F5', 2.3, 110).add(7.75, 'F5', 1.8, 96)
ob = Part('oboe', 'OboeSusVib', level=-25, pan=0.05, send=0.4, align=T_HIT, env=RING)
ob.add(T_HIT, 'Ab5', 2.3, 108).add(7.75, 'Ab5', 1.8, 94)

# ---- brass: warm, never blaring
hn = Part('horns', 'FHornSus', level=-17, pan=-0.15, send=0.5, align=T_HIT, env=[(3.2, -6), (4.8, 0)] + RING)
for t, p, d, v in [(3.22, 'Db4', .74, 80), (3.95, 'C#4', .46, 84), (4.40, 'Db4', .36, 90), (4.78, 'C4', .5, 98)]:
    hn.add(t, p, d, v)
hn.add(T_HIT, ['Db3', 'Ab3', 'Db4', 'F4'], 2.3, 118).add(7.75, ['Db3', 'Ab3', 'F4'], 1.9, 104)
tpt = Part('trumpets', 'TrumpetSus', level=-20, pan=0.2, send=0.5, align=T_HIT, env=[(T_HIT, 0), (6.0, -8), (7.6, -10), (7.8, -6), (8.8, -16)])
tpt.add(T_HIT, ['Ab4', 'Db5', 'F5'], 1.6, 114).add(7.75, ['Ab4', 'Db5'], 1.4, 98)
tbn = Part('trombones', 'TromboneSus', level=-21, pan=0.35, send=0.45, align=T_HIT, env=[(T_HIT, 0), (6.0, -6)] + RING[1:])
tbn.add(T_HIT, ['Db2', 'Ab2', 'F3'], 2.2, 112).add(7.75, ['Db2', 'Ab2'], 1.8, 96)
tba = Part('tuba', 'TubaSus', level=-23, pan=0.4, send=0.35, align=T_HIT, env=[(T_HIT, 0), (6.0, -6)] + RING[1:])
tba.add(T_HIT, 'Db2', 2.2, 110)

# ---- sparkle: celesta, harp, glockenspiel, bells, percussion
cel = Part('celesta', ('gm', 8), level=-21, pan=-0.3, send=0.5)
for i, t in enumerate([0.12, 0.36, 0.60, 0.84, 1.08, 1.32, 1.56, 1.80, 2.04]):
    cel.add(t, ['Ab6', 'Db7', 'F7', 'C7', 'Eb7', 'Bb6', 'Db7', 'F7', 'Ab7'][i], 0.5, 52 + (i % 3) * 6)
for t, p in [(2.65, 'Bb6'), (3.15, 'Db7'), (3.65, 'F7'), (4.10, 'G#6'), (4.55, 'Bb6'), (4.95, 'Eb7')]:
    cel.add(t, p, 0.4, 66)
cel.add(T_HIT, ['Db6', 'F6', 'Ab6'], 1.4, 104)
for t, ps in zip(FW, [['Ab6', 'Db7'], ['F6', 'C7'], ['Gb6', 'Db7'], ['A6', 'Eb7'], ['F6', 'Ab6', 'Db7']]):
    cel.add(t, ps, 0.9, 96)
for i, p in enumerate(['Db7', 'Ab6', 'F6', 'Db6']):
    cel.add(8.30 + i * 0.32, p, 0.8, 60 - i * 4)

harp = Part('harp', 'Harp', level=-17, pan=-0.55, send=0.45, split=True)
for i, p in enumerate(['Db2', 'Ab2', 'F3', 'C4', 'Eb4', 'Ab4']):
    harp.add(0.00 + i * 0.07, p, 2.0, 60 + i * 2)
for i, p in enumerate(['Gb2', 'Db3', 'Bb3', 'F4', 'C5']):
    harp.add(1.00 + i * 0.07, p, 1.6, 58 + i * 2)
star = db_scale('Db3', 'Db7')
for i, p in enumerate(star):                                  # the star's arc: accelerating glissando
    u = i / (len(star) - 1)
    harp.add(2.30 + 2.80 * u ** 0.62, p, 0.6, 50 + 56 * u)
harp.add(T_HIT, ['Db2', 'Ab2', 'Db3', 'F3', 'Ab3', 'Db4'], 2.5, 120)
for t, p in zip(FW, ['Ab5', 'C6', 'Bb5', 'A5', 'Db6']):
    harp.add(t, p, 1.0, 88)
for i, p in enumerate(['Db3', 'Ab3', 'Eb4', 'F4', 'Ab4', 'C5', 'Db5', 'F5']):
    harp.add(8.10 + i * 0.11, p, 1.6, 56)

glock = Part('glock', 'Glockenspiel', level=-22, pan=0.3, send=0.5, split=True)
glock.add(1.20, 'F6', 1.0, 36).add(T_HIT, ['F6', 'Ab6'], 1.5, 112)
for t, p in zip(FW, ['Ab6', 'C7', 'Bb6', 'A6', 'Db6']):
    glock.add(t, p, 1.0, 100)

bells = Part('bells', 'TubularBells', level=-21, pan=0.2, send=0.55, split=True)
bells.add(T_HIT, ['Ab4', 'Db5'], 4.0, 116).add(7.75, ['F5'], 3.0, 96)

perc = Part('perc', 'perc', level=-21, pan=0.05, send=0.5, split=True)
perc.add(2.28, PERC['tree2'], 2.0, 100)                                 # the star appears
perc.add(T_HIT, PERC['crash'], 3.0, 112).add(T_HIT, PERC['tree1'], 2.0, 100).add(T_HIT, PERC['tri6'], 1.0, 110)
for t, k in zip(FW, ['tri6', 'tri3', 'tri6m', 'tri3', 'tri6']):
    perc.add(t, PERC[k], 1.0, 96)
perc.add(6.10, PERC['tree3'], 1.5, 80).add(6.55, PERC['cym'], 2.0, 44).add(7.75, PERC['tree4'], 2.0, 96)
swell = Part('cym_swell', 'perc', level=-24, pan=0.1, send=0.5)
swell.add(T_HIT - 3.81, PERC['swell_m'], 4.0, 110)

timp = Part('timpani', 'Timpani', level=-18, pan=-0.1, send=0.35, split=True)
timp.add(T_HIT, ['Db2', 'Ab2'], 2.0, 124).add(7.75, 'Db2', 1.5, 80)
troll = Part('timp_roll', 'TimpaniRolls', level=-22, pan=-0.1, send=0.35, env=[(4.3, -24), (5.25, 0), (5.3, -60)])
troll.add(4.30, 'Ab2', 1.05, 100)

PARTS = [fl, picc, vln, vln2, vsoft, vtrem, vla, vc, cb, cl, ob, hn, tpt, tbn, tba, cel, harp, glock, bells, perc,
         swell, timp, troll]

if __name__ == '__main__':
    out = sys.argv[1]
    y, rep = build('TAGS_ident', PARTS, LEN, os.path.join(out, 'build'), reverb=(80, 35, 100, 100, 30, 0), wet=0.4,
                   fade=(8.7, 10.05))
    wav, ogg = export(y, out, 'TAGS_ident')
    save_score(PARTS, os.path.join(out, 'TAGS_ident.mid'))
    y = decode(ogg)                         # measure on the delivered file
    rep['length_samples'] = len(y)
    rep['ogg_peak_dbfs'] = round(ogg_peak_db(ogg), 2)
    rep['accents'] = {str(t): round(accent_time(y, t), 4) for t in [T_HIT] + FW}
    json.dump(rep, open(os.path.join(out, 'TAGS_ident_report.json'), 'w'), indent=1)
    print(json.dumps(rep['accents']))
