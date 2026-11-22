#!/usr/bin/env python3
"""Builds web/data.json for the "A Thing About The Thing" site from the analysis outputs.
Run with the project venv: .venv/bin/python web/build_data.py"""
import csv, json, re, collections
import numpy as np

B = str(__import__("pathlib").Path(__file__).resolve().parents[1])  # project root
S = f"{B}/work/segments"
F = 1001 / 24000


def sec(ts):
    h, m, s = ts.split(":"); return int(h) * 3600 + int(m) * 60 + float(s)


CH = ["MacReady", "Childs", "Nauls", "Windows", "Palmer", "Garry", "Blair", "Copper", "Norris", "Clark", "Bennings", "Fuchs"]
ROLE = {
    "MacReady": ("helicopter pilot", "pilot vrtuľníka"), "Childs": ("mechanic", "mechanik"),
    "Nauls": ("cook", "kuchár"), "Windows": ("radio operator", "rádiooperátor"),
    "Palmer": ("assistant mechanic", "pomocný mechanik"), "Garry": ("station commander", "veliteľ stanice"),
    "Blair": ("biologist", "biológ"), "Copper": ("doctor", "lekár"), "Norris": ("geologist", "geológ"),
    "Clark": ("dog handler", "psovod"), "Bennings": ("meteorologist", "meteorológ"), "Fuchs": ("biologist's assistant", "Blairov asistent"),
}
COLOR = {"MacReady": "#f2c879", "Childs": "#6fb7ff", "Nauls": "#8ee6c4", "Windows": "#c9a4ff", "Palmer": "#ff9a76",
         "Garry": "#d8dee6", "Blair": "#f7e36b", "Copper": "#e59ad1", "Norris": "#a7d36f", "Clark": "#c7b08a",
         "Bennings": "#ff7f7f", "Fuchs": "#7fe0ff"}

# scene -> map node (manual, from the analysts' location notes)
NODE = {
 "S1-01": "none", "S1-02": "glacier", "S1-03": "yard", "S1-04": "rec", "S1-05": "shack", "S1-06": "yard", "S1-07": "yard",
 "S1-08": "yard", "S1-09": "infirmary", "S1-10": "radio", "S1-11": "rec", "S1-12": "yard", "S1-13": "helipad", "S1-14": "rec",
 "S1-15": "helipad", "S1-16": "quarters", "S1-17": "norway", "S1-18": "norway", "S1-19": "norway", "S1-20": "helipad", "S1-21": "lab",
 "S2-01": "lab", "S2-02": "radio", "S2-03": "lab", "S2-04": "yard", "S2-05": "quarters", "S2-06": "rec", "S2-07": "kennel",
 "S2-08": "kennel", "S2-09": "kitchen", "S2-10": "kennel", "S2-11": "kennel", "S2-12": "yard", "S2-13": "lab", "S2-14": "kennel",
 "S2-15": "office", "S2-16": "crater", "S2-17": "yard", "S2-18": "rec", "S2-19": "lab", "S2-20": "quarters",
 "3.1": "quarters", "3.2": "store", "3.3": "store", "3.4": "yard", "3.5": "store", "3.6": "yard", "3.7": "yard", "3.8": "store",
 "3.9": "yard", "3.10": "store", "3.11": "yard", "3.12": "helipad", "3.13": "radio", "3.14": "kennel", "3.15": "yard",
 "3.16": "toolshed", "3.17": "yard", "3.18": "infirmary", "3.19": "office",
 "4-01": "yard", "4-02": "rec", "4-03": "office", "4-04": "lab", "4-05": "lab", "4-06": "rec", "4-07": "toolshed", "4-08": "yard",
 "4-09": "shack", "4-10": "rec", "4-11": "entrance", "4-12": "store", "4-13": "infirmary", "4-14": "rec",
 "S5-01": "rec", "S5-02": "rec", "S5-03": "rec", "S5-04": "entrance", "S5-05": "yard", "S5-06": "tunnel", "S5-07": "entrance",
 "S5-08": "toolshed", "S5-09": "yard", "S5-10": "under", "S5-11": "under", "S5-12": "under", "S5-13": "under", "S5-14": "yard",
}
KEYS = [("rádio", "radio"), ("radio", "radio"), ("rec room", "rec"), ("rekreač", "rec"), ("zviazan", "rec"), ("kôlň", "toolshed"),
        ("toolshed", "toolshed"), ("chatr", "shack"), ("chatk", "shack"), ("laborat", "lab"), ("kuchyň", "kitchen"),
        ("ošetrov", "infirmary"), ("psinec", "kennel"), ("izb", "quarters"), ("sklad", "store"), ("vonku", "yard"),
        ("tunel", "tunnel"), ("generátor", "under"), ("podzem", "under")]

scenes = collections.OrderedDict()
for n in range(1, 6):
    for r in csv.DictReader(open(f"{S}/seg{n}_presence.csv", encoding="utf-8")):
        sid = r["scene_id"].strip()
        sc = scenes.setdefault(sid, {"id": sid, "t0": round(sec(r["start"]), 2), "t1": round(sec(r["end"]), 2),
                                     "node": NODE[sid], "c": {}})
        st = r["status"].strip(); ev = (r.get("evidence") or "").lower()
        if st == "on_screen" or st == "imitation_revealed":
            node = sc["node"]
        elif st == "off_screen_stated":
            node = next((v for k, v in KEYS if k in ev), "unknown")
        elif st == "dead":
            node = "dead"
        else:
            node = "unknown"
        code = {"on_screen": "on", "off_screen_stated": "stated", "off_screen_unknown": "unk", "dead": "dead", "imitation_revealed": "thing"}[st]
        sc["c"][r["character"].strip()] = [code, node]
# ending (seg6), lead analysis
scenes["S6"] = {"id": "S6", "t0": 5952.4, "t1": 6127.12, "node": "ruins",
                "c": {c: (["on", "ruins"] if c in ("MacReady", "Childs") else ["dead", "dead"] if c not in ("Garry", "Nauls") else ["unk", "unknown"]) for c in CH}}
# in S6, Childs arrives at 01:39:52.987; before that he is unknown
order = sorted(scenes.values(), key=lambda s: s["t0"])

# face-pass on-screen intervals (labelled clusters only)
onscreen = collections.defaultdict(list)
for r in csv.DictReader(open(f"{B}/work/faces/presence.csv")):
    if r["character"] in CH:
        onscreen[r["character"]].append([round(sec(r["start"]), 1), round(sec(r["end"]), 1)])

# film barcode: mean colour per second (whole runtime), brightened for display
z = np.load(f"{B}/work/framestats.npz"); rgb = z["rgb"].astype(np.float32)   # frames x 3 (R,G,B means)
nsec = int(len(rgb) * F)
idx = (np.arange(len(rgb)) * F).astype(int)
acc = np.zeros((nsec + 1, 3)); cnt = np.zeros(nsec + 1)
np.add.at(acc, idx, rgb); np.add.at(cnt, idx, 1)
col = acc[:nsec] / np.maximum(cnt[:nsec, None], 1)
lum = col.max(1, keepdims=True) + 1e-6
boost = np.clip((lum / 255) ** 0.55 * 255 / lum, 0, 6)          # lift shadows, keep hue
disp = np.clip(col * boost, 0, 255).astype(int)
barcode = "".join(f"{r:02x}{g:02x}{b:02x}" for r, g, b in disp)

# status timelines for fates (seconds) — from the analysis
fates = {
 "Bennings": {"thing": [2812, 2900], "dead": 2900}, "Fuchs": {"dead": 4116, "lost": 3952},
 "Norris": {"thing": [4519, 4660], "dead": 4660}, "Copper": {"dead": 4730}, "Clark": {"dead": 4717},
 "Palmer": {"thing": [4976, 5077], "dead": 5077}, "Windows": {"thing": [5017, 5116], "dead": 5116},
 "Blair": {"thing": [5742, 5918], "dead": 5918}, "Garry": {"lost": 5754}, "Nauls": {"lost": 5800},
 "Childs": {"gap": [5228, 5993]},
}
events = json.load(open(f"{B}/web/events.json", encoding="utf-8"))
out = {"characters": [{"name": c, "role": ROLE[c], "color": COLOR[c]} for c in CH],
       "scenes": order, "onscreen": onscreen, "fates": fates, "events": events,
       "barcode": barcode, "runtime": 6127.12, "credits_end": round(len(rgb) * F, 2)}
json.dump(out, open(f"{B}/web/data.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print(len(order), "scenes;", sum(len(v) for v in onscreen.values()), "on-screen intervals;", nsec, "barcode seconds")
