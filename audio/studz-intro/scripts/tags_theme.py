"""TAGS_theme - the long version of the TAGS ident, 30.0 s, B-flat minor ->
B-flat major, 80 bpm (beat 0.75 s, bar 3.0 s). Original music in the style of
the Transformers-era Paramount intros: robotic/metal logo sounds and a low
braam, an emotional quiet start, a steady 16th string pulse with choir, half-
time drums, and a heroic unison-horn theme over i - VI - III - VII.

bar 0    0-3    the logo: boom, gong scrape, ratchets and metal clanks (the "transforming"
                sounds), a low brass braam swelling up, an anvil
bar 1    3-6    quiet and emotional: soft violins preview the main theme over a harp arpeggio
bars 2-3 6-12   the pulse: 16th spiccato strings, choir "aah", timpani on 1 and 3;
                horns hint at the theme
bar 4    12-15  the rise: drums double up, snare roll, string tremolo climbs, choir and
                braam swell, cymbal swell, a breath before the downbeat
bars 5-8 15-27  THE THEME: horns + trombones in unison, choir, strings, big half-time
                drums, anvil/brake-drum backbeat; trumpets and violins join an octave up
                for the second half
27       final hit: B-flat MAJOR (heroic), gong, crash, metal clang, rings out to 30 s."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orch import Part, PERC, build, export, save_score, accent_time, decode, ogg_peak_db, n

LEN = 30.0
BEAT = 0.75
BAR = 3.0
THEME_T, FINAL = 15.0, 27.0
BREATH = [(14.82, 0), (14.86, -60), (14.98, -60), (14.99, 0)]


def b(k, beat=0.0):
    """Time of beat `beat` (may be fractional) in bar k."""
    return k * BAR + beat * BEAT


# chords per bar (i - VI - III - VII in B-flat minor), as (root, third, fifth)
CH = {1: ('Bb', 'Db', 'F'), 2: ('Bb', 'Db', 'F'), 3: ('Gb', 'Bb', 'Db'), 4: ('Ab', 'C', 'Eb'),
      5: ('Bb', 'Db', 'F'), 6: ('Gb', 'Bb', 'Db'), 7: ('Db', 'F', 'Ab'), 8: ('Ab', 'C', 'Eb')}
# the theme (horns), per bar: (beat, note, beats long)
THEME = {5: [(0, 'Bb3', 1.0), (1, 'F4', 2.0), (3, 'Eb4', 0.5), (3.5, 'Db4', 0.5)],
         6: [(0, 'Db4', 1.5), (1.5, 'Eb4', 0.5), (2, 'F4', 2.0)],
         7: [(0, 'Ab4', 1.5), (1.5, 'Gb4', 0.5), (2, 'F4', 1.0), (3, 'Eb4', 1.0)],
         8: [(0, 'Eb4', 2.0), (2, 'F4', 0.5), (2.5, 'Ab4', 1.5)]}

# ======================= bar 0: the logo - metal, ratchets, braam
mech = Part('mechanics', 'perc', level=-18, pan=0.2, send=0.4, split=True,
            env=[(0, 0), (2.95, 0), (3.5, -40), (11.9, -40), (12.0, 0)])   # the gong scrape rings ~8 s: stop it after the logo
mech.add(0.05, PERC['gscrape'], 3.0, 100)
for t, k, v in [(0.45, 'ratchet_slow', 100), (0.95, 'brake', 90), (1.20, 'brake', 70), (1.55, 'ratchet', 110),
                (2.05, 'brake', 100), (2.20, 'anvil', 80), (2.45, 'ratchet_fast', 110), (2.92, 'anvil', 120)]:
    mech.add(t, PERC[k], 1.0, v)
for t in (b(4, 0), b(4, 2)):                                      # mechanical clicks in the rise
    mech.add(t, PERC['ratchet_fast'], 1.0, 96)
boom = Part('boom', 'perc', level=-13, pan=0.0, send=0.35, split=True)
boom.add(0.05, PERC['bd'], 3.0, 124)
boom.add(2.95, PERC['bd'], 3.0, 110)
braam_t = Part('braam_tbn', 'TromboneSus', level=-15, pan=0.3, send=0.45, env=[(0.4, -24), (2.85, 0), (2.92, -60)])
braam_t.add(0.40, ['Bb1', 'F2', 'Bb2'], 2.55, 120)
braam_u = Part('braam_tuba', 'TubaSus', level=-18, pan=0.4, send=0.35, env=[(0.4, -24), (2.85, 0), (2.92, -60)])
braam_u.add(0.40, 'Bb1', 2.55, 120)
gong = Part('gong', 'perc', level=-20, pan=-0.1, send=0.5, split=True)
gong.add(FINAL, PERC['gong'], 4.0, 127)

# ======================= bar 1: quiet and emotional (a preview of the theme)
cel = Part('celesta', ('gm', 8), level=-21, pan=-0.3, send=0.55, env=[(3.0, 3), (6.2, 1)])
for k in range(5, 9):
    cel.add(b(k), [CH[k][0] + '6', CH[k][2] + '6'], 0.9, 80)
harp = Part('harp', 'Harp', level=-18, pan=-0.55, send=0.45, split=True)
harp.add(3.0, 'Bb1', 3.0, 76)
for i, p in enumerate(['Bb2', 'F3', 'Db4', 'F3', 'Bb3', 'F3', 'Db4', 'F3']):      # slow arpeggio under the preview
    harp.add(3.0 + i * 0.375, p, 1.2, 72 + (8 if i % 4 == 0 else 0))
# a soft preview of the main theme (bars 5-6), sung by quiet violins
preview = Part('theme_preview', 'ViolinEnsSusVib-Quiet', level=-15, pan=-0.3, send=0.55,
               env=[(3.0, -4), (4.0, 0), (5.6, 0), (6.4, -8), (7.0, -40)])
for beat, p, ln in [(0, 'Bb4', 1.0), (1, 'F5', 2.0), (3, 'Eb5', 0.5), (3.5, 'Db5', 1.5)]:
    preview.add(b(1, beat), p, ln * BEAT + 0.05, 64)
for i, p in enumerate([p for p in range(n('F3'), n('F6') + 1) if p % 12 in (10, 0, 1, 3, 5, 6, 8)]):
    harp.add(14.20 + i * 0.028, p, 0.4, 70 + i * 2)
harp.add(FINAL, ['Bb1', 'F2', 'Bb2', 'D3', 'F3', 'Bb3'], 3.0, 124)

# ======================= strings
pad = Part('string_pad', 'ViolaEnsSusVib', level=-20, pan=0.1, send=0.5, env=[(3.0, -10), (4.5, -4), (6.0, -4), (12.0, -6), (14.8, -2)] + BREATH[1:] + [(15.0, -6)])
pad.add(3.0, ['Db4', 'F4'], 3.05, 60)
for k in (2, 3, 4):
    r, t3, f = CH[k]
    pad.add(b(k), [t3 + '4', f + '4'], 3.05 if k < 4 else 2.84, 66 + (k - 2) * 8)
for k in range(5, 9):
    r, t3, f = CH[k]
    pad.add(b(k), [t3 + '4', f + '4'], 3.05, 100)
vc_pad = Part('cello_pad', 'CelloEnsSusVib', level=-19, pan=0.3, send=0.4,
              env=[(3.0, -10), (4.5, -3), (12.0, -3), (14.8, 0)] + BREATH[1:] + [(15.0, 0), (26.9, 0), (FINAL, 2), (28.5, -4), (29.7, -30)])
cb_pad = Part('bass_pad', 'ContrabassSusVB', level=-20, pan=0.4, send=0.3,
              env=[(3.0, -10), (4.5, -3), (12.0, -3), (14.8, 0)] + BREATH[1:] + [(15.0, 0), (26.9, 0), (FINAL, 2), (28.5, -4), (29.7, -30)])
for k in range(1, 9):
    r = CH[k][0]
    d = 2.84 if k == 4 else 3.05
    vc_pad.add(b(k), r + ('2' if r in ('Bb', 'Ab', 'Gb') else '3'), d, 64 if k < 5 else 110)
    cb_pad.add(b(k), r + '1', d, 60 if k < 5 else 110)
vc_pad.add(FINAL, ['Bb2', 'F3'], 3.0, 124)
cb_pad.add(FINAL, 'Bb1', 3.0, 124)

# the 16th pulse (violas + cellos spiccato), from bar 2
SECT = [(0, -2), (6.0, -2), (9.0, -1), (12.0, -1), (14.8, 0)] + BREATH[1:] + [(15.0, 2), (26.9, 2), (26.95, -60)]
osti_va = Part('pulse_violas', 'ViolaEnsSpic', level=-18, pan=0.15, send=0.35, align=b(2), env=SECT)
osti_vc = Part('pulse_cellos', 'CelloEnsSpic', level=-17, pan=0.3, send=0.3, align=b(2), env=SECT)
for k in range(2, 9):
    r, t3, f = CH[k]
    for i in range(16):
        t = b(k, i / 4)
        if 14.82 <= t < 15.0:
            continue
        acc = i % 4 == 0
        osti_va.add(t, (f + '4') if i % 2 == 0 else (r + '4' if r in ('Gb', 'Ab', 'Bb') else r + '4'), 0.1, 92 if acc else 70)
        osti_vc.add(t, r + ('2' if r in ('Bb', 'Ab', 'Gb') else '3'), 0.1, 104 if acc else 76)
trem = Part('violin_trem', 'ViolinEnsTrem', level=-21, pan=-0.35, send=0.5, env=[(12.0, -16), (14.8, 0)] + BREATH[1:] + [(15.0, -60)])
for i, p in enumerate(['Eb5', 'F5', 'Gb5', 'G5', 'Ab5', 'A5']):
    trem.add(12.0 + i * 0.47, [p, n(p) - 12], 0.5, 70 + i * 9)
vln = Part('violins', 'ViolinEnsSusVib', level=-15, pan=-0.35, send=0.45, align=b(7), env=[(b(5), -8), (b(7), 0), (26.9, 0), (FINAL, 2), (28.5, -4), (29.7, -30)])
for k in (5, 6):                                                 # first half: high sustained harmony
    r, t3, f = CH[k]
    vln.add(b(k), [f + '5', t3 + '6' if t3 in ('Db',) else t3 + '5'], 3.05, 96)
for k in (7, 8):                                                 # second half: the theme an octave up
    for beat, p, ln in THEME[k]:
        vln.add(b(k, beat), n(p) + 12, ln * BEAT + 0.03, 122)
vln.add(FINAL, ['D5', 'F5', 'Bb5'], 3.0, 126)

# ======================= choir
choir = Part('choir', ('gm', 52), level=-19, pan=-0.05, send=0.55,
             env=[(6.0, -6), (9.0, -4), (12.0, -3), (14.8, 0)] + BREATH[1:] + [(15.0, 0), (26.9, 0), (FINAL, 2), (28.5, -4), (29.7, -30)])
for k in range(2, 9):
    r, t3, f = CH[k]
    choir.add(b(k), [r + '3', f + '3', t3 + '4', f + '4'], 2.84 if k == 4 else 3.0, 70 if k < 5 else 112)
choir.add(FINAL, ['Bb2', 'F3', 'D4', 'F4', 'Bb4'], 3.0, 124)

# ======================= brass
hn = Part('horns', 'FHornSus', level=-12, pan=-0.15, send=0.45, align=THEME_T,
          env=[(6.0, -14), (12.0, -8), (14.8, -4)] + BREATH[1:] + [(15.0, 0), (26.9, 0), (FINAL, 1), (28.5, -4), (29.7, -30)])
for t, p, d in [(b(3), 'Bb3', 1.5), (b(3, 1.5), 'F4', 2.4)]:      # a hint of the theme
    hn.add(t, p, d * BEAT, 78)
hn.add(b(4), ['C4', 'Eb4'], 2.84, 92)
for k in range(5, 9):                                            # THE THEME, horns in unison (two octaves)
    for beat, p, ln in THEME[k]:
        hn.add(b(k, beat), [p, n(p) - 12], ln * BEAT + 0.03, 124)
hn.add(FINAL, ['Bb2', 'F3', 'Bb3', 'D4', 'F4'], 3.0, 127)
tbn = Part('trombones', 'TromboneSus', level=-13, pan=0.35, send=0.4, align=THEME_T,
           env=[(12.0, -18), (14.8, -2)] + BREATH[1:] + [(15.0, 0), (FINAL, 1), (28.5, -4), (29.7, -30)])
tbn.add(12.0, ['Eb2', 'Ab2', 'Eb3'], 2.84, 118)                   # braam swell
for k in range(5, 9):
    for beat, p, ln in THEME[k]:
        tbn.add(b(k, beat), n(p) - 12, ln * BEAT + 0.03, 122)
tbn.add(FINAL, ['Bb1', 'F2', 'Bb2', 'D3'], 3.0, 127)
tba = Part('tuba', 'TubaSus', level=-16, pan=0.4, send=0.3, align=THEME_T,
           env=[(12.0, -18), (14.8, -2)] + BREATH[1:] + [(15.0, 0), (FINAL, 1), (28.5, -4), (29.7, -30)])
tba.add(12.0, 'Ab1', 2.84, 118)
for k in range(5, 9):
    tba.add(b(k), CH[k][0] + ('2' if CH[k][0] == 'Db' else '1'), 3.05, 120)
tba.add(FINAL, 'Bb1', 3.0, 127)
tpt = Part('trumpets', 'TrumpetSus', level=-13, pan=0.2, send=0.45, align=b(7), env=[(b(7), 0), (FINAL, 2), (28.2, -6), (29.4, -30)])
for k in (7, 8):
    for beat, p, ln in THEME[k]:
        tpt.add(b(k, beat), p if n(p) >= n('E4') else n(p) + 12, ln * BEAT + 0.03, 124)
tpt.add(FINAL, ['F4', 'Bb4', 'D5'], 2.8, 127)

# ======================= drums: half-time epic pattern
DSECT = [(0, 0), (6.0, -1), (9.0, 0), (12.0, 0)] + BREATH + [(26.9, 0)]
kick = Part('kick', 'perc', level=-13, pan=0.0, send=0.25, split=True, env=DSECT)
snare = Part('snare', 'perc', level=-16, pan=-0.05, send=0.3, split=True, env=DSECT)
metal = Part('metal', 'perc', level=-17, pan=0.2, send=0.4, split=True, env=DSECT)
timp = Part('timpani', 'Timpani', level=-14, pan=-0.15, send=0.3, split=True, env=DSECT)
for k in (2, 3):                                                 # the pulse: timpani on 1 and 3
    r = CH[k][0]
    timp.add(b(k, 0), r + '2', 0.6, 96).add(b(k, 2), r + '2', 0.6, 84)
    kick.add(b(k, 0), PERC['bdd'], 0.4, 96)
for i in range(8):                                               # the rise: doubling up into a fill
    kick.add(b(4, i * 0.5), PERC['bdd'], 0.3, 86 + i * 4)
    timp.add(b(4, i * 0.5), ('Ab2' if i % 2 == 0 else 'Eb2'), 0.4, 88 + i * 4)
snare.add(b(4, 2), PERC['sroll'], 1.36, 110)
for k in range(5, 9):
    for beat in (0, 1.5):
        kick.add(b(k, beat), PERC['bd'], 2.0, 127 if beat == 0 else 112)
        kick.add(b(k, beat), PERC['bdd'], 0.4, 124)
    kick.add(b(k, 3.5), PERC['bdd'], 0.4, 104)
    snare.add(b(k, 2), PERC['snare'], 0.5, 127)
    metal.add(b(k, 2), PERC['anvil'] if k % 2 else PERC['brake'], 1.0, 110)
    r, t3, f = CH[k]
    for beat, which, v in [(0, r, 120), (1.5, r, 104), (3, f, 100), (3.25, r, 104), (3.5, f, 108), (3.75, r, 112)]:
        timp.add(b(k, beat), which + '2', 0.4, v)
    metal.add(b(k), PERC['crash'], 3.0, 118 if k in (5, 7) else 96)
kick.add(FINAL, PERC['bd'], 3.0, 127)
snare.add(FINAL, PERC['snare'], 1.0, 127)
timp.add(FINAL, ['F2', 'Bb2'], 2.5, 127)
metal.add(FINAL, PERC['crash'], 3.0, 127).add(FINAL, PERC['anvil'], 1.0, 120).add(FINAL, PERC['brake'], 1.0, 110)
swell = Part('cym_swell', 'perc', level=-22, pan=0.1, send=0.5, thresh=0.001)
swell.add(THEME_T - 3.81, PERC['swell_m'], 3.85, 120).add(FINAL - 1.53, PERC['swell_s'], 1.6, 110)
troll = Part('timp_roll', 'TimpaniRolls', level=-18, pan=-0.15, send=0.35, env=[(25.5, -22), (26.95, 0), (26.99, -60)])
troll.add(25.5, 'F2', 1.5, 110)
bells = Part('bells', 'TubularBells', level=-22, pan=0.2, send=0.5, split=True)
bells.add(THEME_T, ['F4', 'Bb4'], 3.0, 110).add(FINAL, ['F4', 'Bb4', 'D5'], 4.0, 122)

PARTS = [mech, boom, braam_t, braam_u, gong, cel, harp, preview, pad, vc_pad, cb_pad, osti_va, osti_vc, trem, vln, choir,
         hn, tbn, tba, tpt, kick, snare, metal, timp, swell, troll, bells]
ACCENTS = [2.95, b(2), THEME_T, b(7), FINAL]

if __name__ == '__main__':
    out = sys.argv[1]
    y, rep = build('TAGS_theme', PARTS, LEN, os.path.join(out, 'build'), reverb=(75, 40, 100, 100, 25, 0), wet=0.32,
                   fade=(28.6, 29.95))
    wav, ogg = export(y, out, 'TAGS_theme')
    save_score(PARTS, os.path.join(out, 'TAGS_theme.mid'))
    y = decode(ogg)
    rep['length_samples'] = len(y)
    rep['ogg_peak_dbfs'] = round(ogg_peak_db(ogg), 2)
    rep['accents'] = {str(round(t, 2)): round(accent_time(y, t), 4) for t in ACCENTS}
    json.dump(rep, open(os.path.join(out, 'TAGS_theme_report.json'), 'w'), indent=1)
    print(json.dumps(rep['accents']))
