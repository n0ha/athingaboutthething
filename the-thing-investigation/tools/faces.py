#!/usr/bin/env python3
"""Whole-film face pass (meant for the analysis VM, not the laptop).

Usage: faces.py <film> <yunet.onnx> <sface.onnx> <frame_from> <frame_to> <out_prefix>

For every frame in [frame_from, frame_to): YuNet face detection on a half-size copy, landmarks
mapped back to full resolution (1920x816), SFace 128-d embedding from the aligned full-res crop,
and catchlight metrics measured in full-res luma around both eye landmarks.

Streamed output, constant memory (safe to stop; everything written so far is usable):
  <out>_faces.csv   one row per detection (columns below)
  <out>_emb.f16     raw float16 embeddings, 128 per detection, same order as the CSV
  <out>_frames.csv  frame,mean_luma,n_faces  (lets the frame alignment be checked against
                    work/framestats.npz, which was decoded independently)
  <out>_crops/NNN/<frame>_<k>.jpg  112x112 aligned face crop of every detection

Frame index f <-> time f*1001/24000 s (constant 23.976 fps, frame 0 at t=0).

Catchlight metrics (Y = Rec.709 luma, full res, ROI = square of side 0.4*IOD centred on an eye
landmark; IOD = inter-ocular distance in px):
  peak  = max of the 3x3-box-blurred luma in the ROI (blur suppresses film grain)
  base  = median luma of the ROI
  spec  = number of ROI pixels with blurred Y >= max(base + 45, 1.6*face_y)
  face_y = median luma of the central half of the face box
A catchlight is a small cluster of near-white pixels: high peak-base, spec > 0. The metric is
optical. Any wet cornea reflects a light in front of it, so differences describe lighting and
camera angle unless they persist when lighting is controlled for.
"""
import sys, os, subprocess, numpy as np, cv2

film, ypath, spath = sys.argv[1:4]
f0, f1 = int(sys.argv[4]), int(sys.argv[5])
out = sys.argv[6]
W, H = 1920, 816
DW, DH = 960, 408
cv2.setNumThreads(1)
det = cv2.FaceDetectorYN.create(ypath, "", (DW, DH), 0.6, 0.3, 50)
rec = cv2.FaceRecognizerSF.create(spath, "")
t0 = max(0.0, (f0 - 0.5) * 1001 / 24000)
cmd = ["ffmpeg", "-v", "error", "-threads", "1", "-ss", f"{t0:.6f}", "-i", film, "-map", "0:v:0",
       "-fps_mode", "passthrough", "-frames:v", str(f1 - f0), "-f", "rawvideo", "-pix_fmt", "bgr24", "-"]
p = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=W * H * 3 * 2)
fc = open(out + "_faces.csv", "w")
fc.write("frame,time,score,x,y,w,h,rex,rey,lex,ley,nx,ny,iod,face_y,"
         "r_peak,r_base,r_spec,l_peak,l_base,l_spec\n")
fe = open(out + "_emb.f16", "wb")
ff = open(out + "_frames.csv", "w"); ff.write("frame,mean_luma,n_faces\n")
crops = out + "_crops"
nbytes = W * H * 3
f = f0


def eye_metrics(Yb, Y, cx, cy, half, face_y):
    x0, x1 = int(round(cx - half)), int(round(cx + half)) + 1
    y0, y1 = int(round(cy - half)), int(round(cy + half)) + 1
    if x0 < 0 or y0 < 0 or x1 > W or y1 > H or x1 - x0 < 3:
        return -1, -1, -1
    rb = Yb[y0:y1, x0:x1]; base = float(np.median(Y[y0:y1, x0:x1])); peak = float(rb.max())
    spec = int((rb >= max(base + 45, 1.6 * face_y)).sum())
    return peak, base, spec


while f < f1:
    buf = p.stdout.read(nbytes)
    if len(buf) < nbytes:
        break
    img = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
    Y = (0.0722 * img[..., 0] + 0.7152 * img[..., 1] + 0.2126 * img[..., 2]).astype(np.float32)
    small = cv2.resize(img, (DW, DH), interpolation=cv2.INTER_AREA)
    _, faces = det.detect(small)
    n = 0 if faces is None else len(faces)
    ff.write(f"{f},{Y.mean():.2f},{n}\n")
    if n:
        Yb = cv2.blur(Y, (3, 3))
        for k, r in enumerate(faces):
            row = r.copy(); row[:14] *= 2.0              # back to full-res coordinates
            x, y, w, h = row[:4]; rex, rey, lex, ley, nx, ny = row[4:10]
            iod = float(np.hypot(lex - rex, ley - rey))
            fx0, fy0 = int(max(0, x + w / 4)), int(max(0, y + h / 4))
            fx1, fy1 = int(min(W, x + 3 * w / 4)), int(min(H, y + 3 * h / 4))
            face_y = float(np.median(Y[fy0:fy1, fx0:fx1])) if fx1 > fx0 and fy1 > fy0 else -1
            half = max(1.5, 0.2 * iod)
            rm = eye_metrics(Yb, Y, rex, rey, half, face_y)
            lm = eye_metrics(Yb, Y, lex, ley, half, face_y)
            try:
                al = rec.alignCrop(img, row)
                emb = rec.feature(al).astype(np.float16).reshape(-1)
                d = f"{crops}/{f // 2000:03d}"; os.makedirs(d, exist_ok=True)
                cv2.imwrite(f"{d}/{f}_{k}.jpg", al, [cv2.IMWRITE_JPEG_QUALITY, 85])
            except cv2.error:
                emb = np.zeros(128, np.float16)
            fe.write(emb.tobytes())
            fc.write(f"{f},{f*1001/24000:.3f},{row[14]:.3f},{x:.0f},{y:.0f},{w:.0f},{h:.0f},"
                     f"{rex:.1f},{rey:.1f},{lex:.1f},{ley:.1f},{nx:.1f},{ny:.1f},{iod:.1f},{face_y:.1f},"
                     f"{rm[0]:.0f},{rm[1]:.0f},{rm[2]},{lm[0]:.0f},{lm[1]:.0f},{lm[2]}\n")
    f += 1
    if f % 500 == 0:
        fc.flush(); fe.flush(); ff.flush()
        with open(out + "_progress", "w") as pr:
            pr.write(f"{f}\n")
fc.close(); fe.close(); ff.close()
with open(out + "_progress", "w") as pr:
    pr.write(f"{f} done\n")
