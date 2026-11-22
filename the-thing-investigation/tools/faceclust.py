#!/usr/bin/env python3
"""Tracklets and identity clusters from the face pass (runs on the analysis VM).

Usage: faceclust.py <faces_dir> <shots.csv> <out_dir> [cos_dist_threshold=0.55]

1. Loads <faces_dir>/part*_faces.csv + part*_emb.f16 (row-aligned).
2. Tracklets: inside one shot, detections in consecutive frames are linked greedily by box IoU
   >= 0.3 (gap up to 2 frames). Tracklets shorter than 6 detections are dropped as noise.
3. Tracklet embedding = re-normalised mean of L2-normalised SFace embeddings.
4. Average-linkage agglomerative clustering on cosine distance, cut at the threshold.
Outputs in <out_dir>:
  detections.csv  original rows + det_id, tracklet (-1 = dropped)
  tracklets.csv   tid,shot,f0,f1,n,score,iod,face_y,cluster
  montage_XX.jpg  12 clusters per image, up to 10 crops per cluster spread over the film,
                  each labelled with cluster id, tracklet count and first/last time
"""
import sys, glob, csv, os, numpy as np, cv2
from scipy.cluster.hierarchy import linkage, fcluster

fdir, shots_csv, out = sys.argv[1], sys.argv[2], sys.argv[3]
thr = float(sys.argv[4]) if len(sys.argv) > 4 else 0.55
os.makedirs(out, exist_ok=True)
rows, embs = [], []
for p in sorted(glob.glob(f"{fdir}/part*_faces.csv")):
    pre = p[:-len("_faces.csv")]
    r = list(csv.DictReader(open(p)))
    e = np.fromfile(pre + "_emb.f16", np.float16).reshape(-1, 128)
    n = min(len(r), len(e)); rows += r[:n]; embs.append(e[:n].astype(np.float32))
E = np.concatenate(embs); E /= np.linalg.norm(E, axis=1, keepdims=True) + 1e-9
F = np.array([int(r["frame"]) for r in rows])
B = np.array([[float(r[k]) for k in ("x", "y", "w", "h")] for r in rows])
order = np.argsort(F, kind="stable"); F, B, E = F[order], B[order], E[order]; rows = [rows[i] for i in order]
shot_start = np.array([int(r["start_frame"]) for r in csv.DictReader(open(shots_csv))])
shot_of = np.searchsorted(shot_start, F, side="right") - 1


def iou(a, b):
    x0, y0 = max(a[0], b[0]), max(a[1], b[1]); x1, y1 = min(a[0]+a[2], b[0]+b[2]), min(a[1]+a[3], b[1]+b[3])
    i = max(0, x1-x0) * max(0, y1-y0); return i / (a[2]*a[3] + b[2]*b[3] - i + 1e-9)


trk = -np.ones(len(F), int); tracks = []      # each: [last_det_index, shot]
active = []
by_frame = {}
for i, f in enumerate(F): by_frame.setdefault(f, []).append(i)
for f in sorted(by_frame):
    active = [t for t in active if f - F[tracks[t][-1]] <= 3 and shot_of[tracks[t][-1]] == shot_of[by_frame[f][0]]]
    used = set()
    for i in sorted(by_frame[f], key=lambda k: -float(rows[k]["score"])):
        best, bv = None, 0.3
        for t in active:
            if t in used: continue
            v = iou(B[tracks[t][-1]], B[i])
            if v >= bv: best, bv = t, v
        if best is None:
            tracks.append([i]); best = len(tracks) - 1; active.append(best)
        else:
            tracks[best].append(i)
        used.add(best); trk[i] = best
keep = [t for t in range(len(tracks)) if len(tracks[t]) >= 6]
remap = {t: k for k, t in enumerate(keep)}
trk = np.array([remap.get(t, -1) for t in trk])
T = [tracks[t] for t in keep]
TE = np.stack([E[ix].mean(0) for ix in T]); TE /= np.linalg.norm(TE, axis=1, keepdims=True) + 1e-9
Z = linkage(TE, method="average", metric="cosine")
cl = fcluster(Z, t=thr, criterion="distance")
sizes = np.bincount(cl)
rank = {c: k for k, c in enumerate(sorted(set(cl), key=lambda c: -sizes[c]))}
cl = np.array([rank[c] for c in cl])

with open(f"{out}/tracklets.csv", "w") as o:
    o.write("tid,shot,f0,f1,n,score,iod,face_y,cluster\n")
    for k, ix in enumerate(T):
        sc = np.mean([float(rows[i]["score"]) for i in ix]); io = np.mean([float(rows[i]["iod"]) for i in ix])
        fy = np.mean([float(rows[i]["face_y"]) for i in ix])
        o.write(f"{k},{shot_of[ix[0]]+1},{F[ix[0]]},{F[ix[-1]]},{len(ix)},{sc:.3f},{io:.1f},{fy:.1f},{cl[k]}\n")
with open(f"{out}/detections.csv", "w") as o:
    keys = list(rows[0].keys()); o.write(",".join(keys) + ",tracklet,cluster\n")
    for i, r in enumerate(rows):
        o.write(",".join(r[k] for k in keys) + f",{trk[i]},{cl[trk[i]] if trk[i] >= 0 else -1}\n")


def ts(f):
    s = f * 1001 / 24000; return f"{int(s//3600)}:{int(s%3600//60):02d}:{int(s%60):02d}"


crop_index = {}
for p in glob.glob(f"{fdir}/part*_crops/*/*.jpg"):
    b = os.path.basename(p)[:-4]; fr, k = b.split("_"); crop_index.setdefault(int(fr), []).append(p)
ncl = cl.max() + 1; per = 12; S = 96
for m in range(0, ncl, per):
    sheet = np.full((per * (S + 18), 10 * S, 3), 40, np.uint8)
    for j, c in enumerate(range(m, min(ncl, m + per))):
        tids = [k for k in range(len(T)) if cl[k] == c]
        pick = [tids[int(q)] for q in np.linspace(0, len(tids) - 1, min(10, len(tids)))]
        f0, f1 = F[T[tids[0]][0]], F[T[tids[-1]][-1]]
        y = j * (S + 18)
        cv2.putText(sheet, f"C{c:03d} n={len(tids)} {ts(f0)}-{ts(f1)}", (3, y + 13), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1)
        for q, k in enumerate(pick):
            ix = T[k]; best = max(ix, key=lambda i: float(rows[i]["score"]) * float(rows[i]["iod"]))
            fr = F[best]; cands = crop_index.get(int(fr), [])
            # the crop file index k is the detection order inside the frame; match by box rank
            same = [i for i in by_frame[fr]]
            kk = same.index(best) if best in same else 0
            path = [p for p in cands if p.endswith(f"_{kk}.jpg")]
            if not path: continue
            im = cv2.resize(cv2.imread(path[0]), (S, S))
            cv2.putText(im, ts(fr), (2, S - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.33, (255, 255, 0), 1)
            sheet[y + 18:y + 18 + S, q * S:(q + 1) * S] = im
    cv2.imwrite(f"{out}/montage_{m // per:02d}.jpg", sheet, [cv2.IMWRITE_JPEG_QUALITY, 85])
print(f"detections {len(F)} tracklets {len(T)} clusters {ncl} (>=5 tracklets: {(np.bincount(cl) >= 5).sum()})")
