#!/usr/bin/env python3
"""Exploratory detector of a slow periodic low-frequency pulse (the score's bass 'heartbeat').
Low band 30-90 Hz of the mono mix -> 50 Hz envelope -> autocorrelation in 6 s windows (hop 2 s);
pulse_score = max normalised autocorrelation for lags 0.6-2.5 s. Output CSV time,score,lag,rms_db.
Exploratory only: periodic engine/wind sounds can score too; every hit must be checked."""
import sys, numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfiltfilt, resample_poly
sr, a = wavfile.read(sys.argv[1]); a = a.astype(np.float32)/32768
sos = butter(4, [30, 90], btype="band", fs=sr, output="sos")
lo = sosfiltfilt(sos, a); env = np.abs(lo)
env = resample_poly(env, 1, sr//50)  # 50 Hz envelope
fs = 50; win, hop = 6*fs, 2*fs
out = open(sys.argv[2], "w"); out.write("time_s,score,lag_s,rms_db\n")
for s in range(0, len(env)-win, hop):
    x = env[s:s+win]; rms = float(np.sqrt((x**2).mean())+1e-9); x = x - x.mean()
    ac = np.correlate(x, x, "full")[win-1:]; ac = ac/(ac[0]+1e-12)
    l0, l1 = int(0.6*fs), int(2.5*fs); k = l0 + int(np.argmax(ac[l0:l1]))
    out.write(f"{(s+win/2)/fs:.1f},{ac[k]:.3f},{k/fs:.2f},{20*np.log10(rms):.1f}\n")
