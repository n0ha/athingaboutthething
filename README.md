# A Thing About The Thing

Who is human at the end of John Carpenter's *The Thing* (1982)? A frame-by-frame
investigation of the film and a bilingual (English / Slovak) explainer site built from it.

**Site: https://thething.n0ha.tech**

## The verdict, in short

- **The film does not prove who, if anyone, is the Thing at the end** (high confidence).
  It withholds exactly the information that would decide it.
- **Of the eight blood tests shown on screen, only the two survivors' cannot be checked
  from the image.** The 1981 screenplay has MacReady cut himself and draw his own blood
  on screen; the film cuts to a close-up of Childs instead.
- **MacReady is an open case.** A trail of torn clothes through the middle of the film
  (00:41–01:14) is the best candidate for the clue Carpenter says is hidden there
  (low to moderate confidence). The plot also allows that he was framed.
- **Childs: human and Thing stay about equally likely.** He is alone from 01:27:08 at
  his post, earlier than the usual reading assumes; his "thought I saw Blair" fits what
  his window overlooks, but nobody confirms it.
- The popular "breath" and "eye light" tells do not hold up as tests; the "Childs' parka
  changes colour" reading is frost and lighting, not a costume change.

## How it was made

The analysis was carried out by AI agents (Claude Code) under the repository owner's
direction:

1. Five independent passes logged the theatrical cut scene by scene: who is present, who
   is alone, props, costumes, breath and eyes. The final scene was analysed frame by frame.
2. Measurements came from the frames themselves (ffmpeg), face presence clustering,
   the subtitles and an independent faster-whisper transcript of the dialogue channel.
3. Only then were external sources checked: interviews, the commentary track, the 1981
   screenplay and the fan theories with their origins traced.
4. An adversarial review attacked the draft verdict.
5. In a second round, two other models (a separate Claude session and OpenAI Codex) were
   asked to break the verdict. Each challenge was checked against the frames, the
   subtitles and the screenplay before it changed anything. What was accepted, partly
   accepted or rejected is listed in `the-thing-investigation/hypotheses.md` §7.

## What is here

| Path | Contents |
| --- | --- |
| `web/` | the site: `index.html` (source), `data.json` and `events.json` (timeline data), `img/` (31 stills), `build_site.sh` |
| `the-thing-investigation/final-report.md` | the report: material, method, strongest clues, verdict |
| `the-thing-investigation/hypotheses.md` | the five hypotheses, fixed points, scoring, both review rounds |
| `the-thing-investigation/evidence.csv` | 329 timestamped observations with frame numbers, reliability and production explanations |
| `the-thing-investigation/timeline.md` | who is where, scene by scene |
| `the-thing-investigation/rules.md` | what the film itself establishes about how the Thing works |
| `the-thing-investigation/sources.md` | external sources, verified at their origin, and the screenplay comparison |
| `the-thing-investigation/tools/` | analysis scripts (frame statistics, contact sheets, faces, transcript) |

The reports are written in Slovak; the site is in both languages.

Not included: the film, its subtitles, the transcript, face embeddings and the 249 working
stills. The `frame_file` column in `evidence.csv` and the scripts refer to those local
files. Timestamps are presentation times of the decoded theatrical cut at 23.976 fps:
frame = round(t × 24000 / 1001).

## Building the site

`web/index.html` is a page fragment (it is also published as a claude.ai artifact, which
adds its own document skeleton). `build_site.sh` wraps it into two standalone entry
points: `/` with an English link preview and `/sk` with a Slovak one that opens in Slovak.
The preview cards (`og-en.jpg`, `og-sk.jpg`) come from `make_og.py`.

```sh
web/build_site.sh                                         # → web/dist/
BASE_URL=https://thething.n0ha.tech/ web/build_site.sh    # absolute URLs for link previews
python3 -m http.server -d web/dist 8000
```

Every push to `main` that touches `web/` deploys `web/dist/` to GitHub Pages
(`.github/workflows/pages.yml`).

The live site counts visits with [GoatCounter](https://www.goatcounter.com/): no cookies and
no personal data. The counter is added only at deployment, from the repository variable
`GOATCOUNTER_URL`, so local builds and copies of the site do not report anything.

## License

- Code (scripts, build, the page's markup and JavaScript): MIT, see `LICENSE`.
- Text and data (reports, `evidence.csv`, `data.json`, the site's copy):
  [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
- Stills from *The Thing* (1982) are © Universal Pictures and are used for commentary
  and analysis. They are not covered by the licenses above. This is a fan project, not
  affiliated with Universal or the filmmakers.

## Slovensky

Kto je na konci filmu *The Thing* (1982) človek? Forenzný rozbor filmu snímku po snímke
a dvojjazyčná stránka, ktorá ho vysvetľuje: **https://thething.n0ha.tech**. Správy
v `the-thing-investigation/` sú po slovensky. Kód je pod licenciou MIT, texty a dáta pod
CC BY 4.0, zábery z filmu patria Universal Pictures.
