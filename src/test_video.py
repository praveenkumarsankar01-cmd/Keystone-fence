"""Hero video behaviour: autoplay, pause control, reduced motion, off-screen pause."""
import os, sys, threading, http.server, socketserver, functools
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
socketserver.TCPServer.allow_reuse_address = True
srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(Q, directory=os.path.join(ROOT, sys.argv[1] if len(sys.argv) > 1 else "dist")))
port = srv.server_address[1]; threading.Thread(target=srv.serve_forever, daemon=True).start()
ok = fail = 0
def check(name, cond):
    global ok, fail
    ok, fail = ok + bool(cond), fail + (not cond)
    print(("PASS " if cond else "FAIL ") + name)
state = "() => { const v = document.querySelector('.js-vid'); const b = document.querySelector('.vid-btn'); return {paused: v.paused, t: v.currentTime, src: v.currentSrc.split('/').pop(), lbl: b.querySelector('.vid-lbl').textContent, hidden: b.hidden}; }"
with sync_playwright() as pw:
    br = pw.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
    for motion in ("no-preference", "reduce"):
        ctx = br.new_context(viewport={"width": 1280, "height": 800}, reduced_motion=motion)
        pg = ctx.new_page(); pg.goto(f"http://127.0.0.1:{port}/"); pg.wait_for_timeout(1800)
        s = pg.evaluate(state)
        if motion == "no-preference":
            check(f"autoplays ({s['src']}, t={s['t']:.2f})", not s["paused"] and s["t"] > 0.3)
            check("pause control visible, says Pause", not s["hidden"] and s["lbl"] == "Pause")
            pg.click(".vid-btn"); pg.wait_for_timeout(300); s = pg.evaluate(state)
            check("click pauses, label -> Play", s["paused"] and s["lbl"] == "Play")
            pg.mouse.wheel(0, 3000); pg.wait_for_timeout(600); pg.mouse.wheel(0, -3000); pg.wait_for_timeout(800)
            check("stays paused after scrolling away and back (user choice kept)", pg.evaluate(state)["paused"])
            pg.click(".vid-btn"); pg.wait_for_timeout(500)
            check("click plays again", not pg.evaluate(state)["paused"])
            pg.mouse.wheel(0, 3000); pg.wait_for_timeout(800)
            check("pauses when scrolled off-screen", pg.evaluate(state)["paused"])
            pg.mouse.wheel(0, -3000); pg.wait_for_timeout(1000)
            check("resumes when back on screen", not pg.evaluate(state)["paused"])
        else:
            check("reduced motion: stays on poster, label Play", s["paused"] and s["t"] == 0 and s["lbl"] == "Play")
            pg.click(".vid-btn"); pg.wait_for_timeout(900)
            check("reduced motion: plays on request", not pg.evaluate(state)["paused"])
        ctx.close()
    br.close()
srv.shutdown()
print(f"{ok} passed, {fail} failed")
