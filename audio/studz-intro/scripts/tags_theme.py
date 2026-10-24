"""TAGS_theme - the long version of the TAGS ident, 30.0 s, D-flat major /
B-flat minor, 100 bpm (one bar = 2.4 s). The magical castle opening grows
into a dark, driving hybrid-orchestral theme in the spirit of the
Transformers-era Paramount intro (original music): pounding drums, galloping
spiccato strings, brass braams, anvil and brake-drum clangs.

bars 0-1   0.0-4.8    the magical opening (celesta, harp, flute phrase, soft strings)
bars 2-3   4.8-9.6    the beat kicks in: drums, galloping cellos/basses, violins sing the theme
bars 4-5   9.6-14.4   build: horns take the theme, braams swell, drums double, snare roll, riser;
                      a split-second of silence before the drop
bars 6-9   14.4-24.0  DROP: full brass + violins play the theme fortissimo over
                      Bbm - Gb - Db - Ab, big drums, anvils, spiccato ostinato
bar 10     24.0-26.4  fill: brass stabs, snare and timpani run-up
26.4       final hit on D-flat major (gong, bells), then the opening melody returns
           on celesta and it fades to silence by 30.0 s."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orch import Part, PERC, build, export, save_score, accent_time, decode, ogg_peak_db, n

LEN = 30.0
BAR = 2.4
DROP, FINAL = 14.4, 26.4
CUT = [(14.15, 0), (14.2, -60), (14.37, -60), (14.38, 0)]     # the breath before the drop
# beat/ostinato section gains: verse kicks in, build held back and growing, the drop on top
SECT = [(0, 0), (4.75, 7), (9.55, 7), (9.6, -7), (14.1, -1), (14.15, -1), (14.2, -60), (14.37, -60), (14.38, 4), (24.0, 4), (24.1, 1)]


def B(k):
    return k * BAR


def s16(k, i):
    """Time of 16th-note step i (0-15) in bar k."""
    return B(k) + i * BAR / 16


DB = [1, 3, 5, 6, 8, 10, 0]


def db_scale(lo, hi):
    return [p for p in range(n(lo), n(hi) + 1) if p % 12 in DB]


# chord per bar: (root, third, fifth) as note-name stems
CHORD = {2: ('Bb', 'Db', 'F'), 3: ('Gb', 'Bb', 'Db'), 4: ('Db', 'F', 'Ab'), 5: ('Ab', 'C', 'Eb'),
         6: ('Bb', 'Db', 'F'), 7: ('Gb', 'Bb', 'Db'), 8: ('Db', 'F', 'Ab'), 9: ('Ab', 'C', 'Eb')}
GALLOP = [0, 3, 6, 8, 11, 14]                                     # accent steps of the ostinato

# =============================== the opening (as in the logo version)
cel = Part('celesta', ('gm', 8), level=-21, pan=-0.3, send=0.5, env=[(0, 4), (4.8, 4), (5.4, -4), (26.0, -4), (26.4, 2)])
tw = ['Ab6', 'Db7', 'F7', 'C7', 'Eb7', 'Bb6', 'Db7', 'F7', 'Bb6', 'Db7', 'F7', 'C7', 'Gb7', 'F7', 'Db7', 'Bb6']
for i, p in enumerate(tw):
    cel.add(0.12 + i * 0.3, p, 0.5, 52 + (i % 3) * 6)
for k in range(6, 10):                                           # sparkle on the drop's downbeats
    cel.add(B(k), [CHORD[k][0] + '6', CHORD[k][2] + '6'], 0.8, 88)
cel.add(FINAL, ['Db6', 'F6', 'Ab6'], 1.4, 104)
for t, p in [(27.40, 'Ab6'), (27.85, 'Eb7'), (28.35, 'F7'), (28.60, 'Eb7'), (28.85, 'Db7')]:   # the opening melody returns
    cel.add(t, p, 0.9, 74)

harp = Part('harp', 'Harp', level=-17, pan=-0.55, send=0.45, split=True)
for i, p in enumerate(['Db2', 'Ab2', 'F3', 'C4', 'Eb4', 'Ab4']):
    harp.add(0.00 + i * 0.07, p, 2.0, 62 + i * 2)
for i, p in enumerate(['Gb2', 'Db3', 'Bb3', 'F4', 'C5']):
    harp.add(2.40 + i * 0.07, p, 2.0, 60 + i * 2)
for i, p in enumerate(db_scale('Db3', 'Db6')):                    # sweep into the beat
    harp.add(4.05 + i * 0.033, p, 0.5, 60 + i * 2)
for i, p in enumerate(db_scale('Ab3', 'Ab6')):                    # sweep into the drop
    harp.add(13.35 + i * 0.037, p, 0.5, 72 + i * 2)
harp.add(FINAL, ['Db2', 'Ab2', 'Db3', 'F3', 'Ab3', 'Db4'], 3.0, 124)
for i, p in enumerate(['Db3', 'Ab3', 'Eb4', 'F4', 'Ab4', 'C5', 'Db5', 'F5']):
    harp.add(27.2 + i * 0.13, p, 1.6, 58)

fl = Part('flute', 'FluteSusVib', level=-19, pan=-0.1, send=0.45, env=[(0.5, 2), (4.6, 3), (4.9, -6), (13.5, 0)] + CUT)
for t, p, d in [(0.60, 'Ab4', .5), (1.20, 'Eb5', .55), (1.80, 'F5', .28), (2.10, 'Eb5', .28), (2.40, 'Db5', .8),
                (3.30, 'Bb4', .42), (3.75, 'F5', .48), (4.25, 'Gb5', .24), (4.50, 'F5', .3)]:
    fl.add(t, p, d, 78)
for i, p in enumerate(db_scale('Ab5', 'C7')):                     # run into the drop
    fl.add(13.70 + i * 0.044, p, 0.06, 80 + i * 4)
fl.add(DROP, 'F6', 1.0, 110).add(FINAL, 'Db6', 2.5, 110)

vsoft = Part('violins_soft', 'ViolinEnsSusVib-Quiet', level=-20, pan=-0.3, send=0.5, env=[(0, -8), (0.8, 0), (4.6, -1), (5.2, -40)])
vsoft.add(0.0, ['F5', 'C6'], 2.45, 44).add(2.4, ['F5', 'Bb5', 'C6'], 2.6, 46)
vtrem = Part('vln_trem', 'ViolinEnsTrem', level=-25, pan=-0.4, send=0.55,
             env=[(0, -10), (1.0, -4), (4.6, -4), (5.0, -40), (11.9, -40), (12.0, -18), (14.15, 0)] + CUT[1:])
vtrem.add(0.0, 'Db6', 5.0, 36).add(12.0, 'Eb5', 2.2, 100)

# =============================== the beat
drums = Part('drums', 'perc', level=-14, pan=0.0, send=0.25, align=B(2), env=SECT)
shaker = Part('shaker', 'perc', level=-28, pan=0.35, send=0.2, align=B(2), env=SECT)
snare = Part('snare', 'perc', level=-17, pan=-0.05, send=0.3, align=B(2) + 0.6, env=SECT)
metal = Part('metal', 'perc', level=-18, pan=0.2, send=0.4, split=True, env=SECT[:1] + SECT[3:])
timp = Part('timpani', 'Timpani', level=-15, pan=-0.15, send=0.3, split=True, env=SECT)

timp.add(4.20, 'Db2', 0.4, 70).add(4.50, 'Db2', 0.4, 84)          # pick-up into the beat
for k in (2, 3):                                                 # verse: steady heartbeat
    for i, v in zip([0, 6, 8], [100, 82, 94]):
        drums.add(s16(k, i), PERC['bdd'], 0.3, v)
    for i in (4, 12):
        snare.add(s16(k, i), PERC['snare'], 0.4, 70 if k == 2 else 84)
    for i in range(0, 16, 2):
        shaker.add(s16(k, i), PERC['shaker'], 0.2, 70)
    timp.add(B(k), CHORD[k][0] + '2', 0.6, 96)
for k in (4, 5):                                                 # build
    for i in ([0, 6, 8, 14] if k == 4 else range(0, 16, 2)):
        if k == 5 and s16(k, i) >= 14.15:
            continue
        drums.add(s16(k, i), PERC['bdd'], 0.3, 100 if k == 4 else 80 + i * 3)
    for i in range(0, 16, 2):
        shaker.add(s16(k, i), PERC['shaker'], 0.2, 76)
    if k == 4:
        snare.add(s16(k, 4), PERC['snare'], 0.4, 96).add(s16(k, 12), PERC['snare'], 0.4, 96)
    else:
        for i in range(0, 15):                                   # 16th snare roll, growing
            snare.add(s16(k, i), PERC['snare'], 0.12, 50 + i * 5)
    for i in (0, 8, 10, 14) if k == 4 else (0, 6, 8):
        timp.add(s16(k, i), (CHORD[k][0] if i in (0, 8) else CHORD[k][2]) + '2', 0.5, 100)
DROP_BD = [0, 3, 6, 8, 10, 11, 14]
for k in range(6, 10):                                           # the drop: big pattern
    drums.add(B(k), PERC['bd'], 2.0, 127)
    for i in DROP_BD:
        drums.add(s16(k, i), PERC['bdd'], 0.3, 124 if i in (0, 8) else 104)
    for i in (4, 12):
        snare.add(s16(k, i), PERC['snare'], 0.4, 124)
        metal.add(s16(k, i), PERC['brake'], 0.4, 84)
    if k in (7, 9):
        snare.add(s16(k, 15), PERC['snare'], 0.2, 80)
    for i in range(16):
        shaker.add(s16(k, i), PERC['shaker'], 0.15, 86 if i % 4 == 0 else 66)
    for i, which in zip([0, 6, 8, 11, 14], [0, 2, 0, 2, 0]):
        timp.add(s16(k, i), CHORD[k][which] + '2', 0.5, 112 if i in (0, 8) else 98)
    for i in {6: [0], 7: [8], 8: [0], 9: [8, 12]}[k]:
        metal.add(s16(k, i), PERC['anvil'], 1.0, 112)
metal.add(DROP, PERC['crash'], 3.0, 127).add(B(8), PERC['crash'], 3.0, 118).add(B(10), PERC['crash'], 2.0, 110)
for i in range(16):                                              # fill bar
    snare.add(s16(10, i), PERC['snare'], 0.12, 64 + i * 2)
    if i % 2 == 0:
        drums.add(s16(10, i), PERC['bdd'], 0.3, 88 + i)
for t, p in [(25.80, 'Ab2'), (26.00, 'F2'), (26.20, 'Db2')]:
    timp.add(t, p, 0.4, 100)
drums.add(FINAL, PERC['bd'], 3.0, 127)
timp.add(FINAL, ['Db2', 'Ab2'], 2.5, 127)
metal.add(FINAL, PERC['crash'], 3.0, 127).add(FINAL, PERC['gong'], 4.0, 120).add(FINAL, PERC['anvil'], 1.0, 100)
swell = Part('cym_swell', 'perc', level=-22, pan=0.1, send=0.5, thresh=0.001)   # rolls: no attack shift
swell.add(4.80 - 1.53, PERC['swell_s'], 1.8, 100).add(DROP - 3.81, PERC['swell_m'], 3.9, 120).add(FINAL - 1.53, PERC['swell_s'], 1.6, 110)
troll = Part('timp_roll', 'TimpaniRolls', level=-18, pan=-0.15, send=0.35, env=[(12.0, -20)] + CUT + [(14.4, -60)])
troll.add(12.0, 'Ab2', 2.2, 100)
bells = Part('bells', 'TubularBells', level=-21, pan=0.2, send=0.5, split=True)
bells.add(DROP, ['F4', 'Bb4'], 3.0, 110).add(B(8), ['Ab4', 'Db5'], 3.0, 110).add(FINAL, ['Ab4', 'Db5'], 4.0, 120)

# =============================== strings
THEME_A = [(0.0, 'F5', .9), (0.9, 'Db5', .3), (1.2, 'Eb5', .6), (1.8, 'F5', .6)]           # over Bbm
THEME_B = [(0.0, 'Gb5', .9), (0.9, 'F5', .3), (1.2, 'Eb5', .6), (1.8, 'Db5', .6)]          # over Gb
THEME_C = [(0.0, 'Ab5', .9), (0.9, 'Gb5', .3), (1.2, 'F5', .6), (1.8, 'Eb5', .6)]          # over Db
THEME_D = [(0.0, 'Eb5', 1.2), (1.2, 'F5', .6), (1.8, 'C6', .6)]                           # over Ab
THEME = {2: THEME_A, 3: THEME_B, 6: THEME_A, 7: THEME_B, 8: THEME_C, 9: THEME_D}

vln = Part('violins', 'ViolinEnsSusVib', level=-14, pan=-0.35, send=0.4, align=DROP,
           env=[(4.8, -5), (9.4, -4), (9.6, -40), (13.9, -40), (14.38, 0), (24.0, 0)])
for k in (2, 3, 6, 7, 8, 9):
    for t, p, d in THEME[k]:
        vln.add(B(k) + t, p, d + 0.03, 84 if k < 6 else 118)
vln.add(FINAL, ['F5', 'Ab5', 'Db6'], 2.4, 122)
vrun = Part('violins_run', 'ViolinEnsSpic', level=-17, pan=-0.3, send=0.4, align=DROP)
for i, p in enumerate(db_scale('Ab4', 'Db6')):                   # run-up in the fill bar
    vrun.add(25.2 + i * 0.105, p, 0.1, 90 + i * 3)
for k in range(6, 10):                                           # high spiccato ostinato in the drop
    r, t3, f = CHORD[k]
    for i in range(16):
        vrun.add(s16(k, i), (f + '5') if i % 2 == 0 else (t3 + '5'), 0.1, 92 if i in GALLOP else 70)
vla = Part('violas', 'ViolaEnsSpic', level=-18, pan=0.15, send=0.35, align=DROP, env=SECT)
for k in range(4, 11):
    if k == 10:
        r, t3, f = ('Gb', 'Bb', 'Db')
    else:
        r, t3, f = CHORD[k]
    for i in range(16):
        if s16(k, i) >= 14.15 and k == 5:
            continue
        vla.add(s16(k, i), (t3 + '4') if i % 2 == 0 else (f + '4'), 0.1, (96 if i in GALLOP else 72) + (10 if k >= 6 else 0))
vc = Part('cellos', 'CelloEnsSpic', level=-15, pan=0.3, send=0.3, align=DROP, env=SECT)
cb = Part('basses', 'ContrabassSpic', level=-16, pan=0.4, send=0.25, align=DROP, env=SECT)
for k in range(2, 11):
    root = CHORD.get(k, ('Gb',))[0]
    for i in range(16):
        t = s16(k, i)
        if k == 5 and t >= 14.15:
            continue
        if k == 10:
            root = 'Gb' if i < 8 else 'Ab'
        big = k >= 6
        vc.add(t, root + ('2' if i % 4 != 2 else '3'), 0.1, (110 if i in GALLOP else 78) + (12 if big else 0) - (20 if k < 4 else 0))
        if i in GALLOP:
            cb.add(t, root + '1', 0.12, (108 if big else 90) - (16 if k < 4 else 0))
vc_sus = Part('cellos_sus', 'CelloEnsSusVib', level=-17, pan=0.3, send=0.35, align=FINAL, env=[(0, -8), (4.8, -40), (FINAL - 0.1, -40), (FINAL, 0), (28.0, -4), (29.6, -30)])
vc_sus.add(0.0, 'Db3', 4.9, 50).add(FINAL, ['Db2', 'Ab2', 'Db3'], 3.0, 124)
cb_sus = Part('basses_sus', 'ContrabassSusVB', level=-18, pan=0.4, send=0.3, align=FINAL, env=[(0, -8), (4.8, -40), (FINAL - 0.1, -40), (FINAL, 0), (28.0, -4), (29.6, -30)])
cb_sus.add(0.0, 'Db2', 4.9, 46).add(FINAL, 'Db1', 3.0, 124)

# =============================== brass
hn = Part('horns', 'FHornSus', level=-13, pan=-0.15, send=0.45, align=DROP,
          env=[(4.8, -14), (9.6, -13), (13.6, -7)] + CUT + [(14.38, 0), (24.0, 0), (26.3, 0), (26.38, 3), (27.2, 2), (28.2, -6), (29.6, -30)])
for k in (2, 3):                                                 # soft chord pad under the verse
    r, t3, f = CHORD[k]
    hn.add(B(k), [t3 + '3', f + '3'], 2.4, 70)
for t, p, d, v in [(9.6, 'Ab4', .9, 90), (10.5, 'Bb4', .3, 92), (10.8, 'C5', .6, 96), (11.4, 'Db5', .6, 100),
                   (12.0, 'Eb5', 1.2, 108), (13.2, 'Db5', .3, 110), (13.5, 'C5', .3, 112), (13.8, 'Eb5', .35, 116)]:
    hn.add(t, p, d, v)
for k in (6, 7, 8, 9):                                           # the theme an octave down
    for t, p, d in THEME[k]:
        hn.add(B(k) + t, n(p) - 12, d + 0.03, 120)
hn.add(FINAL, ['Db3', 'Ab3', 'Db4', 'F4'], 3.0, 126)
tpt = Part('trumpets', 'TrumpetSus', level=-12, pan=0.2, send=0.45, align=DROP, env=[(DROP, 0), (26.3, 0), (26.38, 3), (27.0, 2), (27.6, -6), (29.2, -30)])
for k in (6, 7, 8, 9):
    for t, p, d in THEME[k]:
        tpt.add(B(k) + t, p, d + 0.03, 124)
tpt.add(FINAL, ['Ab4', 'Db5', 'F5'], 2.6, 127)
tbn = Part('trombones', 'TromboneSus', level=-13, pan=0.35, send=0.4, align=DROP,
           env=[(12.0, -20), (14.1, -8)] + CUT + [(14.38, 0), (26.3, 0), (26.38, 3), (27.2, 2), (28.0, -6), (29.6, -30)])
tbn.add(12.0, ['Ab2', 'Eb3'], 2.2, 110)                           # braam swell into the drop
for k in (6, 7, 8, 9):
    r, t3, f = CHORD[k]
    tbn.add(B(k), [r + '2', f + ('3' if f in ('Db', 'Eb') else '2')], 2.35, 124)
tbn.add(FINAL, ['Db2', 'Ab2', 'F3'], 3.0, 127)
tba = Part('tuba', 'TubaSus', level=-16, pan=0.4, send=0.3, align=DROP, env=[(12.0, -20), (14.1, -8)] + CUT + [(14.38, 0), (26.3, 0), (26.38, 3), (27.2, 2), (28.0, -6), (29.6, -30)])
tba.add(12.0, 'Ab1', 2.2, 110)
for k in (6, 7, 8, 9):
    tba.add(B(k), CHORD[k][0] + ('2' if CHORD[k][0] == 'Db' else '1'), 2.35, 124)
tba.add(FINAL, 'Db2', 3.0, 127)
stabs = [(s16(10, i), i) for i in (0, 3, 6, 8, 11, 14)]
tpt_st = Part('trumpet_stac', 'TrumpetStac', level=-14, pan=0.2, send=0.4, align=24.0)
tbn_st = Part('trombone_stac', 'TromboneStac', level=-14, pan=0.35, send=0.35, align=24.0)
for t, i in stabs:
    gb = i < 8
    tpt_st.add(t, ['Bb4', 'Db5'] if gb else ['C5', 'Eb5'], 0.15, 110 + i)
    tbn_st.add(t, ['Gb2', 'Db3'] if gb else ['Ab2', 'Eb3'], 0.18, 110 + i)

PARTS = [cel, harp, fl, vsoft, vtrem, drums, shaker, snare, metal, timp, swell, troll, bells,
         vln, vrun, vla, vc, cb, vc_sus, cb_sus, hn, tpt, tbn, tba, tpt_st, tbn_st]
ACCENTS = [4.8, DROP, B(8), 24.0, FINAL]

if __name__ == '__main__':
    out = sys.argv[1]
    y, rep = build('TAGS_theme', PARTS, LEN, os.path.join(out, 'build'), reverb=(70, 40, 100, 100, 25, 0), wet=0.3,
                   fade=(28.6, 29.95))
    wav, ogg = export(y, out, 'TAGS_theme')
    save_score(PARTS, os.path.join(out, 'TAGS_theme.mid'))
    y = decode(ogg)
    rep['length_samples'] = len(y)
    rep['ogg_peak_dbfs'] = round(ogg_peak_db(ogg), 2)
    rep['accents'] = {str(round(t, 2)): round(accent_time(y, t), 4) for t in ACCENTS}
    json.dump(rep, open(os.path.join(out, 'TAGS_theme_report.json'), 'w'), indent=1)
    print(json.dumps(rep['accents']))
