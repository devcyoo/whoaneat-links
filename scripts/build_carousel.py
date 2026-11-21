"""Build IG carousel slides with real product frames from our AI demo videos.
Runs in GitHub Actions (needs network + ffmpeg). Usage: python scripts/build_carousel.py cold
Frames are AI visualizations, so every photo carries an on-image label."""
import json, os, subprocess, sys, urllib.request
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = os.path.join(ROOT, "scripts", "fonts")
CDN = "https://d2ol7oe51mr4n9.cloudfront.net/user_3MI2NyIthUwXHQgnoVDvzfzAvZ9/"
W, H = 1080, 1350
INK, CREAM, YEL = (20, 22, 28), (249, 246, 240), (255, 210, 63)

def font(name, size): return ImageFont.truetype(os.path.join(F, f"Inter-{name}.otf"), size)

def frame(vid, t, cache={}):
    if (vid, t) in cache: return cache[(vid, t)]
    mp4, jpg = f"/tmp/{vid}.mp4", f"/tmp/{vid}_{t}.jpg"
    if not os.path.exists(mp4): urllib.request.urlretrieve(CDN + vid + ".mp4", mp4)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(t), "-i", mp4, "-frames:v", "1", "-q:v", "2", jpg], check=True)
    cache[(vid, t)] = Image.open(jpg).convert("RGB")
    return cache[(vid, t)]

def photo(im, w, h, cy=0.5, label=True):
    iw, ih = im.size
    s = max(w / iw, h / ih); im = im.resize((round(iw * s), round(ih * s)), Image.LANCZOS)
    iw, ih = im.size; top = min(max(0, round(ih * cy - h / 2)), ih - h)
    im = im.crop(((iw - w) // 2, top, (iw - w) // 2 + w, top + h))
    if label:
        d = ImageDraw.Draw(im); f = font("SemiBold", 22); txt = "AI visualization of a real product"
        tw = d.textlength(txt, font=f)
        d.rounded_rectangle((16, h - 54, 40 + tw, h - 16), 19, fill=(0, 0, 0))
        d.text((28, h - 49), txt, font=f, fill=(255, 255, 255))
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w, h), 36, fill=255)
    return im, m

def wrap(d, text, f, maxw):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: lines.append(cur); cur = w
    return lines + [cur]

def text_block(d, x, y, text, f, maxw, lh, fill=INK):
    for ln in wrap(d, text, f, maxw): d.text((x, y), ln, font=f, fill=fill); y += lh
    return y

def chrome(d, bg):
    d.text((W - 90, 96), "whoa. neat.", font=font("ExtraBold", 38), fill=INK, anchor="ra")
    d.rounded_rectangle((90, 1200, W - 90, 1270), 35, fill=INK if bg == YEL else YEL)
    d.text((W / 2, 1235), "Link in bio · #ad", font=font("Bold", 34), fill=YEL if bg == YEL else INK, anchor="mm")

def cover(c, out):
    img = Image.new("RGB", (W, H), YEL); d = ImageDraw.Draw(img); chrome(d, YEL)
    d.text((90, 200), c["kicker"], font=font("SemiBold", 34), fill=INK)
    y = text_block(d, 90, 250, c["title"], font("ExtraBold", 92), 900, 104)
    grid_top, g, cw = max(y + 40, 520), 20, (900 - 20) // 2
    ch = (1140 - grid_top - g) // 2
    for k, s in enumerate(c["slides"][:4]):
        p, m = photo(frame(s["vid"], s["t"]), cw, ch, s.get("cy", 0.5), label=False)
        img.paste(p, (90 + (k % 2) * (cw + g), grid_top + (k // 2) * (ch + g)), m)
    d.text((W - 90, 1152), "AI visualizations of real products", font=font("SemiBold", 22), fill=INK, anchor="ra")
    img.save(out, quality=90)

def slide(n, s, out):
    img = Image.new("RGB", (W, H), CREAM); d = ImageDraw.Draw(img); chrome(d, CREAM)
    d.ellipse((90, 150, 190, 250), fill=YEL)
    d.text((140, 200), str(n), font=font("ExtraBold", 52), fill=INK, anchor="mm")
    y = text_block(d, 90, 280, s["title"], font("ExtraBold", 72), 900, 84)
    y = text_block(d, 90, y + 12, s["sub"], font("SemiBold", 36), 900, 48)
    top = y + 36; h = 1170 - top
    p, m = photo(frame(s["vid"], s["t"]), 900, h, s.get("cy", 0.5))
    img.paste(p, (90, top), m); img.save(out, quality=90)

if __name__ == "__main__":
    cfg = json.load(open(os.path.join(ROOT, "scripts", "carousels.json")))
    for key in sys.argv[1:]:
        c = cfg[key]
        cover(c, os.path.join(ROOT, "posts", f"{key}-0.jpg"))
        for i, s in enumerate(c["slides"], 1): slide(i, s, os.path.join(ROOT, "posts", f"{key}-{i}.jpg"))
        print("built", key)
