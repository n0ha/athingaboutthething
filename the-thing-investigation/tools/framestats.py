#!/usr/bin/env python3
"""Per-frame statistics for the whole film (decoded by ffmpeg at 256x109).
Output: work/framestats.npz with arrays
  luma  - mean luma per frame (0..255)
  rgb   - mean R,G,B per frame
  hdist - Bhattacharyya distance of HSV histogram vs previous frame
  mad   - mean absolute luma difference vs previous frame
Frame index i corresponds to time i*1001/24000 s (constant 23.976 fps stream)."""
import subprocess, sys, numpy as np, cv2
src, out = sys.argv[1], sys.argv[2]
W, H = 256, 109
cmd = ["ffmpeg", "-v", "error", "-i", src, "-map", "0:v:0", "-vf", f"scale={W}:{H}:flags=area",
       "-pix_fmt", "bgr24", "-f", "rawvideo", "-"]
p = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=W*H*3*64)
luma, rgb, hdist, mad = [], [], [], []
prev_h = prev_g = None
n = 0
while True:
    buf = p.stdout.read(W*H*3)
    if len(buf) < W*H*3: break
    f = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
    g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV)
    h = cv2.calcHist([hsv], [0, 1, 2], None, [16, 4, 8], [0, 180, 0, 256, 0, 256])
    cv2.normalize(h, h)
    luma.append(g.mean()); rgb.append(f.reshape(-1, 3).mean(0)[::-1])
    if prev_h is None: hdist.append(1.0); mad.append(255.0)
    else:
        hdist.append(cv2.compareHist(prev_h, h, cv2.HISTCMP_BHATTACHARYYA))
        mad.append(np.abs(g.astype(np.int16) - prev_g).mean())
    prev_h, prev_g = h, g.astype(np.int16)
    n += 1
    if n % 20000 == 0: print(n, file=sys.stderr, flush=True)
np.savez_compressed(out, luma=np.array(luma, np.float32), rgb=np.array(rgb, np.float32),
                    hdist=np.array(hdist, np.float32), mad=np.array(mad, np.float32))
print("frames", n)
