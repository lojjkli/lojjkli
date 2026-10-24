"""TAGS_ident - studio logo, exactly 10.1 s. A dark, secret-agent movie-studio
intro in E minor, built on the "agent" motif E-G-F#-D# (minor with a major 7th).
0       a deep boom (bass drum, timpani, low harp) opens the curtain
0-2.3   low tremolo rumble, gong scrape, a muted shimmer; horns state the
        motif softly
2.3-5.3 the rise: string tremolos climb chromatically, a timpani/bass-drum
        heartbeat speeds up, snare and timpani rolls, cymbal swell, and the
        motif returns fortissimo in trumpets, horns and trombones
5.3     the logo: a massive E minor (major 7th) hit - full brass, strings,
        timpani, bass drum, gong, crash, tubular bells - that keeps ringing
5.55 6.1 6.55 7.2 7.75  trailer impacts over the held chord (timpani, drums,
        staccato brass, snare); 7.75 is the biggest
then the chord rings out and fades to silence by 10.1 s."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orch import Part, PERC, build, export, save_score, accent_time, decode, ogg_peak_db, n

T_HIT = 5.3
FW = [5.55, 6.10, 6.55, 7.20, 7.75]
LEN = 10.1
MOTIF = ['E', 'G', 'F#', 'D#']
BEAT = [2.30, 3.30, 3.90, 4.35, 4.68, 4.93, 5.10]       # accelerating heartbeat into the hit
# the held hit: swells a little at the last impact, then rings out
HOLD = [(T_HIT, 0), (5.45, -4), (5.85, -9), (7.6, -11), (7.8, -9), (8.8, -15), (9.9, -45)]
THOLD = [(T_HIT, 0), (5.45, -6), (5.85, -14), (7.6, -16), (7.8, -13), (8.6, -22), (9.5, -50)]   # trumpets drop further

# ---- opening boom, heartbeat and impacts
timp = Part('timpani', 'Timpani', level=-14, pan=-0.1, send=0.35, split=True)
timp.add(0.05, ['E2', 'B2'], 2.0, 124)
for i, t in enumerate(BEAT):
    timp.add(t, 'E2', 0.5, 70 + i * 7)
timp.add(T_HIT, ['E2', 'B2'], 2.0, 127)
for t, ps, v in zip(FW, [['B2'], ['E2', 'B2'], ['G2'], ['A2'], ['E2', 'B2']], [100, 114, 102, 96, 112]):
    timp.add(t, ps, 1.5, v)
troll = Part('timp_roll', 'TimpaniRolls', level=-18, pan=-0.1, send=0.35, env=[(3.9, -24), (5.16, 0), (5.21, -60)])
troll.add(3.90, 'E2', 1.4, 110)

drums = Part('drums', 'perc', level=-15, pan=0.0, send=0.4, split=True)
drums.add(0.05, PERC['bd'], 3.0, 124)
for i, t in enumerate(BEAT[1:]):
    drums.add(t, PERC['bd'], 1.5, 60 + i * 9)
drums.add(T_HIT, PERC['bd'], 3.0, 127)
for t, v in zip(FW, [92, 112, 96, 92, 112]):
    drums.add(t, PERC['bd'], 2.0, v)

metal = Part('metal', 'perc', level=-19, pan=0.15, send=0.5, align=T_HIT)
metal.add(0.05, PERC['gscrape'], 4.0, 60).add(0.4, PERC['bow'], 5.0, 100)
metal.add(T_HIT - 3.81, PERC['swell_m'], 4.0, 120)         # cymbal roll peaking on the hit
metal.add(T_HIT, PERC['crash'], 4.0, 127).add(T_HIT, PERC['gong'], 5.0, 127)
metal.add(6.10, PERC['crash'], 3.0, 90).add(7.75, PERC['crash'], 3.0, 104).add(7.75, PERC['gong'], 4.0, 70)

snare = Part('snare', 'perc', level=-20, pan=-0.05, send=0.35, split=True,
             env=[(0, 0), (4.4, -14), (5.16, 0), (5.21, -60), (5.28, -60), (5.285, 0)])
snare.add(4.40, PERC['sroll'], 0.87, 110)
snare.add(T_HIT, PERC['snare'], 1.0, 127)
for t, v in zip(FW, [114, 104, 114, 102, 116]):
    snare.add(t, PERC['snare'], 1.0, v)

bells = Part('bells', 'TubularBells', level=-20, pan=0.25, send=0.5, split=True)
bells.add(T_HIT, ['E4', 'B4'], 4.5, 124).add(7.75, ['E4'], 3.0, 96)

harp = Part('harp', 'Harp', level=-20, pan=-0.5, send=0.4, split=True)
harp.add(0.05, ['E1', 'E2', 'B2'], 2.0, 124)
up = [p for p in range(n('E3'), n('E7') + 1) if (p - n('E3')) % 12 in (0, 2, 3, 5, 7, 8, 11)]
for i, p in enumerate(up):                                 # sweep up into the hit
    harp.add(4.30 + 0.80 * (i / (len(up) - 1)) ** 0.8, p, 0.4, 70 + i * 2)
harp.add(T_HIT, ['E1', 'E2', 'B2', 'E3'], 3.0, 124).add(7.75, ['E1', 'E2', 'B2'], 2.0, 100)

# ---- strings: rumble, climbing tremolos, then the held chord
cb_trem = Part('bass_trem', 'ContrabassTrem', level=-17, pan=0.4, send=0.3,
               env=[(0, -3), (2.3, -4), (5.16, 0), (5.21, -60)])
cb_trem.add(0.0, 'E1', 5.35, 100)
vc_trem = Part('cello_trem', 'CelloEnsTrem', level=-18, pan=0.3, send=0.35,
               env=[(0, -4), (2.3, -5), (5.16, 0), (5.21, -60)])
vc_trem.add(0.0, ['E2', 'B2'], 5.35, 96)
vla_trem = Part('viola_trem', 'ViolaEnsTrem', level=-23, pan=0.15, send=0.4, env=[(2.3, -14), (5.16, 0), (5.21, -60)])
for k, p in enumerate(['B3', 'C4', 'C#4', 'D4', 'D#4', 'E4']):
    vla_trem.add(2.30 + k * 0.5, p, 0.56, 60 + k * 10)
vln_trem = Part('violin_trem', 'ViolinEnsTrem', level=-20, pan=-0.35, send=0.45,
                env=[(0, -12), (2.0, -10), (2.3, -12), (5.16, 0), (5.21, -60)])
vln_trem.add(0.0, 'B5', 2.4, 40)
for k, p in enumerate(['E5', 'F5', 'F#5', 'G5', 'G#5', 'A5']):
    vln_trem.add(2.30 + k * 0.5, [p, n(p) - 12], 0.56, 60 + k * 10)

vln = Part('violins', 'ViolinEnsSusVib', level=-14, pan=-0.35, send=0.4, align=T_HIT, env=HOLD)
vln.add(T_HIT, ['E5', 'G5', 'B5'], 4.6, 124)
vla = Part('violas', 'ViolaEnsSusVib', level=-18, pan=0.15, send=0.4, align=T_HIT, env=HOLD)
vla.add(T_HIT, ['D#4', 'G4', 'B4'], 4.6, 120)
vc = Part('cellos', 'CelloEnsSusVib', level=-14, pan=0.3, send=0.35, align=T_HIT, env=HOLD)
vc.add(T_HIT, ['E2', 'B2', 'E3'], 4.6, 124)
cb = Part('basses', 'ContrabassSusVB', level=-18, pan=0.4, send=0.3, align=T_HIT, env=HOLD)
cb.add(T_HIT, 'E1', 4.6, 124)

# ---- winds
fl = Part('flute', 'FluteSusVib', level=-23, pan=-0.1, send=0.45, align=T_HIT, env=HOLD)
fl.add(T_HIT, 'B5', 4.0, 112)
cl = Part('clarinet', 'ClarinetSus', level=-24, pan=0.15, send=0.4, align=T_HIT, env=HOLD)
cl.add(T_HIT, 'D#5', 4.0, 110)
bsn = Part('bassoon', 'BassoonSus', level=-23, pan=0.25, send=0.35, align=T_HIT, env=HOLD)
bsn.add(T_HIT, 'E2', 4.0, 110)

# ---- brass: the motif (soft, then fortissimo), the held hit, the impacts
hn_soft = Part('horns_soft', 'FHornSus', level=-13, pan=-0.15, send=0.5, env=[(0.4, -4), (1.6, 0), (2.4, -2)])
for (t, d), p, v in zip([(0.45, 0.48), (0.95, 0.42), (1.38, 0.42), (1.80, 0.6)], MOTIF, [62, 66, 64, 70]):
    hn_soft.add(t, p + '4', d, v)
hn_soft.add(2.42, 'E4', 0.9, 60)
MOT_T = [(3.30, 0.42), (3.72, 0.38), (4.10, 0.38), (4.48, 0.70)]
hn = Part('horns', 'FHornSus', level=-11, pan=-0.15, send=0.45, align=T_HIT,
          env=[(3.3, -5), (4.5, -2), (5.16, 0), (5.21, -60), (5.27, -60), (5.275, 0)] + HOLD)
for (t, d), p, v in zip(MOT_T, MOTIF, [100, 104, 108, 114]):
    hn.add(t, [p + '3', p + '4'], d, v)
hn.add(T_HIT, ['E3', 'B3', 'E4', 'G4'], 4.2, 124)
tpt = Part('trumpets', 'TrumpetSus', level=-12, pan=0.2, send=0.45, align=T_HIT,
           env=[(3.3, -5), (4.5, -2), (5.16, 0), (5.21, -60), (5.27, -60), (5.275, 0)] + THOLD)
for (t, d), p, v in zip(MOT_T, MOTIF, [100, 104, 108, 114]):
    tpt.add(t, p + '5', d, v)
tpt.add(T_HIT, ['G4', 'B4', 'D#5'], 3.4, 126)
tbn = Part('trombones', 'TromboneSus', level=-12, pan=0.35, send=0.4, align=T_HIT,
           env=[(2.3, -14), (3.3, -5), (4.5, -2), (5.16, 0), (5.21, -60), (5.27, -60), (5.275, 0)] + HOLD)
tbn.add(2.30, ['E2', 'B2'], 0.98, 80)
for (t, d), p, v in zip(MOT_T, MOTIF, [100, 104, 108, 114]):
    tbn.add(t, p + '3', d, v)
tbn.add(T_HIT, ['E2', 'B2', 'E3', 'G3'], 4.2, 126)
tba = Part('tuba', 'TubaSus', level=-15, pan=0.4, send=0.3, align=T_HIT, env=[(2.3, -12), (5.16, 0), (5.21, -60), (5.27, -60), (5.275, 0)] + HOLD)
tba.add(2.30, 'E2', 2.9, 90).add(T_HIT, 'E2', 4.2, 124)

tpt_st = Part('trumpet_stac', 'TrumpetStac', level=-13, pan=0.2, send=0.4, split=True, thresh=0.6)
tpt_st.add(5.55, ['B4', 'D#5'], 0.15, 116).add(6.55, ['G4', 'B4', 'E5'], 0.15, 112).add(7.20, ['D#5', 'F#5'], 0.15, 102)
tpt_st.add(7.75, ['E4', 'B4', 'E5'], 0.25, 110)
tbn_st = Part('trombone_stac', 'TromboneStac', level=-13, pan=0.35, send=0.35, split=True, thresh=0.6)
tbn_st.add(6.10, ['E2', 'B2', 'E3'], 0.25, 118).add(7.20, ['A2', 'C3'], 0.2, 100).add(7.75, ['E2', 'B2', 'E3'], 0.3, 114)
tba_st = Part('tuba_stac', 'TubaStac', level=-18, pan=0.4, send=0.3, split=True, thresh=0.6)
tba_st.add(6.10, 'E2', 0.25, 116).add(7.75, 'E2', 0.3, 114)
hn_st = Part('horn_stac', 'FHornStac', level=-14, pan=-0.15, send=0.4, split=True, thresh=0.6)
hn_st.add(5.55, ['B3', 'D#4'], 0.2, 110).add(6.55, ['G3', 'B3', 'E4'], 0.2, 114).add(7.75, ['E3', 'B3', 'E4'], 0.3, 112)

PARTS = [timp, troll, drums, metal, snare, bells, harp, cb_trem, vc_trem, vla_trem, vln_trem, vln, vla, vc, cb,
         fl, cl, bsn, hn_soft, hn, tpt, tbn, tba, tpt_st, tbn_st, tba_st, hn_st]

if __name__ == '__main__':
    out = sys.argv[1]
    y, rep = build('TAGS_ident', PARTS, LEN, os.path.join(out, 'build'), reverb=(75, 40, 100, 100, 25, 0), wet=0.34,
                   fade=(8.9, 10.05))
    wav, ogg = export(y, out, 'TAGS_ident')
    save_score(PARTS, os.path.join(out, 'TAGS_ident.mid'))
    y = decode(ogg)                         # measure on the delivered file
    rep['length_samples'] = len(y)
    rep['ogg_peak_dbfs'] = round(ogg_peak_db(ogg), 2)
    rep['accents'] = {str(t): round(accent_time(y, t), 4) for t in [T_HIT] + FW}
    json.dump(rep, open(os.path.join(out, 'TAGS_ident_report.json'), 'w'), indent=1)
    print(json.dumps(rep['accents']))
