"""Check the longer brand name fits: header row at desktop widths, drawing title blocks."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shoot import shoot
res = {}
def hdr(pg):
    res[pg.viewport_size["width"]] = pg.evaluate("""() => {
      const h = document.querySelector('.hdr .wrap') || document.querySelector('header .wrap');
      const kids = [...h.children].filter(k => getComputedStyle(k).display !== 'none');
      const used = kids.reduce((a, k) => a + k.getBoundingClientRect().width, 0);
      const over = [...document.querySelectorAll('.k-tbh')].map(t => {
        const r = t.closest('g').querySelector('.k-tb').getBBox(); const b = t.getBBox();
        return (b.x + b.width) - (r.x + r.width - 4); }).filter(v => v > 0);
      return {avail: h.clientWidth, used: Math.round(used), sw: document.documentElement.scrollWidth, tbOver: over};
    }""")
shoot([("", w, 800, f"fit_{w}.png", False, hdr) for w in (1181, 1200, 1280, 1440)])
for w, r in res.items(): print(w, r)
