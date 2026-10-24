"""TAGS_theme - 13.0 s, B-flat minor -> B-flat major, 96 bpm (beat 0.625 s,
bar 2.5 s). Original music in the style of the Transformers-era Paramount
intros: robotic/metal sounds and a braam, a string pulse with choir, a driving
beat and a heroic unison-horn theme over i - VI - III - VII.

0-2.5    from silence: soft violins preview the theme over a harp arpeggio, quiet
         ratchets and metal clanks, a low braam fading in
2.5-5.0  the build: 16th string pulse, choir swell, drums doubling up, snare and
         timpani rolls, trombone braam, cymbal swell, a breath before 5.0
5.0-10.0 LOUD: horns + trombones play the theme, trumpets and violins join an octave up
         in the second bar; kick, snare + anvil backbeat, 16th shaker, timpani fills,
         crashes; Bbm - Gb | Db - Ab
10.0     final heroic hit on B-flat MAJOR (gong, crash, bells), then it gets quiet
         and rings out to silence by 13.0 s."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orch import Part, PERC, build, export, save_score, accent_time, decode, ogg_peak_db, n

LEN = 13.0
BEAT = 0.625
BAR = 2.5
LOUD, FINAL = 5.0, 10.0
BREATH = [(4.84, 0), (4.88, -60), (4.985, -60), (4.99, 0)]
OUT = [(FINAL, 0), (10.35, -5), (11.2, -13), (12.9, -45)]       # quieter again after the final hit


def b(k, beat=0.0):
    return k * BAR + beat * BEAT


def s16(k, i):
    return b(k, i / 4)


# half-bar chords: (root, third, fifth)
HALF = {(1, 0): ('Bb', 'Db', 'F'), (1, 2): ('Bb', 'Db', 'F'), (2, 0): ('Bb', 'Db', 'F'), (2, 2): ('Gb', 'Bb', 'Db'),
        (3, 0): ('Db', 'F', 'Ab'), (3, 2): ('Ab', 'C', 'Eb')}


def chord_at(k, i):
    return HALF[(k, 0 if i < 8 else 2)]


THEME = [(2, 0, 'Bb3', 1.0), (2, 1, 'F4', 2.0), (2, 3, 'Eb4', 0.5), (2, 3.5, 'Db4', 0.5),
         (3, 0, 'Ab4', 1.5), (3, 1.5, 'Gb4', 0.5), (3, 2, 'F4', 1.0), (3, 3, 'Eb4', 0.5), (3, 3.5, 'F4', 0.5)]

# ======================= 0-2.5: from silence
preview = Part('theme_preview', 'ViolinEnsSusVib-Quiet', level=-17, pan=-0.3, send=0.55,
               env=[(0.3, -14), (1.2, -4), (2.2, 0), (2.6, -6), (3.2, -40)])
for beat, p, ln in [(0.5, 'Bb4', 1.0), (1.5, 'F5', 1.5), (3.0, 'Eb5', 0.5), (3.5, 'Db5', 1.5)]:
    preview.add(b(0, beat), p, ln * BEAT + 0.05, 64)
harp = Part('harp', 'Harp', level=-18, pan=-0.55, send=0.45, split=True, env=[(0, -12), (1.5, -4), (2.5, 0)])
for i, p in enumerate(['Bb2', 'F3', 'Db4', 'F3', 'Bb3', 'F3', 'Db4', 'F3']):
    harp.add(0.3 + i * BEAT / 2 * 0.98, p, 1.2, 70 + (8 if i % 4 == 0 else 0))
for i, p in enumerate([p for p in range(n('F3'), n('F6') + 1) if p % 12 in (10, 0, 1, 3, 5, 6, 8)]):
    harp.add(4.25 + i * 0.026, p, 0.4, 70 + i * 2)
harp.add(FINAL, ['Bb1', 'F2', 'Bb2', 'D3', 'F3', 'Bb3'], 3.0, 124)
mech = Part('mechanics', 'perc', level=-20, pan=0.2, send=0.45, split=True, env=[(0, -10), (2.4, 0)])
for t, k, v in [(0.55, 'ratchet_slow', 80), (1.20, 'brake', 64), (1.65, 'ratchet', 96), (2.10, 'brake', 90),
                (2.40, 'anvil', 100), (3.75, 'ratchet_fast', 110)]:
    mech.add(t, PERC[k], 1.0, v)
braam = Part('braam', 'TromboneSus', level=-17, pan=0.3, send=0.45,
             env=[(0.2, -36), (2.4, -10), (2.5, -14), (4.84, 0)] + BREATH[1:] + [(5.0, -60)])
braam.add(0.20, ['Bb1', 'F2'], 2.35, 116).add(2.50, ['Eb2', 'Ab2', 'Eb3'], 2.4, 120)
braam_u = Part('braam_tuba', 'TubaSus', level=-20, pan=0.4, send=0.35,
               env=[(0.2, -36), (2.4, -10), (2.5, -14), (4.84, 0)] + BREATH[1:] + [(5.0, -60)])
braam_u.add(0.20, 'Bb1', 2.35, 116).add(2.50, 'Ab1', 2.4, 120)

# ======================= strings
SECT = [(0, -2), (2.5, -12), (4.84, -3)] + BREATH[1:] + [(5.0, 2), (FINAL - 0.05, 2), (FINAL, -60)]
osti_va = Part('pulse_violas', 'ViolaEnsSpic', level=-17, pan=0.15, send=0.35, align=b(1), env=SECT)
osti_vc = Part('pulse_cellos', 'CelloEnsSpic', level=-16, pan=0.3, send=0.3, align=b(1), env=SECT)
for k in (1, 2, 3):
    for i in range(16):
        t = s16(k, i)
        if 4.84 <= t < 5.0:
            continue
        r, t3, f = chord_at(k, i)
        acc = i % 4 == 0
        osti_va.add(t, (f + '4') if i % 2 == 0 else (r + '4'), 0.1, 94 if acc else 72)
        osti_vc.add(t, r + ('2' if r in ('Bb', 'Ab', 'Gb') else '3'), 0.1, 106 if acc else 78)
vc_pad = Part('cello_pad', 'CelloEnsSusVib', level=-18, pan=0.3, send=0.4, env=[(2.5, -10), (4.84, -2)] + BREATH[1:] + [(5.0, 0)] + OUT)
cb_pad = Part('bass_pad', 'ContrabassSusVB', level=-19, pan=0.4, send=0.3, env=[(2.5, -10), (4.84, -2)] + BREATH[1:] + [(5.0, 0)] + OUT)
vc_pad.add(b(1), 'Bb2', 2.35, 70)
cb_pad.add(b(1), 'Bb1', 2.35, 66)
for k in (2, 3):
    for half in (0, 2):
        r = HALF[(k, half)][0]
        vc_pad.add(b(k, half), r + ('2' if r in ('Bb', 'Ab', 'Gb') else '3'), 1.28, 112)
        cb_pad.add(b(k, half), r + '1' if r != 'Db' else 'Db2', 1.28, 112)
vc_pad.add(FINAL, ['Bb2', 'F3'], 3.0, 124)
cb_pad.add(FINAL, 'Bb1', 3.0, 124)
trem = Part('violin_trem', 'ViolinEnsTrem', level=-21, pan=-0.35, send=0.5, env=[(2.5, -16), (4.84, 0)] + BREATH[1:] + [(5.0, -60)])
for i, p in enumerate(['F5', 'Gb5', 'G5', 'Ab5', 'A5']):
    trem.add(2.5 + i * 0.47, [p, n(p) - 12], 0.5, 72 + i * 10)
vln = Part('violins', 'ViolinEnsSusVib', level=-15, pan=-0.35, send=0.45, align=b(3), env=[(b(2), -8), (b(3), 0)] + OUT)
for half in (0, 2):
    r, t3, f = HALF[(2, half)]
    vln.add(b(2, half), [f + '5', t3 + ('6' if t3 == 'Db' else '5')], 1.28, 96)
for k, beat, p, ln in THEME:
    if k == 3:
        vln.add(b(k, beat), n(p) + 12, ln * BEAT + 0.03, 122)
vln.add(FINAL, ['D5', 'F5', 'Bb5'], 3.0, 126)

# ======================= choir
choir = Part('choir', ('gm', 52), level=-19, pan=-0.05, send=0.55, env=[(2.5, -12), (4.84, -3)] + BREATH[1:] + [(5.0, 0)] + OUT)
choir.add(b(1), ['Bb2', 'F3', 'Db4', 'F4'], 2.34, 90)
for k in (2, 3):
    for half in (0, 2):
        r, t3, f = HALF[(k, half)]
        choir.add(b(k, half), [r + '3', f + '3', t3 + '4', f + '4'], 1.25, 112)
choir.add(FINAL, ['Bb2', 'F3', 'D4', 'F4', 'Bb4'], 3.0, 124)

# ======================= brass
hn = Part('horns', 'FHornSus', level=-12, pan=-0.15, send=0.45, align=LOUD, env=[(LOUD, 0), (FINAL, 1)] + OUT[1:])
for k, beat, p, ln in THEME:
    hn.add(b(k, beat), [p, n(p) - 12], ln * BEAT + 0.03, 124)
hn.add(FINAL, ['Bb2', 'F3', 'Bb3', 'D4', 'F4'], 3.0, 127)
tbn = Part('trombones', 'TromboneSus', level=-13, pan=0.35, send=0.4, align=LOUD, env=[(LOUD, 0), (FINAL, 1)] + OUT[1:])
for k, beat, p, ln in THEME:
    tbn.add(b(k, beat), n(p) - 12, ln * BEAT + 0.03, 122)
tbn.add(FINAL, ['Bb1', 'F2', 'Bb2', 'D3'], 3.0, 127)
tba = Part('tuba', 'TubaSus', level=-16, pan=0.4, send=0.3, align=LOUD, env=[(LOUD, 0), (FINAL, 1)] + OUT[1:])
for k in (2, 3):
    for half in (0, 2):
        r = HALF[(k, half)][0]
        tba.add(b(k, half), r + ('2' if r == 'Db' else '1'), 1.28, 120)
tba.add(FINAL, 'Bb1', 3.0, 127)
tpt = Part('trumpets', 'TrumpetSus', level=-13, pan=0.2, send=0.45, align=b(3), env=[(b(3), 0), (FINAL, 2)] + OUT[1:])
for k, beat, p, ln in THEME:
    if k == 3:
        tpt.add(b(k, beat), p if n(p) >= n('E4') else n(p) + 12, ln * BEAT + 0.03, 124)
tpt.add(FINAL, ['F4', 'Bb4', 'D5'], 2.8, 127)

# ======================= the beat
DSECT = [(0, 0), (2.5, -7), (4.84, -2)] + BREATH + [(FINAL - 0.02, 0), (FINAL, 0), (10.35, -5), (11.2, -13)]
kick = Part('kick', 'perc', level=-12, pan=0.0, send=0.22, split=True, env=DSECT)
snare = Part('snare', 'perc', level=-15, pan=-0.05, send=0.28, split=True, env=DSECT)
shaker = Part('shaker', 'perc', level=-27, pan=0.35, send=0.2, split=True, env=DSECT)
metal = Part('metal', 'perc', level=-17, pan=0.2, send=0.4, split=True, env=DSECT)
timp = Part('timpani', 'Timpani', level=-14, pan=-0.15, send=0.3, split=True, env=DSECT)
for i in range(16):                                              # build bar: doubling up
    t = s16(1, i)
    if t >= 4.84:
        continue
    if i % 4 == 0 or i >= 8 and i % 2 == 0 or i >= 12:
        kick.add(t, PERC['bdd'], 0.3, 80 + i * 3)
    if i % 2 == 0:
        shaker.add(t, PERC['shaker'], 0.15, 70)
    if i in (0, 8, 12, 14):
        timp.add(t, 'Bb2' if i in (0, 8) else 'F2', 0.4, 90 + i * 2)
snare.add(b(1, 2), PERC['sroll'], 1.2, 112)
for k in (2, 3):
    kick.add(b(k), PERC['bd'], 2.0, 127)
    for i in (0, 3, 6, 8, 10, 11, 14):
        kick.add(s16(k, i), PERC['bdd'], 0.3, 124 if i in (0, 8) else 106)
    for i in (4, 12):                                            # backbeat on 2 and 4
        snare.add(s16(k, i), PERC['snare'], 0.4, 127)
        metal.add(s16(k, i), PERC['anvil'] if i == 4 else PERC['brake'], 0.8, 108)
    for i in range(16):
        shaker.add(s16(k, i), PERC['shaker'], 0.12, 92 if i % 4 == 0 else 70)
    for i in (0, 6, 8, 13, 14, 15):
        r, t3, f = chord_at(k, i)
        timp.add(s16(k, i), (r if i in (0, 8, 15) else f) + '2', 0.4, 120 if i in (0, 8) else 104 + (i - 13) * 6)
    if k == 3:
        snare.add(s16(k, 14), PERC['snare'], 0.2, 96).add(s16(k, 15), PERC['snare'], 0.2, 110)
    metal.add(b(k), PERC['crash'], 2.5, 124 if k == 2 else 108)
kick.add(FINAL, PERC['bd'], 3.0, 127)
snare.add(FINAL, PERC['snare'], 1.0, 127)
timp.add(FINAL, ['F2', 'Bb2'], 2.5, 127)
metal.add(FINAL, PERC['crash'], 3.0, 127).add(FINAL, PERC['anvil'], 1.0, 120)
gong = Part('gong', 'perc', level=-20, pan=-0.1, send=0.5, split=True, env=OUT)
gong.add(FINAL, PERC['gong'], 3.0, 120)
swell = Part('cym_swell', 'perc', level=-22, pan=0.1, send=0.5, thresh=0.001)
swell.add(LOUD - 1.53, PERC['swell_s'], 1.55, 120).add(FINAL - 1.53, PERC['swell_s'], 1.55, 104)
troll = Part('timp_roll', 'TimpaniRolls', level=-18, pan=-0.15, send=0.35,
             env=[(3.75, -22), (4.84, 0), (4.88, -60), (8.9, -60), (8.95, -18), (9.88, -2), (9.92, -60)])
troll.add(3.75, 'F2', 1.15, 110).add(8.95, 'F2', 1.05, 110)
bells = Part('bells', 'TubularBells', level=-22, pan=0.2, send=0.5, split=True)
bells.add(LOUD, ['F4', 'Bb4'], 2.5, 110).add(FINAL, ['F4', 'Bb4', 'D5'], 3.0, 122)
cel = Part('celesta', ('gm', 8), level=-23, pan=-0.3, send=0.55)
for k in (2, 3):
    for half in (0, 2):
        r, t3, f = HALF[(k, half)]
        cel.add(b(k, half), [r + '6', f + '6'], 0.8, 80)
cel.add(FINAL + 1.2, ['Bb5', 'F6'], 1.5, 60)

PARTS = [preview, harp, mech, braam, braam_u, osti_va, osti_vc, vc_pad, cb_pad, trem, vln, choir, hn, tbn, tba, tpt,
         kick, snare, shaker, metal, timp, gong, swell, troll, bells, cel]
ACCENTS = [2.5, LOUD, b(3), FINAL]

if __name__ == '__main__':
    out = sys.argv[1]
    y, rep = build('TAGS_theme', PARTS, LEN, os.path.join(out, 'build'), reverb=(72, 40, 100, 100, 25, 0), wet=0.3,
                   fade=(11.6, 12.95))
    wav, ogg = export(y, out, 'TAGS_theme')
    save_score(PARTS, os.path.join(out, 'TAGS_theme.mid'))
    y = decode(ogg)
    rep['length_samples'] = len(y)
    rep['ogg_peak_dbfs'] = round(ogg_peak_db(ogg), 2)
    rep['accents'] = {str(round(t, 2)): round(accent_time(y, t), 4) for t in ACCENTS}
    json.dump(rep, open(os.path.join(out, 'TAGS_theme_report.json'), 'w'), indent=1)
    print(json.dumps(rep['accents']))
