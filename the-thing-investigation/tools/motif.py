#!/usr/bin/env python3
"""Find recurrences of a musical passage (template) across the film's mono mix.
Log-magnitude spectrogram 30-400 Hz (bass/pulse register, mostly free of speech formants),
25 frames/s; normalised cross-correlation of the template patch against every offset.
Usage: motif.py <wav16k> <tmpl_start_s> <tmpl_len_s> <out.csv>"""
import sys, numpy as np
from scipy.io import wavfile
from scipy.signal import stft
sr, a = wavfile.read(sys.argv[1]); a = a.astype(np.float32)/32768
t0, L = float(sys.argv[2]), float(sys.argv[3])
f, t, Z = stft(a, fs=sr, nperseg=2048, noverlap=2048-640)  # hop 40 ms
band = (f >= 30) & (f <= 400)
S = np.log1p(np.abs(Z[band])*100).astype(np.float32)  # bands x frames
S = (S - S.mean(1, keepdims=True))
fps = sr/640; i0 = int(t0*fps); n = int(L*fps)
T = S[:, i0:i0+n]; T = (T - T.mean())/ (T.std()+1e-9)
N = S.shape[1]-n+1; sc = np.zeros(N, np.float32)
# sliding NCC via per-offset computation in chunks
from numpy.lib.stride_tricks import sliding_window_view
W = sliding_window_view(S, n, axis=1)  # bands x N+1 x n
for s in range(0, N, 2000):
    w = W[:, s:s+2000, :]                        # bands x k x n
    m = w.mean(axis=(0, 2), keepdims=True); sd = w.std(axis=(0, 2), keepdims=True)+1e-9
    sc[s:s+w.shape[1]] = (((w-m)/sd) * T[:, None, :]).mean(axis=(0, 2))
with open(sys.argv[4], "w") as o:
    o.write("time_s,ncc\n")
    for k in range(0, N, 5): o.write(f"{k/fps:.2f},{sc[k]:.3f}\n")
order = np.argsort(-sc); picked = []
for k in order:
    if sc[k] < 0.35: break
    if all(abs(k-p) > n for p in picked): picked.append(k)
    if len(picked) >= 25: break
for k in sorted(picked):
    tt = k/fps; print(f"{int(tt//3600):02d}:{int(tt%3600//60):02d}:{tt%60:05.2f} ncc={sc[k]:.2f}")
