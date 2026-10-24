"""Side-by-side every 0.25 s: loudness (RMS dB), brightness (centroid Hz) and the
share of energy below 250 Hz, for a reference and a render. Prints the gaps."""
import sys, numpy as np, librosa
ref, mine = sys.argv[1], sys.argv[2]
end = float(sys.argv[3]) if len(sys.argv) > 3 else 9.0
def feats(f):
    y, sr = librosa.load(f, sr=22050); h = int(sr * 0.25)
    out = []
    for i in range(int(end / 0.25)):
        s = y[i * h:(i + 1) * h]
        if len(s) < h: break
        S = np.abs(np.fft.rfft(s * np.hanning(len(s)))) ** 2; fr = np.fft.rfftfreq(len(s), 1 / sr)
        out.append((10 * np.log10((s ** 2).mean() + 1e-12), (S * fr).sum() / (S.sum() + 1e-12), S[fr < 250].sum() / (S.sum() + 1e-12)))
    return np.array(out)
a, b = feats(ref), feats(mine)
n = min(len(a), len(b)); a, b = a[:n], b[:n]
off = np.median(a[4:, 0] - b[4:, 0])           # compare shapes, not absolute level
print(f'level offset {off:+.1f} dB (applied to mine)')
print('  t   ref dB  mine   diff | ref cent mine | ref low% mine')
for i in range(n):
    print(f'{i*0.25:5.2f} {a[i,0]:6.0f} {b[i,0]+off:6.0f} {b[i,0]+off-a[i,0]:+5.0f} | {a[i,1]:6.0f} {b[i,1]:6.0f} | {a[i,2]*100:5.0f} {b[i,2]*100:5.0f}')
k = slice(4, n)
print(f'mean |loudness gap| {np.abs(b[k,0]+off-a[k,0]).mean():.1f} dB, loudness corr {np.corrcoef(a[k,0], b[k,0])[0,1]:.2f}, '
      f'centroid ref {a[k,1].mean():.0f} vs mine {b[k,1].mean():.0f} Hz, low share ref {a[k,2].mean()*100:.0f}% vs mine {b[k,2].mean()*100:.0f}%')
