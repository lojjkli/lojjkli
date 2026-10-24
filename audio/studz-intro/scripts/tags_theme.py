"""TAGS_theme - 10.0 s dark studio intro made only from real
metal recordings (VSCO-2 CE gong, bowed and scraped cymbal, bass-drum rubs,
brake drum, anvil, ratchet), slowed down 2-8x with sliding playback speed so
they become giant metal roars, groans and screeches. No melody, no beat.

The shape follows measurements of the Paramount logo sequence of a robot-action
film (loudness every 0.25 s, brightness, where the energy sits), not its audio:
0.0-1.0 silence | 1.0-1.5 fast swell into a deep metal roar | 2.6 the biggest
hit with a rising screech | 3.7-4.7 two metal groans (about 240 and 285 Hz) with
clangs at 4.0 and 4.4 | 5.0-5.5 dip | 5.4-6.6 swell with faint mechanical clicks |
7.0-7.5 dip | 8.0 deep hit with a falling groan | 8.2-9.9 dark tail into silence."""
import sys, os, json
import numpy as np, soundfile as sf
from scipy import signal as ss
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orch import SR, VSCO, sox_reverb, master, export, decode, ogg_peak_db, accent_time

LEN = 10.0
HIT1, GROAN, HIT2 = 2.6, 3.7, 8.0
PERC_DIR = os.path.join(VSCO, 'Percussion')
N = int(LEN * SR)
mix = np.zeros((N + 8 * SR, 2))
send = np.zeros_like(mix)
LAYERS = []


def load(name):
    x, sr = sf.read(os.path.join(PERC_DIR, name), always_2d=True)
    assert sr == SR
    return np.repeat(x, 2, axis=1) if x.shape[1] == 1 else x[:, :2]


def vari(x, rate, start=0.0, length=None):
    """Play x at a time-varying speed. rate: list of (t, speed) over the output
    time (speed 0.25 = two octaves down and four times longer)."""
    length = length or 12.0
    t = np.arange(int(length * SR)) / SR
    r = np.interp(t, [p[0] for p in rate], [p[1] for p in rate])
    pos = start * SR + np.concatenate([[0], np.cumsum(r)[:-1]])
    k = pos < len(x) - 2
    pos = pos[k]
    i = pos.astype(int); f = (pos - i)[:, None]
    return x[i] * (1 - f) + x[i + 1] * f


def shape(y, pts):
    """dB envelope over the layer's own time."""
    t = np.arange(len(y)) / SR
    return y * (10 ** (np.interp(t, [p[0] for p in pts], [p[1] for p in pts]) / 20))[:, None]


def filt(y, lo=None, hi=None, order=4):
    if lo:
        y = ss.sosfiltfilt(ss.butter(order, lo, 'high', fs=SR, output='sos'), y, axis=0)
    if hi:
        y = ss.sosfiltfilt(ss.butter(order, hi, 'low', fs=SR, output='sos'), y, axis=0)
    return y


def place(name, t, y, db, pan=0.0, wet=0.3, width=1.0):
    """Normalize the layer to its loudest 100 ms RMS, set it to `db`, pan, add."""
    f = min(len(y), int(0.3 * SR))                              # never cut a ringing layer off dead
    y = y.copy(); y[-f:] *= np.linspace(1, 0, f)[:, None]
    k = int(0.1 * SR)
    rms = np.sqrt(np.convolve((y ** 2).mean(axis=1), np.ones(k) / k, 'same')).max()
    y = y / max(rms, 1e-9) * 10 ** (db / 20)
    mid, side = (y[:, 0] + y[:, 1]) / 2, (y[:, 0] - y[:, 1]) / 2 * width
    a = (pan + 1) * np.pi / 4
    y = np.stack([(mid + side) * np.cos(a), (mid - side) * np.sin(a)], axis=1) * np.sqrt(2)
    i = int(round(t * SR))
    e = min(len(mix), i + len(y))
    mix[i:e] += y[:e - i]
    send[i:e] += y[:e - i] * wet
    LAYERS.append(dict(name=name, t=t, db=db, sec=round(len(y) / SR, 2)))


gong_fff, gong_f, gong_mf = load('gongHit_fff.wav'), load('gongHit_f.wav'), load('gongHit_mf.wav')
scrape = load('gongscrape_pp.wav')
bow1, bow3, bow4 = load('susCymb1-bow-1.wav'), load('susCymb1-bow-3.wav'), load('susCymb1-bow-4.wav')
rub2, rub4 = load('bassdrum_rub2_v1.wav'), load('bassdrum_rub4_v1.wav')
brake, anvil = load('BrakeDrum1_Hammer_v3_Sum.wav'), load('Anvil_Hit1_v3_Sum.wav')
ratchet, bd = load('Ratchet1-Slow_v1_rr1_Sum.wav'), load('BDrumNewhit_v7_rr1_Sum.wav')

# ---- the body: a deep metal roar under everything (gongs slowed 3-4x, a bass-drum rub slowed 2x)
START = 1.2                                                     # the roar fades in from here
BODY = [(START, -60), (START + 0.25, -10), (START + 0.4, -2), (2.4, -2), (2.6, -2), (2.7, -4), (2.7, -4), (3.4, -6), (3.7, -13), (4.0, -6), (5.0, -8),
        (5.5, -9), (6.6, -2), (6.85, -3), (7.05, -8), (7.5, -9), (8.0, -3), (8.15, -14), (8.5, -16), (8.8, -14), (9.0, -15), (9.4, -30), (9.6, -80)]
body_t = lambda pts: [(t - START, d) for t, d in pts]            # absolute times -> layer time
place('roar_gong_fff/4', START, filt(shape(vari(gong_fff, [(0, .25), (1.5, .26), (3, .22), (5.5, .24), (8.6, .2)], start=0.02, length=8.7),
                                        body_t(BODY)), lo=30, hi=900), -20, wet=0.25)
place('roar_gong_f/3', START, filt(shape(vari(gong_f, [(0, .34), (2, .32), (4, .35), (8.6, .3)], length=8.7), body_t(BODY)), lo=25, hi=500),
      -21, pan=0.1, wet=0.2)
place('growl_rub4/2', START, filt(shape(vari(rub4, [(0, .55), (1.0, .5), (2.0, .62), (3.0, .48), (6.0, .55), (8.6, .45)], length=8.7),
                                      body_t(BODY)), lo=25, hi=700), -22, pan=-0.15, wet=0.15)

# ---- 2.6 s: the biggest hit (fresh gong strike 2x down, slowed brake drum and anvil, a slowed kick)
place('hit1_gong/2', HIT1, filt(shape(vari(gong_fff, [(0, .5), (3, .45)], length=3.0), [(0, 0), (0.8, -10), (2.5, -40)]), lo=30, hi=1500), -10, wet=0.4)
place('hit1_brake/4', HIT1, filt(vari(brake, [(0, .25)], length=3), hi=2500), -19, pan=0.2, wet=0.5)
place('hit1_anvil/6', HIT1 + 0.01, filt(vari(anvil, [(0, .16)], length=3), lo=200, hi=3000), -23, pan=-0.25, wet=0.5)
place('hit1_kick/2', HIT1, filt(vari(bd, [(0, .5)], length=3), hi=300), -13, wet=0.1)
# the screech: bowed cymbal slowed 2x, its speed rising (a metal scream sliding up 1.4-2.0 and 2.4-3.5)
place('screech_fall', 1.4, filt(shape(vari(bow4, [(0, .9), (0.6, .6)], start=1.0, length=0.7), [(0, -30), (0.2, 0), (0.5, -3), (0.7, -40)]), lo=250, hi=3500),
      -30, pan=-0.3, wet=0.5)
place('screech_rise', 2.4, filt(shape(vari(bow3, [(0, .45), (1.1, .75)], start=1.5, length=1.15), [(0, -24), (0.25, 0), (0.8, -2), (1.15, -40)]), lo=250, hi=3500),
      -27, pan=0.3, wet=0.5)

# ---- 3.7-4.7 s: two metal groans (bowed cymbal 2x down, ~240 and ~285 Hz), clangs at 4.0 and 4.4
wob = lambda base: [(i * 0.1, base * (1 + 0.006 * np.sin(i * 1.7))) for i in range(13)]
place('groan_240', GROAN, filt(shape(vari(bow4, wob(0.43), start=1.0, length=1.2), [(0, -30), (0.25, 0), (0.9, 0), (1.2, -40)]), lo=150, hi=2000),
      -25, pan=-0.2, wet=0.45)
place('groan_285', GROAN + 0.1, filt(shape(vari(bow1, wob(0.505), start=2.0, length=1.1), [(0, -30), (0.25, 0), (0.8, 0), (1.1, -40)]), lo=150, hi=2000),
      -26, pan=0.25, wet=0.45)
place('clang_4.0', 4.0, filt(vari(brake, [(0, .3)], length=2.5), hi=1500), -26, pan=0.3, wet=0.5)
place('clang_4.4', 4.4, filt(vari(anvil, [(0, .2)], length=2.5), lo=150, hi=2000), -28, pan=-0.3, wet=0.5)
place('clang_4.4_gong', 4.4, filt(shape(vari(gong_mf, [(0, .5)], length=2.5), [(0, 0), (2.5, -30)]), lo=40, hi=1200), -24, wet=0.4)

# ---- 4.9-5.5 s: the dip, a short scrape
place('scrape_5.0', 4.7, filt(shape(vari(scrape, [(0, .5)], start=0.3, length=0.75), [(0, -20), (0.1, 0), (0.5, -3), (0.75, -40)]), lo=300, hi=4000), -25, wet=0.5)
# a metallic mid texture under the second half (two bowed-cymbal takes slowed ~2.5x, slowly drifting)
TEX = [(4.6, -30), (5.0, -4), (5.5, -6), (6.6, 0), (7.0, -2), (7.5, -2), (8.0, 0), (8.6, -1), (9.0, -2), (9.4, -40)]
place('texture_bow4', 4.6, filt(shape(vari(bow4, [(0, .44), (2, .4), (4.6, .37)], start=1.0, length=4.6), [(t - 4.6, d) for t, d in TEX]), lo=200, hi=2500),
      -32, pan=0.2, wet=0.45)
place('texture_bow3', 4.6, filt(shape(vari(bow3, [(0, .4), (2.5, .46), (4.6, .42)], start=2.0, length=4.6), [(t - 4.6, d) for t, d in TEX]), lo=200, hi=2500),
      -33, pan=-0.25, wet=0.45)

# ---- 5.4-6.6 s: swell with faint mechanical clicks (ratchet a bit slowed), a rub groaning upward
place('clicks', 5.4, filt(shape(vari(ratchet, [(0, .7)], start=0.5, length=1.4), [(0, -12), (0.4, 0), (1.1, -2), (1.4, -40)]), lo=300, hi=4500),
      -36, pan=0.2, wet=0.3, width=0.6)
place('groan_rub2', 5.4, filt(shape(vari(rub2, [(0, .45), (1.2, .6)], start=1.0, length=1.6), [(0, -24), (1.1, 0), (1.6, -30)]), lo=30, hi=900),
      -24, pan=-0.1, wet=0.3)

# ---- 7.5-8.0 rise (a reversed slowed gong), 8.0 deep hit, a falling groan 7.8-8.6
rev = filt(vari(gong_f, [(0, .4)], length=1.2), lo=30, hi=1200)[::-1]
place('rise_rev_gong', HIT2 - len(rev) / SR, shape(rev, [(0, -30), (len(rev) / SR - 0.05, 0), (len(rev) / SR, -60)]), -24, wet=0.3)
place('hit2_gong/3', HIT2, filt(shape(vari(gong_f, [(0, .33), (2, .3)], length=2.0), [(0, 0), (0.5, -9), (2.0, -40)]), lo=25, hi=700), -21, wet=0.35)
place('hit2_kick/2', HIT2, filt(shape(vari(bd, [(0, .45)], length=3), [(0, 0), (0.3, -6), (1.5, -40)]), hi=250), -19, wet=0.1)
place('hit2_brake/5', HIT2, filt(vari(brake, [(0, .2)], length=3), hi=1800), -28, pan=-0.2, wet=0.5)
place('fall_groan', 7.8, filt(shape(vari(gong_mf, [(0, .7), (0.8, .32)], start=0.05, length=1.1), [(0, -18), (0.2, 0), (0.8, -4), (1.1, -40)]), lo=40, hi=1500),
      -25, wet=0.4)

if __name__ == '__main__':
    out = sys.argv[1]
    wd = os.path.join(out, 'build', 'TAGS_metal'); os.makedirs(wd, exist_ok=True)
    rv = sox_reverb(send, (85, 60, 100, 100, 40, 0), wd)
    L = min(len(rv), len(mix))
    y = (mix[:L] + rv[:L] * 0.3)[:N]
    y = master(y, os.path.join(out, 'build'), 'TAGS_metal', (9.3, 9.95), True)
    wav, ogg = export(y, out, 'TAGS_theme')
    y = decode(ogg)
    rep = dict(length_samples=len(y), ogg_peak_dbfs=round(ogg_peak_db(ogg), 2), layers=LAYERS,
               accents={str(t): round(accent_time(y, t), 4) for t in (HIT1, 4.0, 4.4, HIT2)})
    json.dump(rep, open(os.path.join(out, 'TAGS_theme_report.json'), 'w'), indent=1)
    print(json.dumps(rep['accents']), rep['length_samples'], rep['ogg_peak_dbfs'])
