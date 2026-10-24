"""TAGS_ident - studio logo, exactly 10.1 s. Secret-agent version, E minor,
120 bpm grid (8ths every 0.25 s, offset so 5.3 s falls on a beat).
0-2.3   in the shadows: creeping pizzicato bass riff, ticking snare taps,
        a B/C tremolo cluster high in the violins, a muted trumpet whispers
        the motif (B-C-B), a celesta glint
2.3-5.3 the agent moves in: cellos join the riff, violin tremolo creeps up
        chromatically, muted horn stabs Em(maj7) -> F#m7b5 -> B7, the bass
        riff turns into 16ths, snare + timpani rolls and a cymbal swell,
        harp swish into the hit
5.3     reveal: full-orchestra E minor (major 7th) stinger, timpani, bass drum,
        crash, snare and a low tubular bell
5.55 6.1 6.55 7.2 7.75  gadget stabs: staccato brass, pizzicato, claves, snare
then low tremolo, the whispered motif once more, a last low pizzicato E, fade."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orch import Part, PERC, build, export, save_score, spectral_flux_onset, accent_time, decode, ogg_peak_db, n

T_HIT = 5.3
FW = [5.55, 6.10, 6.55, 7.20, 7.75]
LEN = 10.1


def duck(hits, hold=0.14, fall=0.1, depth=-16, start=0.0):
    """Gain envelope that lets each hit ring briefly, then damps it (a muted
    pizzicato / a hand on the timpani) so the next stab is heard clearly."""
    env = [(start, 0)]
    for i, t in enumerate(hits):
        env += [(t - 0.006, depth if i else 0), (t - 0.004, 0), (t + hold, 0), (t + hold + fall, depth)]
    return env


def g(k):
    """8th-note grid: g(21) == 5.3."""
    return 0.05 + 0.25 * k


# ---- the creeping riff (bass pizzicato), 16 eighths, then 16ths into the hit
RIFF = [(0, 'E2', 96), (2, 'E2', 70), (3, 'G2', 64), (5, 'F#2', 78), (6, 'E2', 66), (7, 'B1', 84),
        (8, 'E2', 96), (10, 'E2', 70), (11, 'G2', 66), (13, 'A2', 82), (14, 'A#2', 86), (15, 'B2', 92)]
cb_pz = Part('bass_pizz', 'ContrabassPizz', level=-21, pan=0.3, send=0.25, env=[(4.95, 0), (5.12, -36)])
for k, p, v in RIFF:
    cb_pz.add(g(k), p, 0.2, v)
for i in range(8):                                     # 16ths 4.05 -> 4.93, getting louder, then a breath
    cb_pz.add(g(16) + i * 0.125, 'E2' if i % 2 == 0 else 'E3', 0.1, 70 + i * 6)
cb_hit = Part('bass_pizz_hits', 'ContrabassPizz', level=-17, pan=0.3, send=0.25, split=True, env=duck([T_HIT, 7.75, 9.30]))
cb_hit.add(T_HIT, 'E1', 0.6, 127).add(7.75, 'E1', 0.6, 100).add(9.30, 'E1', 0.8, 84)
vc_pz = Part('cello_pizz', 'CelloEnsPizz', level=-20, pan=0.15, send=0.25, env=[(4.95, 0), (5.12, -36)])
for k, p, v in RIFF[6:]:
    vc_pz.add(g(k), n(p) + 12, 0.2, v - 6)
for i in range(8):
    vc_pz.add(g(16) + i * 0.125, 'E3', 0.1, 66 + i * 6)
vc_hit = Part('cello_pizz_hits', 'CelloEnsPizz', level=-20, pan=0.15, send=0.25, split=True, env=duck([T_HIT, 6.55, 7.75, 9.30]))
vc_hit.add(T_HIT, ['E2', 'B2'], 0.6, 124).add(6.55, 'G3', 0.3, 100).add(7.75, 'E2', 0.6, 100).add(9.30, 'E2', 0.8, 74)
vn_pz = Part('violin_pizz', 'ViolinEnsPizz', level=-20, pan=-0.35, send=0.35, split=True, thresh=0.6)
vn_pz.add(5.55, ['D#5', 'B5'], 0.3, 104).add(6.55, ['G5', 'B5'], 0.3, 100).add(7.20, ['B4', 'F#5'], 0.3, 96)

# ---- snare: taps ticking on the off-beats, roll into the hit, hits on the stabs
snare = Part('snare', 'perc', level=-22, pan=-0.05, send=0.3, align=T_HIT,
             env=[(0, -6), (2.3, -4), (4.25, -12), (4.98, 0), (5.06, -60), (5.29, -60), (5.295, 0)])
for k in range(0, 17):
    snare.add(g(k) + 0.125, PERC['taps'], 0.1, 34 + (k % 4 == 3) * 14)
for k in range(9, 16):                                   # extra 16th ticks as it tightens
    snare.add(g(k), PERC['taps'], 0.1, 28)
snare.add(4.25, PERC['sroll'], 1.02, 100)
snare.add(T_HIT, PERC['snare'], 1.0, 120).add(5.55, PERC['snare'], 1.0, 96).add(6.10, PERC['snare'], 1.0, 100).add(7.20, PERC['snare'], 1.0, 92)
snare.add(7.75, PERC['snare'], 1.0, 90).add(9.30, PERC['taps'], 0.1, 60)

perc = Part('perc', 'perc', level=-20, pan=0.1, send=0.4, align=T_HIT)
perc.add(T_HIT - 1.53, PERC['swell_s'], 1.8, 110)                    # short cymbal roll peaking at the hit
perc.add(T_HIT, PERC['crash'], 3.0, 120).add(T_HIT, PERC['bd'], 2.0, 124)
perc.add(5.55, PERC['claves'], 0.5, 100).add(6.55, PERC['claves'], 0.5, 92)
perc.add(7.75, PERC['cym'], 2.0, 50)

timp = Part('timpani', 'Timpani', level=-17, pan=-0.1, send=0.3, split=True, env=duck([T_HIT, 6.10, 7.75], hold=0.18, depth=-12, start=0.0))
timp.add(g(0), 'E2', 1.0, 54).add(g(8), 'E2', 1.0, 60)
timp.add(T_HIT, ['E2', 'B2'], 2.0, 127).add(6.10, 'E2', 1.0, 86).add(7.75, 'E2', 1.5, 88)
troll = Part('timp_roll', 'TimpaniRolls', level=-21, pan=-0.1, send=0.3, env=[(4.3, -24), (4.98, -2), (5.06, -60)])
troll.add(4.30, 'E2', 1.0, 100)

bells = Part('bell', 'TubularBells', level=-25, pan=0.25, send=0.45, align=T_HIT, env=[(T_HIT, 0), (5.45, 0), (5.52, -10)])
bells.add(T_HIT, 'E4', 4.0, 110)

cel = Part('celesta', ('gm', 8), level=-26, pan=-0.3, send=0.5)
cel.add(0.30, 'E7', 0.6, 52).add(1.55, 'D#7', 0.6, 48).add(2.80, 'B6', 0.6, 52).add(3.80, 'G7', 0.6, 56)
cel.add(6.55, 'B6', 0.5, 80).add(7.20, 'F#7', 0.5, 80).add(9.30, 'E7', 0.8, 58)

harp = Part('harp', 'Harp', level=-21, pan=-0.5, send=0.4, align=T_HIT)
swish = [p for p in range(n('E3'), n('E6') + 1) if (p - n('E3')) % 12 in (0, 2, 3, 5, 7, 8, 11)]
for i, p in enumerate(swish):                       # quick swish up, done before the breath
    harp.add(4.55 + i * 0.4 / len(swish), p, 0.3, 66 + i * 2)
harp.add(T_HIT, ['E1', 'E2', 'B2'], 2.0, 124).add(7.75, ['E1', 'E2'], 1.5, 90)

# ---- strings (arco)
vtrem = Part('vln_trem', 'ViolinEnsTrem', level=-23, pan=-0.35, send=0.45, align=None,
             env=[(0, -12), (1.5, -8), (2.3, -8), (4.98, 0), (5.06, -60), (7.9, -60), (8.3, -16), (9.6, -30)])
vtrem.add(0.05, ['B5', 'C6'], 2.4, 40)                               # cluster: B against C
for k, p in enumerate(['E5', 'F5', 'F#5', 'G5', 'G#5', 'A5']):        # chromatic creep upward
    vtrem.add(2.30 + k * 0.5, [p, n(p) - 12], 0.55, 50 + k * 10)
vtrem.add(7.95, ['B5', 'C6'], 1.8, 40)
vla_trem = Part('viola_trem', 'ViolaEnsTrem', level=-24, pan=0.15, send=0.4,
                env=[(2.3, -10), (4.98, 0), (5.06, -60)])
for k, p in enumerate(['B3', 'C4', 'C#4', 'D4', 'D#4', 'E4']):
    vla_trem.add(2.30 + k * 0.5, p, 0.55, 50 + k * 10)
low_trem = Part('low_trem', 'CelloEnsTrem', level=-23, pan=0.3, send=0.35, align=T_HIT,
                env=[(T_HIT, -6), (5.8, -14), (7.7, -10), (8.0, -12), (9.7, -36)])
low_trem.add(T_HIT, ['E2', 'B2'], 4.5, 90)
cb_trem = Part('bass_trem', 'ContrabassTrem', level=-24, pan=0.4, send=0.3, align=T_HIT,
               env=[(T_HIT, -6), (5.8, -14), (7.7, -10), (8.0, -12), (9.7, -36)])
cb_trem.add(T_HIT, 'E1', 4.5, 90)
vln = Part('violins', 'ViolinEnsSusVib', level=-17, pan=-0.35, send=0.4, align=T_HIT, env=[(T_HIT, 0), (5.38, -2), (5.5, -12), (5.85, -20), (6.4, -50)])
vln.add(T_HIT, ['E5', 'G5', 'B5'], 1.0, 120)
vla = Part('violas', 'ViolaEnsSusVib', level=-21, pan=0.15, send=0.4, align=T_HIT, env=[(T_HIT, 0), (5.38, -2), (5.5, -12), (5.85, -20), (6.4, -50)])
vla.add(T_HIT, ['D#4', 'G4', 'B4'], 1.0, 118)

# ---- winds
cl = Part('clarinet', 'ClarinetSus', level=-25, pan=0.15, send=0.4, align=T_HIT, env=[(T_HIT, 0), (5.38, -2), (5.5, -12), (5.85, -20), (6.4, -50)])
cl.add(T_HIT, 'D#5', 1.0, 110)
cl_st = Part('clarinet_stac', 'ClarinetStac', level=-27, pan=0.15, send=0.4, split=True, thresh=0.6)
cl_st.add(7.20, ['B4', 'F#5'], 0.2, 100)

# ---- brass
mtpt = Part('muted_trumpet', 'TrumpetStraightMuteSus', level=-30, pan=0.25, send=0.5)
for t, p, d, v in [(0.80, 'B4', .30, 64), (1.10, 'C5', .22, 60), (1.32, 'B4', .70, 56),
                   (2.05, 'E5', .28, 66), (2.33, 'D#5', .80, 60),
                   (8.30, 'B4', .30, 56), (8.60, 'C5', .22, 52), (8.82, 'B4', .80, 48)]:
    mtpt.add(t, p, d, v)
mhn = Part('muted_horns', 'FHornMute', level=-20, pan=-0.15, send=0.45, align=3.30, env=[(3.3, -3), (4.8, 0), (5.0, 0), (5.08, -60)])
mhn.add(3.30, ['E3', 'G3', 'B3', 'D#4'], 0.42, 96).add(4.30, ['F#3', 'A3', 'C4', 'E4'], 0.42, 106)
mhn.add(4.80, ['B3', 'D#4', 'F#4', 'A4'], 0.22, 116)
hn = Part('horns', 'FHornSus', level=-14, pan=-0.15, send=0.45, align=T_HIT, env=[(T_HIT, 0), (5.38, -2), (5.5, -12), (5.85, -20), (6.4, -50)])
hn.add(T_HIT, ['E3', 'B3', 'E4', 'G4'], 1.1, 122)
tpt = Part('trumpets', 'TrumpetSus', level=-15, pan=0.2, send=0.45, align=T_HIT, env=[(T_HIT, 0), (5.38, -2), (5.5, -12), (5.85, -20), (6.4, -50)])
tpt.add(T_HIT, ['G4', 'B4', 'D#5'], 0.9, 124)
tbn = Part('trombones', 'TromboneSus', level=-16, pan=0.35, send=0.4, align=T_HIT, env=[(T_HIT, 0), (5.38, -2), (5.5, -12), (5.85, -20), (6.4, -50)])
tbn.add(T_HIT, ['E2', 'B2', 'E3', 'G3'], 1.1, 122)
tba = Part('tuba', 'TubaSus', level=-21, pan=0.4, send=0.3, align=T_HIT, env=[(T_HIT, 0), (5.38, -2), (5.5, -12), (5.85, -20), (6.4, -50)])
tba.add(T_HIT, 'E2', 1.1, 120)
# gadget stabs
tpt_st = Part('trumpet_stac', 'TrumpetStac', level=-16, pan=0.2, send=0.4, split=True, thresh=0.6)
tpt_st.add(5.55, ['B4', 'D#5'], 0.15, 112).add(7.20, ['B4', 'F#5'], 0.15, 104).add(7.75, ['E4', 'B4', 'E5'], 0.2, 92)
tbn_st = Part('trombone_stac', 'TromboneStac', level=-19, pan=0.35, send=0.35, split=True, thresh=0.6)
tbn_st.add(6.10, ['E3', 'B3'], 0.2, 112).add(7.75, ['E2', 'B2', 'E3'], 0.25, 90)
tba_st = Part('tuba_stac', 'TubaStac', level=-21, pan=0.4, send=0.3, split=True, thresh=0.6)
tba_st.add(6.10, 'E2', 0.2, 112).add(7.75, 'E2', 0.25, 90)
hn_st = Part('horn_stac', 'FHornStac', level=-20, pan=-0.15, send=0.4, split=True, thresh=0.6)
hn_st.add(6.55, ['G3', 'B3', 'D#4'], 0.2, 108).add(7.75, ['E3', 'B3', 'E4'], 0.25, 92)

PARTS = [cb_pz, cb_hit, vc_pz, vc_hit, vn_pz, snare, perc, timp, troll, bells, cel, harp, vtrem, vla_trem, low_trem, cb_trem, vln, vla,
         cl, cl_st, mtpt, mhn, hn, tpt, tbn, tba, tpt_st, tbn_st, tba_st, hn_st]

if __name__ == '__main__':
    out = sys.argv[1]
    y, rep = build('TAGS_ident', PARTS, LEN, os.path.join(out, 'build'), reverb=(55, 50, 85, 100, 15, 0), wet=0.28,
                   fade=(8.9, 10.05))
    wav, ogg = export(y, out, 'TAGS_ident')
    save_score(PARTS, os.path.join(out, 'TAGS_ident.mid'))
    y = decode(ogg)                         # measure on the delivered file
    rep['length_samples'] = len(y)
    rep['ogg_peak_dbfs'] = round(ogg_peak_db(ogg), 2)
    rep['accents'] = {str(t): round(accent_time(y, t), 4) for t in [T_HIT] + FW}
    json.dump(rep, open(os.path.join(out, 'TAGS_ident_report.json'), 'w'), indent=1)
    print(json.dumps(rep['accents']))
