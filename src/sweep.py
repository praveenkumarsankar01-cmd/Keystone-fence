"""Horizontal-overflow sweep: every page at phone, tablet and desktop widths."""
import os, sys, threading, http.server, socketserver, functools
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = sys.argv[1] if len(sys.argv) > 1 else "dist"
WIDTHS = [320, 360, 390, 414, 768, 1024, 1180, 1280, 1440]
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
    def handle(self):
        try: super().handle()
        except (BrokenPipeError, ConnectionResetError): pass
socketserver.TCPServer.allow_reuse_address = True
srv = socketserver.ThreadingTCPServer(("127.0.0.1", 0), functools.partial(Q, directory=os.path.join(ROOT, BUILD)))
port = srv.server_address[1]; threading.Thread(target=srv.serve_forever, daemon=True).start()
pages = sorted(os.path.relpath(os.path.join(d, f), os.path.join(ROOT, BUILD)).replace(os.sep, "/").replace("index.html", "")
               for d, _, fs in os.walk(os.path.join(ROOT, BUILD)) for f in fs if f.endswith(".html") and f != "404.html")
CHECK = """() => { const W = innerWidth, bad = [];
  const scrollers = [...document.querySelectorAll('*')].filter(e => { const s = getComputedStyle(e); return /auto|scroll|hidden/.test(s.overflowX) && e !== document.documentElement && e !== document.body; });
  for (const e of document.querySelectorAll('body *')) {
    if (scrollers.some(s => s !== e && s.contains(e))) continue;
    if (e.closest('.hp, .sr-only, .skip')) continue;
    const s = getComputedStyle(e); if (s.position === 'fixed' || s.display === 'none' || s.visibility === 'hidden') continue;
    const r = e.getBoundingClientRect(); if (r.width && (r.right > W + 1 || r.left < -1)) bad.push(e.tagName.toLowerCase() + '.' + [...e.classList].join('.') + ' ' + Math.round(r.left) + '..' + Math.round(r.right));
  }
  return {sw: document.documentElement.scrollWidth, W, bad: bad.slice(0, 4)}; }"""
problems = 0
with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
    ctx = b.new_context(reduced_motion="reduce")
    ctx.route("**/*", lambda r: r.abort() if not r.request.url.startswith(f"http://127.0.0.1:{port}") else r.continue_())
    pg = ctx.new_page()
    for w in WIDTHS:
        pg.set_viewport_size({"width": w, "height": 900})
        for p in pages:
            pg.goto(f"http://127.0.0.1:{port}/{p}", wait_until="load")
            r = pg.evaluate(CHECK)
            if r["sw"] > r["W"] or r["bad"]:
                problems += 1; print(f"{w}px /{p}: scrollWidth {r['sw']} > {r['W']}" if r["sw"] > r["W"] else f"{w}px /{p}:", r["bad"])
    b.close()
srv.shutdown()
print(f"{len(pages)} pages x {len(WIDTHS)} widths: {problems} with overflow")
