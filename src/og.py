"""Render assets/og.png (1200x630 social share image) from the brand assets."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from drawings import drawing, logo_mark
from data_services import SILOS
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
css = open(f"{ROOT}/static/assets/site.css").read().replace("url(fonts/", f"url(file://{ROOT}/static/assets/fonts/")
trades = " · ".join(s["nav"] for s in SILOS)
html = f'''<!doctype html><meta charset="utf-8"><style>{css}
body{{margin:0;width:1200px;height:630px;overflow:hidden;background:var(--vellum)}}
.og{{display:grid;grid-template-columns:520px 1fr;gap:40px;align-items:center;height:630px;padding:0 60px;border-top:10px solid var(--cedar)}}
.og h1{{font-size:84px;line-height:.92;margin:26px 0 24px}}
.og p{{font:500 19px/1.45 var(--mono);color:var(--graphite);letter-spacing:.02em;margin:0}}
.og .brand-name{{font-size:2.1rem}} .og .brand-sub{{font-size:12px}}
.og .drawing .co,.og .drawing .tb{{display:inline}}
</style><div class="og"><div><span class="brand">{logo_mark(46)}<span class="brand-word"><span class="brand-name">Keystone</span><span class="brand-sub">Fence &amp; Deck Co.</span></span></span>
<h1>Fences built to stay straight in Texas clay.</h1><p>{trades}<br>Plano &amp; North Dallas</p></div>
<figure class="sheet-frame"><span class="sheet-tag">Sheet F-01 · Elevation</span>{drawing("board_on_board")}</figure></div>'''
open(f"{ROOT}/shots/og.html", "w").write(html)
with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
    pg = b.new_page(viewport={"width": 1200, "height": 630})
    pg.goto(f"file://{ROOT}/shots/og.html"); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(400)
    pg.screenshot(path=f"{ROOT}/static/assets/og.png"); b.close()
print("og.png:", trades)
