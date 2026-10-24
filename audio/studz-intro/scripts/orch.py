"""Tiny orchestration toolkit: write each part as MIDI, render it with real
instrument samples (sfizz + VSCO-2 SFZ, fluidsynth + GeneralUser GS for the
celesta), line the stems up so the accents land on time, mix with a hall
reverb send, master and export.

Paths come from the environment (see README.md):
  VSCO_DIR   folder of the VSCO-2 Community Edition SFZ branch
  GUGS_SF2   path to GeneralUser-GS.sf2
  SFIZZ      path to the sfizz_render binary
"""
import os, subprocess, math, json
import numpy as np
import mido
import soundfile as sf

SR = 44100
HERE = os.path.dirname(os.path.abspath(__file__))
VSCO = os.environ.get('VSCO_DIR', '')
GUGS = os.environ.get('GUGS_SF2', '')
SFIZZ = os.environ.get('SFIZZ', 'sfizz_render')
TPB = 1000            # ticks per beat; tempo 60 bpm -> 1 tick = 1 ms

_NAMES = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}


def n(name):
    """'C4' -> 60, 'F#5' -> 78, 'Bb2' -> 46."""
    if isinstance(name, int):
        return name
    p = _NAMES[name[0].upper()]
    rest = name[1:]
    while rest and rest[0] in '#b':
        p += 1 if rest[0] == '#' else -1
        rest = rest[1:]
    return p + 12 * (int(rest) + 1)


# Custom SFZ for the VSCO one-shot percussion we use (no SFZ ships for these).
PERC_SFZ = r"""
<control> default_path=Percussion/
<global> ampeg_release=8 loop_mode=one_shot
<group> key=36 // bass drum
<region> sample=BDrumNewhit_v2_rr1_Sum.wav hivel=40
<region> sample=BDrumNewhit_v4_rr1_Sum.wav lovel=41 hivel=80
<region> sample=BDrumNewhit_v6_rr1_Sum.wav lovel=81 hivel=110
<region> sample=BDrumNewhit_v7_rr1_Sum.wav lovel=111
<group> key=49 // crash cymbal
<region> sample=cymbal-crash1_pp_rr1.wav hivel=40
<region> sample=cymbal-crash1_mp_rr1.wav lovel=41 hivel=80
<region> sample=cymbal-crash1_mf_rr1.wav lovel=81 hivel=110
<region> sample=cymbal-crash1_ff_rr1.wav lovel=111
<group> key=51 // suspended cymbal, soft mallet
<region> sample=susCymb1-hit_pp_rr1.wav hivel=40
<region> sample=susCymb1-hit_mp_rr1.wav lovel=41 hivel=80
<region> sample=susCymb1-hit_f_rr1.wav lovel=81 hivel=110
<region> sample=susCymb1-hit_fff_rr1.wav lovel=111
<group> key=52 // suspended cymbal crescendo rolls (short / medium / long)
<region> sample=susCymb1-cresc-Short_v1.wav
<group> key=53
<region> sample=susCymb1-cresc-Median_v1.wav
<group> key=54
<region> sample=susCymb1-cresc-Long_v1.wav
<group> key=55 // gong
<region> sample=gongHit_p.wav hivel=40
<region> sample=gongHit_mf.wav lovel=41 hivel=80
<region> sample=gongHit_f.wav lovel=81 hivel=110
<region> sample=gongHit_fff.wav lovel=111
<group> // bell tree strokes
<region> key=57 sample=BellTree_Stroke1_v1_Sum.wav
<region> key=58 sample=BellTree_Stroke2_v1_Sum.wav
<region> key=59 sample=BellTree_Stroke3_v1_Sum.wav
<region> key=60 sample=BellTree_Stroke4_v1_Sum.wav
<group> // triangles
<region> key=62 sample=Triangle3-Hit_v2_rr1_Sum.wav
<region> key=63 sample=Triangle6-Hit_v2_rr1_Sum.wav
<region> key=64 sample=Triangle6-HitM_v2_rr1_Sum.wav
<group> key=65 // bowed suspended cymbal (shimmer)
<region> sample=susCymb1-bow-1.wav
<group> key=37 // snare taps (soft ticking)
<region> sample=Snare2-taps_v1_rr1_Sum.wav hivel=40
<region> sample=Snare2-taps_v2_rr1_Sum.wav lovel=41 hivel=70
<region> sample=Snare2-taps_v3_rr1_Sum.wav lovel=71 hivel=100
<region> sample=Snare2-taps_v4_rr1_Sum.wav lovel=101
<group> key=38 // snare hit
<region> sample=Snare2-HitSN_v1_rr1_Sum.wav hivel=30
<region> sample=Snare2-HitSN_v3_rr1_Sum.wav lovel=31 hivel=60
<region> sample=Snare2-HitSN_v5_rr1_Sum.wav lovel=61 hivel=90
<region> sample=Snare2-HitSN_v7_rr1_Sum.wav lovel=91 hivel=112
<region> sample=Snare2-HitSN_v9_rr1_Sum.wav lovel=113
<group> key=40 loop_mode=no_loop ampeg_release=0.12 // snare roll (note-off cuts it)
<region> sample=Snare2-rollSN_v1_rr1_Sum.wav hivel=50
<region> sample=Snare2-rollSN_v3_rr1_Sum.wav lovel=51 hivel=95
<region> sample=Snare2-rollSN_v5_rr1_Sum.wav lovel=96
<group> key=56 // gong scrape (dark shimmer)
<region> sample=gongscrape_pp.wav hivel=80
<region> sample=gongscrape_mf.wav lovel=81
<group> key=35 loop_mode=no_loop ampeg_release=0.18 // bass drum, damped (for beat patterns)
<region> sample=BDrumNewhit_v3_rr1_Sum.wav hivel=60
<region> sample=BDrumNewhit_v5_rr1_Sum.wav lovel=61 hivel=100
<region> sample=BDrumNewhit_v7_rr1_Sum.wav lovel=101
<group> key=67 // anvil
<region> sample=Anvil_Hit1_v1_Sum.wav hivel=60
<region> sample=Anvil_Hit1_v2_Sum.wav lovel=61 hivel=100
<region> sample=Anvil_Hit1_v3_Sum.wav lovel=101
<group> key=68 // brake drum (metal)
<region> sample=BrakeDrum1_Hammer_v1_Sum.wav hivel=60
<region> sample=BrakeDrum1_Hammer_v2_Sum.wav lovel=61 hivel=100
<region> sample=BrakeDrum1_Hammer_v3_Sum.wav lovel=101
<group> key=70 // tambourine shake
<region> sample=Tamb1-Shake_v1_rr1_Sum.wav
<group> // ratchet: mechanical clicking for the robot/transformation sounds
<region> key=71 sample=Ratchet1-Crank_v1_rr1_Sum.wav
<region> key=72 sample=Ratchet1-Fast_v1_rr1_Sum.wav
<region> key=73 sample=Ratchet1-Slow_v1_rr1_Sum.wav
<group> key=75 // claves
<region> sample=Claves1_Hit_v1_rr1_Sum.wav hivel=50
<region> sample=Claves1_Hit_v2_rr1_Sum.wav lovel=51 hivel=95
<region> sample=Claves1_Hit_v3_rr1_Sum.wav lovel=96
"""
PERC = dict(bd=36, crash=49, cym=51, swell_s=52, swell_m=53, swell_l=54, gong=55,
            tree1=57, tree2=58, tree3=59, tree4=60, tri3=62, tri6=63, tri6m=64, bow=65,
            taps=37, snare=38, sroll=40, claves=75, gscrape=56,
            bdd=35, anvil=67, brake=68, shaker=70,
            ratchet=71, ratchet_fast=72, ratchet_slow=73)


class Part:
    def __init__(self, name, inst, level=-20.0, pan=0.0, send=0.3, align=None, env=None, split=False, thresh=0.35):
        self.name, self.inst = name, inst          # inst: 'Harp' (VSCO sfz) / 'perc' / ('gm', program)
        self.level = level                         # loudest 100 ms RMS of the stem, dBFS (before the master)
        self.notes = []                            # (start s, dur s, midi note, velocity)
        self.pan, self.send = pan, send
        self.align = align                         # time (s) of the accent this stem must hit exactly
        self.env = env or []                       # [(t, dB)] gain automation
        self.split = split                         # time every chord on its own (stabs)
        self.thresh = thresh                       # fraction of the peak that counts as the attack

    def add(self, t, pitches, dur, vel):
        for p in (pitches if isinstance(pitches, (list, tuple)) else [pitches]):
            self.notes.append((float(t), float(dur), n(p), int(max(1, min(127, vel)))))
        return self


def write_midi(notes, path, program=None, extra_tail=0.5):
    mid = mido.MidiFile(ticks_per_beat=TPB)
    tr = mido.MidiTrack(); mid.tracks.append(tr)
    tr.append(mido.MetaMessage('set_tempo', tempo=1_000_000, time=0))
    if program is not None:
        tr.append(mido.Message('program_change', program=program, channel=0, time=0))
    ev = []
    for (t, d, p, v) in notes:
        ev.append((round(t * 1000), 1, p, v))
        ev.append((round((t + d) * 1000), 0, p, 0))
    ev.sort(key=lambda e: (e[0], e[1]))
    now = 0
    for (tk, on, p, v) in ev:
        msg = 'note_on' if on else 'note_off'
        tr.append(mido.Message(msg, note=p, velocity=v if on else 0, channel=0, time=tk - now))
        now = tk
    tr.append(mido.MetaMessage('end_of_track', time=round(extra_tail * 1000)))
    mid.save(path)


def render(part, workdir):
    os.makedirs(workdir, exist_ok=True)
    midp = os.path.join(workdir, part.name + '.mid')
    wav = os.path.join(workdir, part.name + '.wav')
    if isinstance(part.inst, tuple):          # General MIDI program through fluidsynth (celesta)
        write_midi(part.notes, midp, program=part.inst[1])
        subprocess.run(['fluidsynth', '-ni', '-q', '-g', '1.0', '-r', str(SR), '-R', '0', '-C', '0',
                        '-F', wav, GUGS, midp], check=True, stdout=subprocess.DEVNULL)
    else:
        sfz = os.path.join(VSCO, part.inst + '.sfz')
        if part.inst == 'perc':
            sfz = os.path.join(VSCO, '_studz_perc.sfz')
            with open(sfz, 'w') as f:
                f.write(PERC_SFZ)
        write_midi(part.notes, midp)
        subprocess.run([SFIZZ, '--sfz', sfz, '--midi', midp, '--wav', wav, '-s', str(SR), '-q', '3', '-p', '128'],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    x, sr = sf.read(wav, always_2d=True)
    assert sr == SR
    if x.shape[1] == 1:
        x = np.repeat(x, 2, axis=1)
    return x[:, :2]


def latency(p, workdir, ref=None):
    """How late the accent (or first) chord of a part sounds after its note-on:
    render just that chord on its own and find where it reaches `thresh` of
    its peak (a stand-in for the perceived attack of slow-speaking samples)."""
    if not p.notes:
        return 0.0
    if ref is None:
        ref = p.align if p.align is not None else min(t for t, *_ in p.notes)
    chord = [(0.5, d, q, v) for (t, d, q, v) in p.notes if abs(t - ref) < 1e-3]
    probe = Part(f'{p.name}_probe', p.inst); probe.notes = chord
    x = render(probe, workdir)
    thresh = p.thresh
    e = envelope(x, 0.01)
    i0, i1 = int(0.45 * SR), int(2.0 * SR)
    seg = e[i0:i1]
    if seg.size == 0 or seg.max() < 1e-6:
        return 0.0
    k = int(np.argmax(seg >= thresh * seg.max()))
    return float(np.clip((i0 + k) / SR - 0.5, 0.0, 0.3))


def render_split(p, workdir):
    """Render each chord of a stab part separately and place it so its own
    attack lands exactly on its time. Returns the assembled stem (no shift)."""
    times = sorted({round(t, 4) for t, *_ in p.notes})
    out = np.zeros((int((max(t + d for t, d, *_ in p.notes) + 8) * SR), 2))
    for t0 in times:
        lat = latency(p, workdir, t0)
        probe = Part(f'{p.name}_at{int(t0 * 1000)}', p.inst)
        probe.notes = [(0.5, d, q, v) for (t, d, q, v) in p.notes if abs(t - t0) < 1e-3]
        x = render(probe, workdir)
        start = int(round((t0 - 0.5 - lat) * SR))
        a0 = max(0, -start)
        seg = x[a0:]
        e = min(len(out), start + a0 + len(seg))
        out[start + a0:e] += seg[:e - start - a0]
    return out


def envelope(x, win=0.005):
    a = np.abs(x).max(axis=1)
    k = max(1, int(SR * win))
    return np.convolve(a, np.ones(k) / k, 'same')


def onset_near(x, t, before=0.12, after=0.25):
    """Time of the steepest rise of the envelope near t (the perceived attack)."""
    e = envelope(x)
    i0, i1 = max(0, int((t - before) * SR)), min(len(e) - 1, int((t + after) * SR))
    seg = e[i0:i1]
    if seg.size < 10 or seg.max() < 1e-5:
        return None
    d = np.diff(np.convolve(seg, np.ones(int(SR * 0.004)) / int(SR * 0.004), 'same'))
    return (i0 + int(np.argmax(d))) / SR


def gain_curve(env, length):
    if not env:
        return np.ones(length)
    ts = np.array([p[0] for p in env]); db = np.array([p[1] for p in env], dtype=float)
    t = np.arange(length) / SR
    return 10 ** (np.interp(t, ts, db) / 20)


def pan_gains(p):
    a = (p + 1) * math.pi / 4
    return math.cos(a) * math.sqrt(2), math.sin(a) * math.sqrt(2)


def sox_reverb(x, args, tmp):
    a, b = os.path.join(tmp, '_rv_in.wav'), os.path.join(tmp, '_rv_out.wav')
    g = max(1e-9, np.abs(x).max()) / 0.5          # keep sox's input well below clipping
    sf.write(a, x / g, SR, subtype='FLOAT')
    subprocess.run(['sox', a, b, 'reverb', '-w'] + [str(v) for v in args], check=True)
    y, _ = sf.read(b, always_2d=True)
    return y * g


def build(title, parts, length, workdir, reverb=(60, 45, 100, 100, 20, 0), wet=0.32,
          fade=None, comp=True):
    """Render all parts, align, mix, master. Returns (stereo array, report dict)."""
    N = int(round(length * SR))
    dry = np.zeros((N + SR * 8, 2)); send = np.zeros_like(dry)
    report = {'stems': {}}
    for p in parts:
        if p.split:
            x, shift = render_split(p, os.path.join(workdir, title)), 0.0
        else:
            x = render(p, os.path.join(workdir, title))
            shift = latency(p, os.path.join(workdir, title))
        s = int(round(shift * SR))
        x = x[s:] if s > 0 else np.vstack([np.zeros((-s, 2)), x])
        L = min(len(x), len(dry))
        x = x[:L]
        k = int(SR * 0.1)
        rms = np.sqrt(np.convolve((x ** 2).mean(axis=1), np.ones(k) / k, 'same')).max()
        x = x / max(rms, 1e-9) * 10 ** (p.level / 20) * gain_curve(p.env, L)[:, None]
        gl, gr = pan_gains(p.pan)
        x = np.stack([x[:, 0] * gl, x[:, 1] * gr], axis=1)
        dry[:L] += x
        send[:L] += x * p.send
        if os.environ.get('SAVE_STEMS'):
            sf.write(os.path.join(workdir, title, p.name + '_stem.wav'), x[:N], SR, subtype='FLOAT')
        report['stems'][p.name] = dict(inst=str(p.inst), shift_ms=round(shift * 1000, 1),
                                       peak_db=round(20 * math.log10(np.abs(x).max() + 1e-12), 1))
    rv = sox_reverb(send, reverb, os.path.join(workdir, title))
    L = min(len(rv), len(dry))
    mix = dry[:L] + rv[:L] * wet
    mix = mix[:N]
    if len(mix) < N:
        mix = np.vstack([mix, np.zeros((N - len(mix), 2))])
    return master(mix, workdir, title, fade, comp), report


def master(mix, workdir, title, fade, comp):
    tmp_a = os.path.join(workdir, title, '_pre.wav'); tmp_b = os.path.join(workdir, title, '_post.wav')
    sf.write(tmp_a, mix / max(1e-9, np.abs(mix).max()) * 0.5, SR, subtype='FLOAT')
    filt = ['highpass=f=28', 'equalizer=f=250:t=q:w=1.0:g=-1.5', 'equalizer=f=9000:t=q:w=0.8:g=1.0']
    if comp:
        filt.append('acompressor=threshold=-20dB:ratio=2:attack=25:release=300:knee=6:makeup=1')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', tmp_a, '-af', ','.join(filt), '-c:a', 'pcm_f32le', tmp_b], check=True)
    y, _ = sf.read(tmp_b, always_2d=True)
    y = y[:len(mix)]
    if fade:
        f0, f1 = fade
        t = np.arange(len(y)) / SR
        g = np.where(t < f0, 1.0, np.where(t > f1, 0.0, 0.5 * (1 + np.cos(np.pi * (t - f0) / (f1 - f0)))))
        y = y * g[:, None]
    y[-int(0.02 * SR):] = 0.0                       # true silence at the very end
    y = y / np.abs(y).max() * 10 ** (-1.0 / 20)     # normalize to -1 dBFS peak
    return y


def accent_time(y, t, win=0.06):
    """Measured accent time near t in a finished mix: the 2 ms frame where the
    energy above 1.5 kHz (where attacks live) rises most steeply, in dB,
    compared with the 20 ms before it."""
    m = y.mean(axis=1)
    i0 = max(0, int((t - win - 0.05) * SR)); i1 = min(len(m), int((t + win + 0.02) * SR))
    seg = m[i0:i1]
    spec = np.fft.rfft(seg); f = np.fft.rfftfreq(len(seg), 1 / SR); spec[f < 1500] = 0
    hf = np.fft.irfft(spec, len(seg))
    hop = int(0.002 * SR)
    e = np.array([np.mean(hf[k:k + hop] ** 2) for k in range(0, len(hf) - hop, hop)]) + 1e-12
    db = 10 * np.log10(np.convolve(e, np.ones(3) / 3, 'same'))
    rise = np.array([db[k] - db[max(0, k - 10):k].mean() if k >= 10 else -99 for k in range(len(db))])
    k_lo, k_hi = int(0.05 / 0.002), int((0.05 + 2 * win) / 0.002)
    k = k_lo + int(np.argmax(rise[k_lo:k_hi]))
    return (i0 + k * hop) / SR


def spectral_flux_onset(y, t, win=0.06):
    """Measured accent time near t in a finished mix (broadband spectral flux peak)."""
    m = y.mean(axis=1)
    hop, nfft = 128, 1024
    i0 = max(0, int((t - win - 0.012) * SR)); i1 = min(len(m), int((t + win + 0.012) * SR))
    seg = m[i0:i1]
    frames = [seg[k:k + nfft] * np.hanning(nfft) for k in range(0, len(seg) - nfft, hop)]
    S = np.abs(np.fft.rfft(np.array(frames), axis=1))
    flux = np.maximum(0, np.diff(np.log1p(S * 50), axis=0)).sum(axis=1)
    k0 = int(np.argmax(flux >= 0.5 * flux.max()))          # first strong attack in the window
    k = k0 + int(np.argmax(flux[k0:k0 + 4])) + 1
    return (i0 + k * hop + nfft // 2) / SR


def export(y, outdir, title):
    os.makedirs(outdir, exist_ok=True)
    wav = os.path.join(outdir, title + '.wav'); ogg = os.path.join(outdir, title + '.ogg')
    for _ in range(4):        # Vorbis can overshoot the WAV peak: trim until the OGG peak is <= -1 dBFS
        sf.write(wav, y, SR, subtype='PCM_24')
        subprocess.run(['oggenc', '-Q', '-q', '7', '-o', ogg, wav], check=True)
        pk = ogg_peak_db(ogg)
        if pk <= -0.98:
            break
        y = y * 10 ** ((-1.0 - pk) / 20)
    return wav, ogg


def decode(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).astype(float)


def ogg_peak_db(path):
    return 20 * math.log10(np.abs(decode(path)).max())


def save_score(parts, path):
    """Multi-track MIDI of the whole piece (one track per part)."""
    mid = mido.MidiFile(ticks_per_beat=TPB, type=1)
    meta = mido.MidiTrack(); mid.tracks.append(meta)
    meta.append(mido.MetaMessage('set_tempo', tempo=1_000_000, time=0))
    for ch_i, p in enumerate(parts):
        tr = mido.MidiTrack(); mid.tracks.append(tr)
        tr.append(mido.MetaMessage('track_name', name=f'{p.name} ({p.inst})', time=0))
        ch = 9 if p.inst == 'perc' else ch_i % 9
        ev = []
        for (t, d, q, v) in p.notes:
            ev += [(round(t * 1000), 1, q, v), (round((t + d) * 1000), 0, q, 0)]
        ev.sort(key=lambda e: (e[0], e[1])); now = 0
        for (tk, on, q, v) in ev:
            tr.append(mido.Message('note_on' if on else 'note_off', note=q, velocity=v, channel=ch, time=tk - now)); now = tk
    mid.save(path)
