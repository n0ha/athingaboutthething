#!/usr/bin/env python3
"""Per-second audio profile of the film (memory-safe, run on the VM).

Usage: audio2.py <music_lr16k.wav> <dialog_fc16k.wav> <out.csv>

music_lr = mono downmix of the front L/R channels (score and effects, little dialogue),
dialog_fc = centre channel (dialogue). Both 16 kHz mono PCM, read via mmap in chunks.

Columns: t (s), lr_db, fc_db (RMS dBFS per second),
         pulse, lag (s): slow periodic bass pulse ("heartbeat") in the L/R channels:
         30-150 Hz band-pass -> rectified envelope at 100 Hz -> in 8 s windows (hop 1 s) the
         normalised autocorrelation peak for lags 0.30-2.00 s (pulse = peak height, lag = its period).
Exploratory: engines, wind or footsteps can also pulse; hits must be checked against the picture.
"""
import sys, numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt, sosfilt_zi

lr_p, fc_p, out = sys.argv[1:4]
sr, lr = wavfile.read(lr_p, mmap=True); sr2, fc = wavfile.read(fc_p, mmap=True)
assert sr == sr2 == 16000
n = min(len(lr), len(fc)); secs = n // sr
bp = butter(4, [30, 150], btype="band", fs=sr, output="sos")
lp = butter(2, 10, fs=sr, output="sos")
zi_b = sosfilt_zi(bp) * 0; zi_l = sosfilt_zi(lp) * 0
env = np.zeros(secs * 100, np.float32)
lr_db = np.zeros(secs, np.float32); fc_db = np.zeros(secs, np.float32)
CH = 60  # seconds per chunk
for s0 in range(0, secs, CH):
    s1 = min(secs, s0 + CH)
    x = np.asarray(lr[s0 * sr:s1 * sr], np.float32) / 32768
    y = np.asarray(fc[s0 * sr:s1 * sr], np.float32) / 32768
    lr_db[s0:s1] = 10 * np.log10((x.reshape(-1, sr) ** 2).mean(1) + 1e-10)
    fc_db[s0:s1] = 10 * np.log10((y.reshape(-1, sr) ** 2).mean(1) + 1e-10)
    b, zi_b = sosfilt(bp, x, zi=zi_b)
    e, zi_l = sosfilt(lp, np.abs(b), zi=zi_l)
    env[s0 * 100:s1 * 100] = e.reshape(-1, sr // 100).mean(1)
W, L0, L1 = 800, 30, 200
pulse = np.zeros(secs, np.float32); lag = np.zeros(secs, np.float32)
for t in range(secs):
    a = max(0, t * 100 - W // 2); seg = env[a:a + W]
    if len(seg) < W: continue
    seg = seg - seg.mean(); den = (seg ** 2).sum()
    if den <= 0: continue
    ac = np.array([(seg[:-k] * seg[k:]).sum() / den for k in range(L0, L1)])
    # a genuine pulse shows a peak, not just slow decay: require a local maximum
    k = int(np.argmax(ac));
    if 0 < k < len(ac) - 1 and ac[k] > ac[k - 1] and ac[k] > ac[k + 1]:
        pulse[t] = ac[k]; lag[t] = (k + L0) / 100
with open(out, "w") as o:
    o.write("t,lr_db,fc_db,pulse,lag\n")
    for t in range(secs):
        o.write(f"{t},{lr_db[t]:.1f},{fc_db[t]:.1f},{pulse[t]:.3f},{lag[t]:.2f}\n")
print("seconds", secs)
