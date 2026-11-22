#!/usr/bin/env python3
"""Specular catchlight measurement in hand-placed eye regions.
Usage: catchlight.py <frame.png> <label> x,y,w,h [x,y,w,h ...] -> prints metrics, writes <frame>_eyes.png
Metrics per eye ROI (full-res pixel coords): Y = Rec.709 luma.
  peak   = 99.7th percentile of Y inside ROI
  face   = median Y of the ROI expanded 3x (skin/surround reference)
  ratio  = peak / face ; spec_px = pixels with Y >= max(face*2.2, face+60)
A visible catchlight gives a small cluster of near-white pixels (high ratio, spec_px > 0).
The measure is optical only: any wet cornea (human or imitation) reflects a light source in
front of it; differences say something about lighting/camera angle, not biology."""
import sys, cv2, numpy as np
img = cv2.imread(sys.argv[1]); label = sys.argv[2]
Y = (0.0722*img[...,0] + 0.7152*img[...,1] + 0.2126*img[...,2]).astype(np.float32)
H, W = Y.shape; crops = []
for k, spec in enumerate(sys.argv[3:]):
    x, y, w, h = map(int, spec.split(","))
    roi = Y[y:y+h, x:x+w]
    X0, Y0 = max(0, x-w), max(0, y-h); X1, Y1 = min(W, x+2*w), min(H, y+2*h)
    face = float(np.median(Y[Y0:Y1, X0:X1])); peak = float(np.percentile(roi, 99.7))
    thr = max(face*2.2, face+60); spec_px = int((roi >= thr).sum())
    print(f"{label} eye{k+1} roi={spec} peak={peak:.0f} face={face:.0f} ratio={peak/max(face,1):.2f} spec_px={spec_px} max={roi.max():.0f}")
    c = cv2.resize(img[y:y+h, x:x+w], (w*8, h*8), interpolation=cv2.INTER_NEAREST)
    cv2.putText(c, f"eye{k+1} r={peak/max(face,1):.2f} n={spec_px}", (4, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,255), 1)
    crops.append(c)
if crops:
    hmax = max(c.shape[0] for c in crops)
    crops = [cv2.copyMakeBorder(c, 0, hmax-c.shape[0], 0, 4, cv2.BORDER_CONSTANT) for c in crops]
    cv2.imwrite(sys.argv[1].rsplit(".",1)[0] + "_eyes.png", np.hstack(crops))
