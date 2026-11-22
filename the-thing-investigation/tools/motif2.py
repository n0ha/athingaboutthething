#!/usr/bin/env python3
"""Memory-safe search for recurrences of a musical passage (replaces motif.py, whose whole-film
STFT plus sliding windows took >20 GB and got the laptop terminal OOM-killed). Run on the VM.

Usage: motif2.py <wav16k_mono> <out_prefix> <tmpl_start_s>:<len_s>[,<start>:<len> ...]

Spectrogram is computed in 120 s chunks (hop 40 ms = 25 frames/s, Hann 2048), only the
30-400 Hz bins are kept (bass/pulse register, mostly below speech formants) as log magnitude:
~48 bins x 163k frames float32 = ~30 MB for the whole film.
For each template: normalised cross-correlation (template and every window z-scored over all
bins x frames), computed with FFT correlation per bin and running sums -> <out>_<k>.csv
(time_s,ncc every 0.2 s) and the 25 best non-overlapping matches printed.
"""
import sys, numpy as np
from scipy.io import wavfile
from scipy.signal import fftconvolve

sr, a = wavfile.read(sys.argv[1], mmap=True)
assert sr == 16000 and a.ndim == 1
out = sys.argv[2]
hop, nfft = 640, 2048
freqs = np.fft.rfftfreq(nfft, 1 / sr); band = (freqs >= 30) & (freqs <= 400)
win = np.hanning(nfft).astype(np.float32)
nfr = (len(a) - nfft) // hop + 1
S = np.empty((band.sum(), nfr), np.float32)
CH = 3000                                          # frames per chunk (120 s)
for c0 in range(0, nfr, CH):
    c1 = min(nfr, c0 + CH)
    seg = np.asarray(a[c0 * hop:(c1 - 1) * hop + nfft], dtype=np.float32) / 32768
    idx = np.arange(c1 - c0)[:, None] * hop + np.arange(nfft)[None, :]
    X = np.fft.rfft(seg[idx] * win, axis=1)[:, band]
    S[:, c0:c1] = np.log1p(np.abs(X) * 100).T
S -= S.mean(1, keepdims=True)
fps = sr / hop


def ts(t):
    return f"{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


for k, spec in enumerate(sys.argv[3].split(",")):
    t0, L = map(float, spec.split(":")); i0, n = int(t0 * fps), int(L * fps)
    T = S[:, i0:i0 + n]; T = (T - T.mean()) / (T.std() + 1e-9)
    N = S.shape[1] - n + 1
    num = np.zeros(N, np.float64)
    for b in range(S.shape[0]):
        num += fftconvolve(S[b].astype(np.float64), T[b, ::-1].astype(np.float64), mode="valid")
    cs = np.concatenate([[0], np.cumsum(S.sum(0, dtype=np.float64))])
    cs2 = np.concatenate([[0], np.cumsum((S.astype(np.float64) ** 2).sum(0))])
    cnt = n * S.shape[0]
    mu = (cs[n:] - cs[:-n]) / cnt; var = (cs2[n:] - cs2[:-n]) / cnt - mu ** 2
    ncc = num / (cnt * np.sqrt(np.maximum(var, 1e-12)))   # sum(T)=0, so the window mean drops out
    with open(f"{out}_{k}.csv", "w") as o:
        o.write("time_s,ncc\n")
        for j in range(0, N, 5): o.write(f"{j / fps:.2f},{ncc[j]:.3f}\n")
    print(f"template {k}: {ts(t0)} +{L}s")
    picked = []
    for j in np.argsort(-ncc):
        if ncc[j] < 0.3 or len(picked) >= 25: break
        if all(abs(j - p) > n for p in picked): picked.append(j)
    for j in sorted(picked): print(f"  {ts(j / fps)} ncc={ncc[j]:.2f}")
