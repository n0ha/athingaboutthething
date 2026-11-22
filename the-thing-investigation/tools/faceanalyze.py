#!/usr/bin/env python3
"""Character presence and eye catchlight statistics from labelled face clusters.

Usage: faceanalyze.py <clust_dir> <labels.json> <out_dir>

labels.json: {"<cluster id>": "MacReady", ...}; unlisted clusters are "unknown".
Outputs:
  presence.csv     character,start,end,dur_s,tracklets  (on-screen face intervals; tracklets of
                   one character closer than 3 s are merged)
  catch_tracks.csv per tracklet with a usable face (median IOD >= 35 px):
                   tid,character,cluster,f0,t0,t1,n,iod,face_y,catch,spec_frac
                   catch     = median over frames of max(right,left) eye (peak - base)
                   spec_frac = share of frames in which at least one eye has spec > 0
Interpretation is left to the analyst: catchlights depend on lighting, angle, eye opening
and face size; compare like with like (same scene, same lighting).
"""
import sys, csv, json, os, numpy as np

cdir, lab, out = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(out, exist_ok=True)
labels = {int(k): v for k, v in json.load(open(lab)).items()}
tr = list(csv.DictReader(open(f"{cdir}/tracklets.csv")))
F = 1001 / 24000


def ts(s):
    return f"{int(s // 3600):02d}:{int(s % 3600 // 60):02d}:{s % 60:06.3f}"


by_char = {}
for t in tr:
    c = labels.get(int(t["cluster"]), "unknown")
    by_char.setdefault(c, []).append((int(t["f0"]), int(t["f1"])))
with open(f"{out}/presence.csv", "w") as o:
    o.write("character,start,end,dur_s,tracklets\n")
    for c, iv in sorted(by_char.items()):
        iv.sort(); cur = [iv[0][0], iv[0][1], 1]
        for a, b in iv[1:]:
            if a * F - cur[1] * F <= 3.0:
                cur[1] = max(cur[1], b); cur[2] += 1
            else:
                o.write(f"{c},{ts(cur[0]*F)},{ts(cur[1]*F)},{(cur[1]-cur[0])*F:.1f},{cur[2]}\n"); cur = [a, b, 1]
        o.write(f"{c},{ts(cur[0]*F)},{ts(cur[1]*F)},{(cur[1]-cur[0])*F:.1f},{cur[2]}\n")

det = {}
for r in csv.DictReader(open(f"{cdir}/detections.csv")):
    k = int(r["tracklet"])
    if k < 0: continue
    rp, rb, lp, lb = (float(r[x]) for x in ("r_peak", "r_base", "l_peak", "l_base"))
    cvals = [p - b for p, b in ((rp, rb), (lp, lb)) if p >= 0]
    spec = (int(r["r_spec"]) > 0) or (int(r["l_spec"]) > 0)
    det.setdefault(k, []).append((max(cvals) if cvals else np.nan, spec, float(r["iod"]), float(r["face_y"])))
with open(f"{out}/catch_tracks.csv", "w") as o:
    o.write("tid,character,cluster,f0,t0,t1,n,iod,face_y,catch,spec_frac\n")
    for t in tr:
        k = int(t["tid"]); d = det.get(k, [])
        if not d: continue
        iod = np.median([x[2] for x in d])
        if iod < 35: continue
        c = labels.get(int(t["cluster"]), "unknown")
        o.write(f"{k},{c},{t['cluster']},{t['f0']},{ts(int(t['f0'])*F)},{ts(int(t['f1'])*F)},{len(d)},"
                f"{iod:.0f},{np.median([x[3] for x in d]):.0f},{np.nanmedian([x[0] for x in d]):.0f},"
                f"{np.mean([x[1] for x in d]):.2f}\n")
print("ok")
