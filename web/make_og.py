"""Link-preview cards (og-en.jpg, og-sk.jpg, 1200×630) for WhatsApp, Slack, Facebook, X.

MacReady on the left, Childs on the right, the question between them. The title sits in
the middle 630 px so a square crop (WhatsApp's small thumbnail) still reads.
Fonts are the site's (Google Fonts, OFL): Big Shoulders Display 900, IBM Plex Mono 500.
    python3 make_og.py <fonts_dir>      # BigShouldersDisplay.ttf, IBMPlexMono.ttf
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
W, H = 1200, 630
ICE, RED, FROST, BG = (143, 216, 255), (227, 38, 46), (201, 214, 227), (4, 7, 12)
TEXT = {
    "en": ("Who is human at the end?", "A FRAME-BY-FRAME INVESTIGATION"),
    "sk": ("Kto je na konci človek?", "ROZBOR FILMU SNÍMKU PO SNÍMKE"),
}


def panel(name, face_x, face_y, scale, at_x):
    """A W/2 × H panel cut from img/<name>, the face centre placed at panel x = at_x."""
    im = Image.open(HERE / "img" / name).convert("RGB")
    cw, ch = W / 2 / scale, H / scale
    left = min(max(face_x - at_x / scale, 0), im.width - cw)
    top = min(max(face_y - ch * 0.42, 0), im.height - ch)
    return im.crop((int(left), int(top), int(left + cw), int(top + ch))).resize((W // 2, H), Image.LANCZOS)


def shade():
    """Alpha mask: dark in the middle (title) and at the bottom (labels), clear over the faces."""
    m = Image.new("L", (W, H))
    px = m.load()
    for x in range(W):
        d = abs(x - W / 2) / (W / 2)          # 0 in the middle, 1 at the edges
        a = 235 if d < 0.30 else max(40, int(235 - (d - 0.30) / 0.45 * 195))
        for y in range(H):
            b = max(0, (y - H * 0.70) / (H * 0.30)) * 150
            px[x, y] = min(250, int(a + b))
    return m.filter(ImageFilter.GaussianBlur(18))


def centred(draw, y, text, font, fill, spacing=0):
    w = draw.textlength(text, font=font) + spacing * (len(text) - 1)
    x = (W - w) / 2
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + spacing


def card(lang, fonts):
    big = lambda s: ImageFont.truetype(str(fonts / "BigShouldersDisplay.ttf"), s)
    mono = lambda s: ImageFont.truetype(str(fonts / "IBMPlexMono.ttf"), s)
    base = Image.new("RGB", (W, H), BG)
    base.paste(panel("mac-frost.jpg", 905, 215, 1.25, 190), (0, 0))
    base.paste(panel("parka-end.jpg", 745, 255, 1.25, W // 2 - 190), (W // 2, 0))
    out = Image.composite(Image.new("RGB", (W, H), BG), base, shade())
    d = ImageDraw.Draw(out)
    question, kicker = TEXT[lang]
    centred(d, 118, kicker, mono(19), ICE, spacing=3)
    centred(d, 158, "A THING ABOUT", big(86), FROST, spacing=2)
    centred(d, 238, "THE THING", big(150), ICE, spacing=2)
    centred(d, 420, question, mono(30), FROST)
    d.line((W / 2 - 40, 478, W / 2 + 40, 478), fill=RED, width=3)
    d.text((48, H - 60), "MacREADY", font=mono(24), fill=FROST)
    d.text((W - 48 - d.textlength("CHILDS", font=mono(24)), H - 60), "CHILDS", font=mono(24), fill=FROST)
    centred(d, H - 56, "THETHING.N0HA.TECH", mono(17), ICE, spacing=2)
    path = HERE / f"og-{lang}.jpg"
    out.save(path, quality=86, optimize=True, progressive=True)
    return path


if __name__ == "__main__":
    fonts = Path(sys.argv[1])
    for lang in TEXT:
        p = card(lang, fonts)
        print(p.name, p.stat().st_size // 1024, "KB")
