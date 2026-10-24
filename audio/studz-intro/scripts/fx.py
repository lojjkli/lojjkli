"""Synthesized trailer sound design (all generated here with numpy, no samples):
sub impacts, braam layers, pitch-dive 'downers', noise risers, reverse swells,
mechanical ticks, metal hits and a low rumble. Each Buf becomes one stem
through Part(name, buf) - build() calls it instead of rendering MIDI."""
import numpy as np
from scipy import signal as ss
from orch import SR

_rng = np.random.default_rng(7)


class Buf:
    def __init__(self, length, tail=8.0):
        self.x = np.zeros((int((length + tail) * SR), 2))
        self.__name__ = 'fx'

    def __call__(self):
        return self.x

    def put(self, t, y, pan=0.0):
        """Add mono or stereo y starting at t seconds."""
        if y.ndim == 1:
            a = (pan + 1) * np.pi / 4
            y = np.stack([y * np.cos(a), y * np.sin(a)], axis=1) * np.sqrt(2)
        i = int(round(t * SR))
        a0 = max(0, -i)
        e = min(len(self.x), i + len(y))
        if e > i + a0:
            self.x[i + a0:e] += y[a0:e - i]
        return self


def _t(dur):
    return np.arange(int(dur * SR)) / SR


def _glide(f0, f1, dur, curve=3.0):
    """Instantaneous frequency gliding f0 -> f1 (exponential, fast at first)."""
    u = _t(dur) / dur
    return f1 + (f0 - f1) * np.exp(-curve * u) * (1 - u)


def _phase(freq):
    return 2 * np.pi * np.cumsum(freq) / SR


def _env(dur, att, tau=None, rel=0.05):
    t = _t(dur)
    e = np.minimum(1, t / max(att, 1e-4))
    if tau:
        e = e * np.exp(-np.maximum(0, t - att) / tau)
    r = int(rel * SR)
    if r and r < len(e):
        e[-r:] *= np.linspace(1, 0, r)
    return e


def _sweep_filter(x, centers, width_oct=1.0, lowpass=False):
    """Time-varying band/lowpass via STFT masking; centers: Hz per sample."""
    f, tt, Z = ss.stft(x, SR, nperseg=2048, noverlap=1536)
    idx = np.clip((tt * SR).astype(int), 0, len(centers) - 1)
    c = centers[idx][None, :]
    ff = np.maximum(f, 1)[:, None]
    if lowpass:
        m = 1 / np.sqrt(1 + (ff / c) ** 8)
    else:
        m = np.exp(-0.5 * (np.log2(ff / c) / width_oct) ** 2)
    _, y = ss.istft(Z * m, SR, nperseg=2048, noverlap=1536)
    return y[:len(x)]


def impact(buf, t, f0=62, f1=27, dur=2.2, tau=0.55, gain=1.0):
    """Sub boom: sine diving in pitch, saturated, with a short click on top."""
    s = np.sin(_phase(_glide(f0, f1, dur, 4.0)))
    s = np.tanh(2.2 * s * _env(dur, 0.004, tau)) / np.tanh(2.2)
    click = _rng.standard_normal(int(0.012 * SR)) * np.exp(-_t(0.012) / 0.003)
    click = ss.sosfilt(ss.butter(2, [400, 5000], 'band', fs=SR, output='sos'), click)
    s[:len(click)] += 0.6 * click
    buf.put(t, s * gain)


def braam(buf, t, freqs, dur=1.6, tau=0.9, bright=2600, dive=0.0, gain=1.0):
    """Gritty brass-like 'BRAAM': detuned saws per pitch, filter closing after
    the attack, distortion; optional pitch dive (semitones) over the tail."""
    T = _t(dur)
    bend = 2 ** (-dive / 12 * np.clip((T - dur * 0.45) / (dur * 0.55), 0, 1) ** 2)
    out = np.zeros((len(T), 2))
    for f in freqs:
        for ch in range(2):
            for d in (-11, -4, 3, 9):
                det = 2 ** ((d + (2 if ch else -2)) / 1200)
                ph = _phase(f * det * bend) + _rng.uniform(0, 6.28)
                out[:, ch] += ((ph / (2 * np.pi)) % 1) * 2 - 1
    cut = 180 + (bright - 180) * np.exp(-T / (0.35 * dur)) * np.minimum(1, T / 0.04)
    for ch in range(2):
        out[:, ch] = _sweep_filter(out[:, ch], cut, lowpass=True)
    out = np.tanh(1.8 * out / np.abs(out).max()) * _env(dur, 0.03, tau, 0.25)[:, None]
    buf.put(t, out * gain)


def downer(buf, t, f0=1400, f1=70, dur=1.4, gain=1.0, pan=0.0):
    """Falling pitch sweep (tonal 'downer'), slightly distorted."""
    fr = _glide(f0, f1, dur, 2.5)
    ph = _phase(fr)
    s = np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.2 * np.sin(3 * ph + 1)
    s = np.tanh(1.6 * s) * _env(dur, 0.01, dur * 0.45, 0.2)
    buf.put(t, s * gain, pan)


def riser(buf, t0, t1, f0=250, f1=9000, tone=(180, 1500), gain=1.0, start_db=-36):
    """Noise sweeping up in pitch and loudness from t0, cut dead at t1;
    a sine (tone) rises underneath."""
    dur = t1 - t0
    u = _t(dur) / dur
    c = f0 * (f1 / f0) ** (u ** 1.6)
    out = np.zeros((len(u), 2))
    for ch in range(2):
        out[:, ch] = _sweep_filter(_rng.standard_normal(len(u)), c, 0.6)
    out /= np.abs(out).max()
    if tone:
        ph = _phase(tone[0] * (tone[1] / tone[0]) ** (u ** 1.3))
        out += 0.35 * np.tanh(1.5 * (np.sin(ph) + 0.4 * np.sin(2.01 * ph)))[:, None]
    g = 10 ** (start_db * (1 - u) ** 1.5 / 20)
    g[-int(0.008 * SR):] *= np.linspace(1, 0, int(0.008 * SR))
    buf.put(t0, out * g[:, None] * gain)


def reverse_swell(buf, t1, dur=1.2, gain=1.0, lp=6000):
    """Reversed decaying noise (a 'suck' into a hit) ending exactly at t1."""
    n = _rng.standard_normal((int(dur * SR), 2))
    n = ss.sosfilt(ss.butter(2, lp, fs=SR, output='sos'), n, axis=0)
    e = np.exp(-_t(dur) / (dur * 0.25))
    y = (n * e[:, None])[::-1]
    y[-int(0.006 * SR):] *= np.linspace(1, 0, int(0.006 * SR))[:, None]
    buf.put(t1 - dur, y / np.abs(y).max() * gain)


def tick(buf, t, kind='click', gain=1.0, pan=0.0):
    """Mechanical tick: noise burst + inharmonic ringing partials.
    'click' is small and bright, 'clunk' heavier, 'servo' a short whirr."""
    if kind == 'click':
        parts, dur, nb = [(2150, .03), (3420, .02), (5310, .012), (7600, .008)], 0.08, 0.002
    elif kind == 'clunk':
        parts, dur, nb = [(190, .07), (410, .05), (930, .035), (1720, .02)], 0.25, 0.006
    else:
        parts, dur, nb = [], 0.16, 0.16
    T = _t(dur)
    j = _rng.uniform(0.94, 1.06)
    y = sum(np.sin(2 * np.pi * f * j * T + _rng.uniform(0, 6)) * np.exp(-T / tau) for f, tau in parts) if parts else np.zeros(len(T))
    nz = _rng.standard_normal(len(T)) * np.exp(-T / nb)
    if kind == 'servo':
        nz = np.sign(np.sin(2 * np.pi * np.cumsum(np.linspace(900, 1400, len(T))) / SR)) * 0.5 + 0.5 * nz
        nz *= np.sin(np.pi * T / dur)
    nz = ss.sosfilt(ss.butter(2, [600, 9000], 'band', fs=SR, output='sos'), nz)
    y = y + 0.8 * nz
    buf.put(t, y / np.abs(y).max() * gain, pan)


def metal(buf, t, f=310, dur=2.5, tau=0.7, gain=1.0, pan=0.0):
    """Struck metal plate: inharmonic partials with different decays."""
    T = _t(dur)
    ratios = [1, 1.59, 2.14, 2.65, 3.91, 5.4, 7.13]
    y = sum(np.sin(2 * np.pi * f * r * T + _rng.uniform(0, 6)) * np.exp(-T / (tau / (1 + 0.35 * k))) / (1 + 0.4 * k)
            for k, r in enumerate(ratios))
    nz = ss.sosfilt(ss.butter(2, [1500, 9000], 'band', fs=SR, output='sos'), _rng.standard_normal(len(T))) * np.exp(-T / 0.01)
    y = y / np.abs(y).max() + 0.5 * nz
    buf.put(t, np.tanh(1.2 * y) * gain, pan)


def rumble(buf, t0, t1, hz=36.7, gain=1.0, env=None):
    """Low rumble: lowpassed noise plus a slow-beating sub drone."""
    T = _t(t1 - t0)
    nz = ss.sosfilt(ss.butter(4, 110, fs=SR, output='sos'), _rng.standard_normal((len(T), 2)), axis=0)
    nz /= np.abs(nz).max()
    dr = np.sin(2 * np.pi * hz * T) + 0.5 * np.sin(2 * np.pi * hz * 1.006 * T + 1) + 0.3 * np.sin(2 * np.pi * hz * 2 * T)
    y = 0.6 * nz + 0.5 * dr[:, None] / 1.8
    g = np.interp(T + t0, [p[0] for p in env], [10 ** (p[1] / 20) for p in env]) if env else np.ones(len(T))
    buf.put(t0, y * g[:, None] * gain)
