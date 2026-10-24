"""TAGS_theme - 16.0 s, B-flat minor -> B-flat major, 96 bpm (beat 0.625 s,
bar 2.5 s). Original music in the style of the Transformers-era Paramount
intros: robotic/metal sounds and a braam, a string pulse with choir, a driving
beat and a heroic unison-horn theme over i - VI - III - VII.

0-2.5     from silence: soft violins preview the theme over a harp arpeggio, quiet
          ratchets and metal clanks, a low braam fading in
2.5-5.0   the build: 16th string pulse, choir swell, kick doubling up, snare and
          timpani rolls, braam, cymbal swell, a breath before 5.0
5.0-7.5   LOUD: horns + trombones play the theme over the full beat (Bbm - Gb)
7.5-10.0  BEAT DOWN: the drums drop out to a heartbeat, the strings hold Gb -> Ab quietly,
          then a riser (snare roll, climbing tremolo, braam, cymbal swell, ratchets)
          and a breath before 10.0
10.0-12.5 MEGA UP: everything bigger - the theme climax with trumpets and violins an
          octave up, double-time kick, timpani 16ths, full choir, crashes (Db - Ab)
12.5      the final hit on B-flat MAJOR, held to 13.0
13.0-16.0 slowly down to silence."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orch import Part, PERC, build, export, save_score, accent_time, decode, ogg_peak_db, n

LEN = 16.0
BEAT = 0.625
BAR = 2.5
LOUD, DOWN, MEGA, FINAL = 5.0, 7.5, 10.0, 12.5
BREATH1 = [(4.84, 0), (4.88, -60), (4.985, -60), (4.99, 0)]
BREATH2 = [(9.84, 0), (9.88, -60), (9.985, -60), (9.99, 0)]
OUT = [(FINAL, 0), (13.0, -1), (14.5, -10), (15.9, -50)]       # slowly down from 13 s


def b(k, beat=0.0):
    return k * BAR + beat * BEAT


def s16(k, i):
    return b(k, i / 4)


HALF = {(1, 0): ('Bb', 'Db', 'F'), (1, 2): ('Bb', 'Db', 'F'), (2, 0): ('Bb', 'Db', 'F'), (2, 2): ('Gb', 'Bb', 'Db'),
        (3, 0): ('Gb', 'Bb', 'Db'), (3, 2): ('Ab', 'C', 'Eb'), (4, 0): ('Db', 'F', 'Ab'), (4, 2): ('Ab', 'C', 'Eb')}


def chord_at(k, i):
    return HALF[(k, 0 if i < 8 else 2)]


def lowroot(r):
    return r + ('2' if r in ('Bb', 'Ab', 'Gb') else '3')


THEME1 = [(2, 0, 'Bb3', 1.0), (2, 1, 'F4', 2.0), (2, 3, 'Eb4', 0.5), (2, 3.5, 'Db4', 0.5)]
THEME2 = [(4, 0, 'Ab4', 1.5), (4, 1.5, 'Gb4', 0.5), (4, 2, 'F4', 1.0), (4, 3, 'Eb4', 0.5), (4, 3.5, 'F4', 0.5)]

# ======================= 0-2.5: from silence
preview = Part('theme_preview', 'ViolinEnsSusVib-Quiet', level=-17, pan=-0.3, send=0.55,
               env=[(0.3, -14), (1.2, -4), (2.2, 0), (2.6, -6), (3.2, -40)])
for beat, p, ln in [(0.5, 'Bb4', 1.0), (1.5, 'F5', 1.5), (3.0, 'Eb5', 0.5), (3.5, 'Db5', 1.5)]:
    preview.add(b(0, beat), p, ln * BEAT + 0.05, 64)
harp = Part('harp', 'Harp', level=-18, pan=-0.55, send=0.45, split=True, env=[(0, -12), (1.5, -4), (2.5, 0)])
for i, p in enumerate(['Bb2', 'F3', 'Db4', 'F3', 'Bb3', 'F3', 'Db4', 'F3']):
    harp.add(0.3 + i * BEAT / 2 * 0.98, p, 1.2, 70 + (8 if i % 4 == 0 else 0))
for t0 in (4.25, 9.25):
    for i, p in enumerate([p for p in range(n('F3'), n('F6') + 1) if p % 12 in (10, 0, 1, 3, 5, 6, 8)]):
        harp.add(t0 + i * 0.026, p, 0.4, 70 + i * 2)
for i, p in enumerate(['Gb2', 'Db3', 'Bb3', 'Db4']):            # breakdown: gentle arpeggio
    harp.add(DOWN + i * 0.31, p, 1.2, 64)
harp.add(FINAL, ['Bb1', 'F2', 'Bb2', 'D3', 'F3', 'Bb3'], 3.0, 124)
mech = Part('mechanics', 'perc', level=-20, pan=0.2, send=0.45, split=True, env=[(0, -10), (2.4, 0)])
for t, k, v in [(0.55, 'ratchet_slow', 80), (1.20, 'brake', 64), (1.65, 'ratchet', 96), (2.10, 'brake', 90),
                (2.40, 'anvil', 100), (3.75, 'ratchet_fast', 110), (8.10, 'ratchet_slow', 96), (8.75, 'ratchet_fast', 110)]:
    mech.add(t, PERC[k], 1.0, v)
BRAAM_ENV = [(0.2, -36), (2.4, -10), (2.5, -14), (4.84, 0)] + BREATH1[1:] + [(5.0, -60), (8.75, -60), (8.76, -18), (9.84, 0)] + BREATH2[1:] + [(10.0, -60)]
braam = Part('braam', 'TromboneSus', level=-17, pan=0.3, send=0.45, env=BRAAM_ENV)
braam.add(0.20, ['Bb1', 'F2'], 2.35, 116).add(2.50, ['Eb2', 'Ab2', 'Eb3'], 2.4, 120).add(8.76, ['Eb2', 'Ab2', 'Eb3'], 1.2, 122)
braam_u = Part('braam_tuba', 'TubaSus', level=-20, pan=0.4, send=0.35, env=BRAAM_ENV)
braam_u.add(0.20, 'Bb1', 2.35, 116).add(2.50, 'Ab1', 2.4, 120).add(8.76, 'Ab1', 1.2, 122)

# ======================= strings
SECT = ([(0, -2), (2.5, -12), (4.84, -3)] + BREATH1[1:] + [(5.0, 1), (7.45, 1), (7.5, -14), (8.75, -14), (9.84, -2)]
        + BREATH2[1:] + [(10.0, 3), (FINAL - 0.05, 3), (FINAL, -60)])
osti_va = Part('pulse_violas', 'ViolaEnsSpic', level=-17, pan=0.15, send=0.35, align=b(1), env=SECT)
osti_vc = Part('pulse_cellos', 'CelloEnsSpic', level=-16, pan=0.3, send=0.3, align=b(1), env=SECT)
for k in (1, 2, 3, 4):
    for i in range(16):
        t = s16(k, i)
        if 4.84 <= t < 5.0 or 9.84 <= t < 10.0:
            continue
        r, t3, f = chord_at(k, i)
        acc = i % 4 == 0
        osti_va.add(t, (f + '4') if i % 2 == 0 else (r + '4'), 0.1, 94 if acc else 72)
        osti_vc.add(t, lowroot(r), 0.1, 106 if acc else 78)
PAD_ENV = [(2.5, -10), (4.84, -2)] + BREATH1[1:] + [(5.0, -2), (7.45, -2), (7.5, -8), (9.84, -2)] + BREATH2[1:] + [(10.0, 1)] + OUT
vc_pad = Part('cello_pad', 'CelloEnsSusVib', level=-18, pan=0.3, send=0.4, env=PAD_ENV)
cb_pad = Part('bass_pad', 'ContrabassSusVB', level=-19, pan=0.4, send=0.3, env=PAD_ENV)
vc_pad.add(b(1), 'Bb2', 2.35, 70)
cb_pad.add(b(1), 'Bb1', 2.35, 66)
for k in (2, 3, 4):
    for half in (0, 2):
        r = HALF[(k, half)][0]
        d = 1.18 if (k, half) == (3, 2) else 1.28
        vc_pad.add(b(k, half), lowroot(r), d, 112 if k != 3 else 84)
        cb_pad.add(b(k, half), r + '1' if r != 'Db' else 'Db2', d, 112 if k != 3 else 80)
vc_pad.add(FINAL, ['Bb2', 'F3'], 3.4, 124)
cb_pad.add(FINAL, 'Bb1', 3.4, 124)
trem = Part('violin_trem', 'ViolinEnsTrem', level=-21, pan=-0.35, send=0.5,
            env=[(2.5, -16), (4.84, 0)] + BREATH1[1:] + [(5.0, -60), (7.5, -60), (7.55, -16), (9.84, 0)] + BREATH2[1:] + [(10.0, -60)])
for t0 in (2.5, 7.55):
    for i, p in enumerate(['F5', 'Gb5', 'G5', 'Ab5', 'A5']):
        trem.add(t0 + i * 0.46, [p, n(p) - 12], 0.5, 72 + i * 10)
vln = Part('violins', 'ViolinEnsSusVib', level=-15, pan=-0.35, send=0.45, align=MEGA, env=[(b(2), -8), (b(4), 0)] + OUT)
for half in (0, 2):
    r, t3, f = HALF[(2, half)]
    vln.add(b(2, half), [f + '5', t3 + ('6' if t3 == 'Db' else '5')], 1.28, 96)
for k, beat, p, ln in THEME2:
    vln.add(b(k, beat), n(p) + 12, ln * BEAT + 0.03, 124)
vln.add(FINAL, ['D5', 'F5', 'Bb5'], 3.4, 127)

# ======================= choir
choir = Part('choir', ('gm', 52), level=-19, pan=-0.05, send=0.55, env=PAD_ENV[:-len(OUT)] + [(10.0, 2)] + OUT)
choir.add(b(1), ['Bb2', 'F3', 'Db4', 'F4'], 2.34, 90)
for k in (2, 3, 4):
    for half in (0, 2):
        r, t3, f = HALF[(k, half)]
        d = 1.18 if (k, half) == (3, 2) else 1.25
        choir.add(b(k, half), [r + '3', f + '3', t3 + '4', f + '4'] + ([r + '4'] if k == 4 else []), d, 112 if k != 3 else 86)
choir.add(FINAL, ['Bb2', 'F3', 'D4', 'F4', 'Bb4'], 3.4, 127)

# ======================= brass
BR_ENV = [(LOUD, -1), (7.45, -1), (7.5, -60), (9.99, -60), (MEGA, 2), (FINAL, 2)] + OUT[1:]
hn = Part('horns', 'FHornSus', level=-12, pan=-0.15, send=0.45, align=LOUD, env=BR_ENV)
for k, beat, p, ln in THEME1 + THEME2:
    hn.add(b(k, beat), [p, n(p) - 12], ln * BEAT + 0.03, 124)
hn.add(FINAL, ['Bb2', 'F3', 'Bb3', 'D4', 'F4'], 3.4, 127)
tbn = Part('trombones', 'TromboneSus', level=-13, pan=0.35, send=0.4, align=LOUD, env=BR_ENV)
for k, beat, p, ln in THEME1 + THEME2:
    tbn.add(b(k, beat), n(p) - 12, ln * BEAT + 0.03, 122)
tbn.add(FINAL, ['Bb1', 'F2', 'Bb2', 'D3'], 3.4, 127)
tba = Part('tuba', 'TubaSus', level=-16, pan=0.4, send=0.3, align=LOUD, env=BR_ENV)
for k in (2, 4):
    for half in (0, 2):
        r = HALF[(k, half)][0]
        tba.add(b(k, half), r + ('2' if r == 'Db' else '1'), 1.28, 120)
tba.add(FINAL, 'Bb1', 3.4, 127)
tpt = Part('trumpets', 'TrumpetSus', level=-12, pan=0.2, send=0.45, align=MEGA, env=[(MEGA, 0), (FINAL, 2)] + OUT[1:])
for k, beat, p, ln in THEME2:
    tpt.add(b(k, beat), p if n(p) >= n('E4') else n(p) + 12, ln * BEAT + 0.03, 127)
tpt.add(FINAL, ['F4', 'Bb4', 'D5'], 3.0, 127)

# ======================= the beat
DSECT = ([(0, 0), (2.5, -7), (4.84, -2)] + BREATH1 + [(5.0, -1), (7.45, -1), (7.5, 0), (9.84, 0)] + BREATH2
         + [(MEGA, 1), (FINAL - 0.02, 1), (FINAL, 0)] + OUT[1:])
kick = Part('kick', 'perc', level=-12, pan=0.0, send=0.22, split=True, env=DSECT)
snare = Part('snare', 'perc', level=-15, pan=-0.05, send=0.28, split=True, env=DSECT)
shaker = Part('shaker', 'perc', level=-27, pan=0.35, send=0.2, split=True, env=DSECT)
metal = Part('metal', 'perc', level=-17, pan=0.2, send=0.4, split=True, env=DSECT)
timp = Part('timpani', 'Timpani', level=-14, pan=-0.15, send=0.3, split=True, env=DSECT)
for i in range(16):                                              # build bar
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


def full_bar(k, mega=False):
    kick.add(b(k), PERC['bd'], 2.0, 127)
    for i in (range(0, 16, 2) if mega else (0, 3, 6, 8, 10, 11, 14)):
        kick.add(s16(k, i), PERC['bdd'], 0.3, 124 if i in (0, 8) else (112 if mega else 106))
    if mega:
        kick.add(b(k, 2), PERC['bd'], 2.0, 124)
    for i in (4, 12):
        snare.add(s16(k, i), PERC['snare'], 0.4, 127)
        metal.add(s16(k, i), PERC['anvil'] if i == 4 else PERC['brake'], 0.8, 116 if mega else 104)
    for i in range(16):
        shaker.add(s16(k, i), PERC['shaker'], 0.12, 96 if i % 4 == 0 else 74)
    for i in (range(16) if mega else (0, 6, 8, 13, 14, 15)):
        r, t3, f = chord_at(k, i)
        if mega and i % 2 and i < 12:
            continue
        timp.add(s16(k, i), (r if i in (0, 8, 15) or (mega and i % 4 == 0) else f) + '2', 0.4,
                 124 if i in (0, 8) else 104 + max(0, i - 12) * 5)
    metal.add(b(k), PERC['crash'], 2.5, 127 if mega else 116)
    if mega:
        metal.add(b(k, 2), PERC['crash'], 2.0, 112)
        snare.add(s16(k, 13), PERC['snare'], 0.2, 96).add(s16(k, 14), PERC['snare'], 0.2, 108).add(s16(k, 15), PERC['snare'], 0.2, 120)


full_bar(2)
full_bar(4, mega=True)
for beat in (0, 2):                                              # beat down: a heartbeat only
    kick.add(b(3, beat), PERC['bdd'], 0.3, 70)
snare.add(8.75, PERC['sroll'], 1.08, 118)
for i in (8, 10, 12, 13, 14, 15):
    if s16(3, i) < 9.84:
        timp.add(s16(3, i), 'Ab2' if i % 2 == 0 else 'Eb2', 0.4, 92 + i * 2)
kick.add(FINAL, PERC['bd'], 3.0, 127)
snare.add(FINAL, PERC['snare'], 1.0, 127)
timp.add(FINAL, ['F2', 'Bb2'], 2.5, 127)
metal.add(FINAL, PERC['crash'], 3.0, 127).add(FINAL, PERC['anvil'], 1.0, 124)
gong = Part('gong', 'perc', level=-19, pan=-0.1, send=0.5, split=True, env=[(0, 0)] + OUT)
gong.add(MEGA, PERC['gong'], 2.5, 100).add(FINAL, PERC['gong'], 3.4, 124)
swell = Part('cym_swell', 'perc', level=-22, pan=0.1, send=0.5, thresh=0.001)
swell.add(LOUD - 1.53, PERC['swell_s'], 1.55, 120).add(MEGA - 1.53, PERC['swell_s'], 1.55, 127)
troll = Part('timp_roll', 'TimpaniRolls', level=-18, pan=-0.15, send=0.35,
             env=[(3.75, -22), (4.84, 0), (4.88, -60), (8.7, -60), (8.75, -20), (9.84, 0), (9.88, -60),
                  (11.4, -60), (11.45, -18), (12.38, -2), (12.42, -60)])
troll.add(3.75, 'F2', 1.15, 110).add(8.75, 'F2', 1.15, 110).add(11.45, 'F2', 1.0, 110)
bells = Part('bells', 'TubularBells', level=-22, pan=0.2, send=0.5, split=True)
bells.add(LOUD, ['F4', 'Bb4'], 2.5, 110).add(MEGA, ['Ab4', 'Db5'], 2.5, 118).add(FINAL, ['F4', 'Bb4', 'D5'], 3.4, 124)
cel = Part('celesta', ('gm', 8), level=-23, pan=-0.3, send=0.55)
for k in (2, 4):
    for half in (0, 2):
        r, t3, f = HALF[(k, half)]
        cel.add(b(k, half), [r + '6', f + '6'], 0.8, 80)
cel.add(14.0, ['Bb5', 'F6'], 1.5, 56)

PARTS = [preview, harp, mech, braam, braam_u, osti_va, osti_vc, vc_pad, cb_pad, trem, vln, choir, hn, tbn, tba, tpt,
         kick, snare, shaker, metal, timp, gong, swell, troll, bells, cel]
ACCENTS = [2.5, LOUD, DOWN, MEGA, FINAL]

if __name__ == '__main__':
    out = sys.argv[1]
    y, rep = build('TAGS_theme', PARTS, LEN, os.path.join(out, 'build'), reverb=(72, 40, 100, 100, 25, 0), wet=0.3,
                   fade=(14.6, 15.95))
    wav, ogg = export(y, out, 'TAGS_theme')
    save_score(PARTS, os.path.join(out, 'TAGS_theme.mid'))
    y = decode(ogg)
    rep['length_samples'] = len(y)
    rep['ogg_peak_dbfs'] = round(ogg_peak_db(ogg), 2)
    rep['accents'] = {str(round(t, 2)): round(accent_time(y, t), 4) for t in ACCENTS}
    json.dump(rep, open(os.path.join(out, 'TAGS_theme_report.json'), 'w'), indent=1)
    print(json.dumps(rep['accents']))
