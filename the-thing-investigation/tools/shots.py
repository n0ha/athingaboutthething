#!/usr/bin/env python3
"""Shot boundary detection from work/framestats.npz + one representative frame per shot.
Usage: shots.py detect   -> work/shots.csv
       shots.py thumbs   -> work/shot_thumbs/S####.jpg (middle frame of each shot, 480 px)
       shots.py sheets A B prefix  -> contact sheets of shots whose start lies in [A,B] seconds
Cut rule: Bhattacharyya HSV distance >= 0.30 and local maximum within +-4 frames, or
luma MAD >= 28 with distance >= 0.18. Fades/dissolves may be split or merged; the shot list is
a navigation aid, every evidential timestamp is re-read from real decoded frames."""
import sys, csv, os, subprocess, numpy as np
FPS = 24000/1001
def ts(fr):
    t = fr/FPS; h=int(t//3600); m=int(t%3600//60); s=t%60
    return f"{h:02d}:{m:02d}:{s:06.3f}"
root = os.path.join(os.path.dirname(__file__), "..", "..", "work")
root = os.path.abspath(root)
cmd = sys.argv[1]
if cmd == "detect":
    d = np.load(f"{root}/framestats.npz"); h = d["hdist"]; mad = d["mad"]; L = d["luma"]
    n = len(h); cuts = [0]
    for i in range(1, n):
        lo, hi = max(1, i-4), min(n, i+5)
        if (h[i] >= 0.30 and h[i] == h[lo:hi].max()) or (mad[i] >= 28 and h[i] >= 0.18 and h[i] == h[lo:hi].max()):
            if i - cuts[-1] >= 6: cuts.append(i)
    cuts.append(n)
    with open(f"{root}/shots.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["shot","start_frame","end_frame","start","end","dur_s","mid_frame","mean_luma"])
        for k in range(len(cuts)-1):
            a, b = cuts[k], cuts[k+1]-1; mid = (a+b)//2
            w.writerow([f"S{k+1:04d}", a, b, ts(a), ts(b), round((b-a+1)/FPS, 2), mid, round(float(L[a:b+1].mean()),1)])
    print("shots:", len(cuts)-1, "frames:", n)
elif cmd == "thumbs":
    rows = list(csv.DictReader(open(f"{root}/shots.csv")))
    os.makedirs(f"{root}/shot_thumbs", exist_ok=True)
    mids = [int(r["mid_frame"]) for r in rows]
    # one sequential decode, keep only the wanted frames (by decoded index)
    W, H = 480, 204
    p = subprocess.Popen(["ffmpeg","-v","error","-i",f"{root}/film.mkv","-map","0:v:0","-vf",f"scale={W}:{H}",
                          "-pix_fmt","rgb24","-f","rawvideo","-"], stdout=subprocess.PIPE, bufsize=W*H*3*32)
    from PIL import Image
    want = dict((m, r["shot"]) for m, r in zip(mids, rows)); i = 0
    while True:
        buf = p.stdout.read(W*H*3)
        if len(buf) < W*H*3: break
        if i in want: Image.frombytes("RGB", (W, H), buf).save(f"{root}/shot_thumbs/{want[i]}.jpg", quality=88)
        i += 1
    print("decoded", i)
elif cmd == "sheets":
    from PIL import Image, ImageDraw, ImageFont
    A, B, prefix = float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
    cols, rows_n, tw, th = 5, 6, 384, 163
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 15)
    rows = [r for r in csv.DictReader(open(f"{root}/shots.csv")) if A <= int(r["start_frame"])/FPS < B]
    per = cols*rows_n; out = []
    for s in range(0, len(rows), per):
        chunk = rows[s:s+per]; sheet = Image.new("RGB", (cols*tw + (cols+1)*3, rows_n*(th+18) + (rows_n+1)*3), (60,60,60))
        dr = ImageDraw.Draw(sheet)
        for j, r in enumerate(chunk):
            x = 3 + (j % cols)*(tw+3); y = 3 + (j//cols)*(th+21)
            im = Image.open(f"{root}/shot_thumbs/{r['shot']}.jpg").resize((tw, th))
            sheet.paste(im, (x, y+18))
            dr.text((x+2, y), f"{r['shot']} mid {ts(int(r['mid_frame']))[:-2]} f{r['mid_frame']} ({r['dur_s']}s)", fill=(255,255,0), font=font)
        fn = f"{prefix}_{s//per+1:02d}.jpg"; sheet.save(fn, quality=85); out.append(fn)
    print("\n".join(out))
