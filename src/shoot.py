"""Screenshot helper: serves dist/, routes Chromium through the sandbox proxy
so Google Fonts load, and verifies the webfonts actually rendered."""
import os, sys, threading, http.server, socketserver, functools
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass

def shoot(jobs, build="dist"):
    os.makedirs(os.path.join(ROOT, "shots"), exist_ok=True)
    socketserver.TCPServer.allow_reuse_address = True
    srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(Q, directory=os.path.join(ROOT, build)))
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
                               proxy={"server": proxy, "bypass": "127.0.0.1,localhost"} if proxy else None,
                               args=["--ignore-certificate-errors-spki-list"])
        ctx = b.new_context(ignore_https_errors=False)
        for path, w, h, out, full, action in jobs:
            pg = ctx.new_page(); pg.set_viewport_size({"width": w, "height": h})
            pg.goto(f"http://127.0.0.1:{port}/{path}", wait_until="networkidle")
            pg.evaluate("document.fonts.ready")
            ok = pg.evaluate("[...document.fonts].filter(f=>f.status==='loaded').map(f=>f.family).filter((v,i,a)=>a.indexOf(v)===i)")
            if action: action(pg)
            pg.wait_for_timeout(400)
            pg.screenshot(path=os.path.join(ROOT, "shots", out), full_page=full)
            print(f"{out}: fonts loaded -> {ok}")
            pg.close()
        b.close()
    srv.shutdown()

if __name__ == "__main__":
    shoot([("", 1280, 820, "home_top.png", False, None)])
