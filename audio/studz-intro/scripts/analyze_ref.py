"""Measure a reference intro: loudness curve, band energies, onsets/hits,
tempo, chords/key over time. Usage: analyze_ref.py in.wav out_prefix"""
import sys, json, numpy as np, librosa, soundfile as sf
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
wav, pre = sys.argv[1], sys.argv[2]
y, sr = librosa.load(wav, sr=22050, mono=True)
dur = len(y) / sr
hop = 512
t = librosa.frames_to_time(np.arange(1 + len(y) // hop), sr=sr, hop_length=hop)
rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=hop)[0]
rdb = 20 * np.log10(rms + 1e-9)
S = np.abs(librosa.stft(y, n_fft=2048, hop_length=hop))
f = librosa.fft_frequencies(sr=sr, n_fft=2048)
def band(lo, hi):
    return 10 * np.log10((S[(f >= lo) & (f < hi)] ** 2).sum(axis=0) + 1e-9)
bands = {'sub<60': band(20, 60), 'bass60-250': band(60, 250), 'mid250-2k': band(250, 2000), 'high2k-8k': band(2000, 8000), 'air>8k': band(8000, 11000)}
cent = librosa.feature.spectral_centroid(S=S, sr=sr)[0]
onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop)
onsets = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr, hop_length=hop, units='time')
tempo, beats = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr, hop_length=hop, units='time')
# strongest hits
idx = np.argsort(onset_env)[::-1]
hits = []
for i in idx:
    tt = t[i] if i < len(t) else i * hop / sr
    if all(abs(tt - h[0]) > 0.6 for h in hits):
        hits.append((round(float(tt), 2), round(float(onset_env[i]), 1), round(float(rdb[min(i + 4, len(rdb) - 1)]), 1)))
    if len(hits) >= 14:
        break
hits.sort()
# chroma per 1-second window -> chord guess
chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=hop)
NOTES = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']
def chord_guess(v):
    best = None
    for r in range(12):
        for q, iv in (('', (0, 4, 7)), ('m', (0, 3, 7))):
            s = sum(v[(r + k) % 12] for k in iv)
            if best is None or s > best[0]:
                best = (s, NOTES[r] + q)
    return best[1]
win = []
for s0 in np.arange(0, dur, 1.0):
    a, b_ = librosa.time_to_frames([s0, s0 + 1.0], sr=sr, hop_length=hop)
    v = chroma[:, a:b_].mean(axis=1)
    top = [NOTES[k] for k in np.argsort(v)[::-1][:3]]
    win.append((round(float(s0), 1), round(float(rdb[a:b_].mean()), 1), chord_guess(v), top, round(float(cent[a:b_].mean())), {k: round(float(vv[a:b_].mean()), 1) for k, vv in bands.items()}))
key_prof = chroma.mean(axis=1)
rep = dict(duration=round(dur, 2), tempo_est=float(np.atleast_1d(tempo)[0]), n_onsets=len(onsets), hits=hits,
           loudest_second=max(win, key=lambda w: w[1])[0], key_top=[NOTES[k] for k in np.argsort(key_prof)[::-1][:5]])
json.dump(dict(rep, windows=win), open(pre + '.json', 'w'), indent=1)
print(json.dumps(rep, indent=1))
print('sec  rmsdB chord   top3            centroid  bands(dB)')
for w in win:
    print(f"{w[0]:4.0f} {w[1]:6.1f} {w[2]:6s} {' '.join(w[3]):14s} {w[4]:6d}  " + ' '.join(f"{k.split('<')[0].split('>')[0][:4]}:{v:5.1f}" for k, v in w[5].items()))
fig, ax = plt.subplots(4, 1, figsize=(15, 12), sharex=True)
ax[0].plot(t[:len(rdb)], rdb); ax[0].set_ylabel('RMS dB'); ax[0].grid(alpha=.3)
for h in hits: ax[0].axvline(h[0], color='r', alpha=.3)
for k, v in bands.items(): ax[1].plot(t[:len(v)], v - v.max(), label=k, lw=0.8)
ax[1].legend(fontsize=7); ax[1].set_ylabel('band dB (rel)'); ax[1].grid(alpha=.3)
D = librosa.amplitude_to_db(S, ref=np.max)
ax[2].imshow(D, origin='lower', aspect='auto', extent=[0, dur, 0, sr / 2], cmap='magma', vmin=-80); ax[2].set_ylim(0, 8000); ax[2].set_ylabel('Hz')
ax[3].imshow(chroma, origin='lower', aspect='auto', extent=[0, dur, 0, 12], cmap='viridis'); ax[3].set_yticks(np.arange(12) + .5); ax[3].set_yticklabels(NOTES, fontsize=7)
ax[3].set_xlabel('s'); plt.tight_layout(); plt.savefig(pre + '.png', dpi=60)
