"""Waveform + spectrogram + loudness plot of a rendered piece, with the accent
targets marked (a visual check of the mix and timing)."""
import sys, numpy as np, soundfile as sf
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
wav, png = sys.argv[1], sys.argv[2]; marks = [float(v) for v in sys.argv[3:]]
y, sr = sf.read(wav, always_2d=True); m = y.mean(axis=1); t = np.arange(len(m)) / sr
fig, ax = plt.subplots(3, 1, figsize=(14, 9), sharex=True)
ax[0].plot(t, y[:, 0], lw=0.3); ax[0].plot(t, y[:, 1], lw=0.3, alpha=0.6); ax[0].set_ylim(-1, 1); ax[0].set_ylabel('wave')
ax[1].specgram(m, NFFT=2048, Fs=sr, noverlap=1536, cmap='magma', vmin=-120); ax[1].set_ylim(0, 12000); ax[1].set_ylabel('Hz')
k = int(sr * 0.05); rms = np.sqrt(np.convolve(m ** 2, np.ones(k) / k, 'same'))
ax[2].plot(t, 20 * np.log10(rms + 1e-9)); ax[2].set_ylim(-70, 0); ax[2].set_ylabel('dBFS rms 50ms'); ax[2].grid(alpha=0.3)
for a in ax:
    for v in marks: a.axvline(v, color='cyan', lw=0.8, alpha=0.7)
ax[2].set_xlabel('s'); plt.tight_layout(); plt.savefig(png, dpi=70)
