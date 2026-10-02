"""Full-page phone screenshots, tiled into review sheets (4 slices side by side)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shoot import shoot
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W = int(os.environ.get("W", 390)); SL = 1500
pages = sys.argv[1:] or [""]
def settle(pg):
    pg.evaluate("document.querySelectorAll('video').forEach(v => v.pause())")
    pg.evaluate("window.scrollTo(0, document.body.scrollHeight)"); pg.wait_for_timeout(500); pg.evaluate("window.scrollTo(0, 0)")
jobs = [(p, W, 844, f"long_{W}_{(p.strip('/').replace('/', '_') or 'home')}.png", True, settle) for p in pages]
shoot(jobs)
for _, _, _, out, _, _ in jobs:
    im = Image.open(os.path.join(ROOT, "shots", out)); w, h = im.size
    n = -(-h // SL); sheets = -(-n // 4)
    for s in range(sheets):
        cols = min(4, n - s * 4); sheet = Image.new("RGB", (cols * (w + 12) - 12, SL), "white")
        for c in range(cols):
            i = s * 4 + c; sheet.paste(im.crop((0, i * SL, w, min(h, (i + 1) * SL))), (c * (w + 12), 0))
        sheet.save(os.path.join(ROOT, "shots", out.replace(".png", f"_s{s + 1}.png")))
    print(out, f"{w}x{h}", f"{sheets} sheet(s)")
