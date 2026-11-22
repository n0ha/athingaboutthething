#!/usr/bin/env python3
"""Builds the-thing-investigation/timeline.md from work/segments/seg*_presence.csv + scene headers.
Hand-written sections (story time, assimilations, map) live in this file; tables are generated."""
import csv, re, collections, os
B = str(__import__("pathlib").Path(__file__).resolve().parents[2])  # project root
S = f"{B}/work/segments"
CH = ["MacReady", "Childs", "Nauls", "Windows", "Palmer", "Garry", "Blair", "Copper", "Norris", "Clark", "Bennings", "Fuchs"]
ABBR = {"MacReady": "Mac", "Childs": "Chi", "Nauls": "Nau", "Windows": "Win", "Palmer": "Pal", "Garry": "Gar",
        "Blair": "Bla", "Copper": "Cop", "Norris": "Nor", "Clark": "Cla", "Bennings": "Ben", "Fuchs": "Fuc"}
SYM = {"on_screen": "●", "off_screen_stated": "○", "off_screen_unknown": "·", "dead": "✝", "imitation_revealed": "◆"}

titles = {}
for n in range(1, 6):
    for line in open(f"{S}/seg{n}.md", encoding="utf-8"):
        if not line.startswith("## "): continue
        m = re.match(r"## (?:Scéna )?(S\d-\d+|\d\.\d+|\d-\d+)\s*[·|—-]+\s*(.*)", line.strip())
        if m:
            sid, rest = m.group(1), m.group(2)
            parts = re.split(r"\s+[·|—]\s+", rest)
            titles[sid] = parts[-1].strip(" ·|—")
scenes = collections.OrderedDict()
for n in range(1, 6):
    for r in csv.DictReader(open(f"{S}/seg{n}_presence.csv", encoding="utf-8")):
        sid = r["scene_id"].strip()
        sc = scenes.setdefault(sid, {"start": r["start"], "end": r["end"], "loc": r["location"], "st": {}, "ev": {}})
        name = r["character"].strip()
        sc["st"][name] = r["status"].strip(); sc["ev"][name] = (r.get("evidence") or "").strip().strip('"')
order = sorted(scenes, key=lambda s: scenes[s]["start"])

out = []
w = out.append
w("# Časová os — The Thing (1982)\n")
w("> Zostavené z piatich nezávislých chronologických priechodov (`work/segments/seg1–5`) a analýzy záveru (`seg6_ending.md`).")
w("> Časy sú prezentačné časy snímok vo filme (`HH:MM:SS.mmm`, 23,976 fps). **Čas vo filme ≠ čas v príbehu**: strih môže skryť minúty aj dni.\n")
w("## 1. Čas v príbehu — čo film o uplynulom čase skutočne hovorí\n")
w("""| film | značka | čo z nej vyplýva |
| --- | --- | --- |
| 00:10:15 | „First goddamn week of winter.“ | začiatok antarktickej zimy |
| 00:11:04 | Windows: dva týždne bez spojenia | izolácia trvá už pred príchodom psa |
| 00:26:47 → 00:30:08 | pes sa večer dostane do psinca, útok v noci | medzi umiestnením a útokom uplynú hodiny (Clark: pes v psinci „until last night“, 00:35:28) |
| 00:35:37 | Clark: s psom sám „an hour, hour and a half“ | na obraze ≈1 min; zvyšok skrytý |
| 00:36:12 | „about nine hours“ nórskych záznamov | analýza pások trvá hodiny |
| 00:46:03 | MacReady: „I haven't slept in days“ | od príletu psa uplynulo viac dní |
| 00:54:42 | noc → deň bez vysvetlenia (úsek 3) | skrytý čas medzi scénami |
| 01:01:59 → 01:03:16 | „storm hitting us in six hours“ → „hitting us hard now for 48 hours“ | **najmenej ≈54 h skrytého času** medzi dvoma po sebe idúcimi scénami |
| 01:06:21 | „Lights were out in there for an hour.“ | hodina tmy, na obraze len Fuchs |
| 01:09:57 | MacReady a Nauls sú vonku „40, 45 minutes“ | navzájom jediní svedkovia, interiér chatrče nikdy neukázaný |
| 01:27:08 → 01:39:53 | Childs mimo obrazu ≈12 min 45 s filmu | v príbehu: výprava k Blairovi, výpadok, ničenie tábora, výbuch — rádovo hodiny |
| 01:30:32 | „In six hours it'll be a hundred below in here.“ | horná hranica, kým stanica zamrzne |
| 01:40:31 | „Fire's got the temperature up all over the camp. Won't last long, though.“ | záver sa odohráva krátko po výbuchoch, oheň ešte horí |
""")
w("## 2. Potvrdené imitácie a okná asimilácie\n")
w("""| imitácia | kedy odhalená | najneskoršie okno asimilácie (čo film ukazuje) | istota |
| --- | --- | --- | --- |
| pes (nórsky) | 00:28:20 psinec | pred príchodom (Nóri ho prenasledujú) | priamo ukázané |
| Bennings | 00:46:52–00:48:03 | sklad, sám s pozostatkami 00:45:25–00:46:36 | priamo ukázané (vrátane priebehu) |
| Norris | 01:15:19 (defibrilácia) | neznáme; možné príležitosti: kontakt s psom 00:26:44–46, celá hodina tmy 01:05–01:06 aj skoršie neviditeľné okná; bolesť na hrudi 01:10:08 | odhalenie priamo, okno neurčené |
| Palmer | 01:22:56 (krvný test) | neznáme; dlhé neviditeľné úseky (00:50–00:57:51 a i.) | odhalenie priamo, okno neurčené |
| Windows | 01:24:50 | 01:23:37–01:24:50 napadnutý Palmerom-Vecou na obraze | priamo ukázané |
| Blair | 01:35:42 (ruka na Garryho tvári), 01:38:02 Blair-Vec | neurčené; od 00:56:06 sám zamknutý v kôlni, nikdy netestovaný | odhalenie priamo, okno neurčené |
| Garry | — (zmizne po 01:35:54) | 01:35:42–01:35:54 Blairova ruka na tvári, „gurgling“ | osud neukázaný |
| Nauls | — (zmizne po 01:36:40) | sám v podzemí, nereaguje na volanie 01:36:42 | osud neukázaný |
| **Childs** | — | **01:27:08–01:39:53 bez dozoru**; test krvi 01:25:43 (výsledok len odvodený) | **otvorené** |
| **MacReady** | — | test 01:21:55 (bez reakcie); neskôr sám 01:36–01:39 (podzemie, Blair-Vec) | **otvorené pre čas po teste** |
""")
w("## 3. Childs a MacReady — kde sú, kto ich vidí\n")
w("Prehľad z tabuľky prítomnosti (● v zábere, ○ mimo záberu so známym miestom, · neznáme, ✝ mŕtvy, ◆ odhalená imitácia).\n")
w("| scéna | od | do | miesto | MacReady | Childs |\n| --- | --- | --- | --- | --- | --- |")
for sid in order:
    sc = scenes[sid]
    def cell(c):
        st = sc["st"].get(c, ""); ev = sc["ev"].get(c, "").replace("|", "/")
        return f"{SYM.get(st, '?')} {ev[:110]}"
    w(f"| {sid} | {sc['start']} | {sc['end']} | {sc['loc'][:50].replace('|','/')} | {cell('MacReady')} | {cell('Childs')} |")
w("| S6 | 01:39:12.405 | 01:42:07.121 | trosky tábora, oheň (noc) | ● sedí s fľašou J&B | ● príde 01:39:52.987 z tmy, parka pôsobí svetlo (námraza), plameňomet |")
w("""
**Nepozorované okná (výber, podrobne v segmentoch):**

- **MacReady:** sám v kuchyni pri útoku v psinci (00:30:08, sám spustí poplach); sám vonku ≈81 s
  (00:50:53–00:52:14) a ≈50 s s Blairom v kôlni; posledný videný s Fuchsom pred výpadkom (01:05:06);
  40–45 min s Naulsom pri chatrči (01:09–01:10, len Nauls je svedok, ktorý ho potom obviní);
  sám vonku po odrezaní z lana (01:11–01:12:30); po teste sám pri rozbuške a s Blair-Vecou
  (01:36:46–01:38:38).
- **Childs:** sám ≈24 s pri traktore (00:52:36–00:53:00) a pri dverách mapovne (00:53:18–00:53:46);
  počas výpadku v stanici s Palmerom (01:06–01:09, navzájom); **01:27:08–01:39:53 úplne bez dozoru**
  (prázdna šatňa so snehom na podlahe 01:29:17–35; neidentifikovaná postava s plameňometom pri hlavnom
  vchode 01:29:50–55; Nauls „I think I saw Childs outside the main entrance“ 01:30:04).
""")
w("## 4. Všetky postavy po scénach\n")
w("Stĺpce: " + ", ".join(f"{ABBR[c]} = {c}" for c in CH) + ".\n")
w("| scéna | od | do | miesto | " + " | ".join(ABBR[c] for c in CH) + " | obsah |")
w("| --- | --- | --- | --- | " + " | ".join("---" for _ in CH) + " | --- |")
for sid in order:
    sc = scenes[sid]
    w(f"| {sid} | {sc['start']} | {sc['end']} | {sc['loc'][:45].replace('|','/')} | " +
      " | ".join(SYM.get(sc['st'].get(c, ''), '?') for c in CH) + f" | {titles.get(sid, '')[:90].replace('|','/')} |")
w("""
## 5. Mapa stanice (schéma z priestorových náznakov vo filme)

Film nikdy neukáže celý pôdorys; schéma je odvodená z prechodov postáv a zo záberov exteriéru.
Vzdialenosti nie sú v mierke.

```
                      [MacReadyho chatrč]  (vyvýšená búda na nohách, rebrík)
                              ▲
                              │ vodiace lano na stĺpoch s modrými svetlami (01:09:41)
                              │
   [Blairova kôlňa/toolshed]──┤          ┌──────────────── HLAVNÁ BUDOVA (kupola) ─────────────────┐
     padacie dvere → tunel    │          │ rec room (biliard, gauč) · kuchyňa · rádiová miestnosť    │
     → Blairova „loď“         │          │ laboratórium · sklad (storeroom) · ošetrovňa · mapovňa    │
     (pod snehom, 01:28)      ├── lano ──┤ izby (MacReady, Blair...) · chodby                         │
                              │          │ šatňa/predsieň s vešiakmi parkov (01:26:39) ─► HLAVNÝ VCHOD│
   [psinec] (rad klietok,     │          │   (oblúkový zasnežený vstupný tunel s lampou, 00:09:12)   │
    za ním schody nahor)  ────┘          └───────────────┬─────────────────────────────────────────┘
                                                         │ podzemie: sudy, generátorovňa (01:34),
   [hangár / vrtuľníky, traktor/snowcat]                 │ „old storage room“ (Garry, 01:35)
   [sklad krvi: zamknutá skriňa, kľúč Garry/Copper]      ▼
```

Pre vizualizáciu „stanica zhora s bodkami“ (final-report.md, sekcia 8) sa miesta zo stĺpca *miesto*
mapujú na tieto uzly.
""")
open(f"{B}/the-thing-investigation/timeline.md", "w", encoding="utf-8").write("\n".join(out) + "\n")
print(len(order), "scenes;", sum(1 for s in order if s in titles), "with titles")
