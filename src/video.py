"""Render the home-hero "site walk" video from src/video_scene.js.

    python3 src/video.py --stills 1.5 5.5 13.4   -> shots/vid_<t>.png (check frames)
    python3 src/video.py                         -> static/assets/media/site-walk.{mp4,webm,webp}

Frames are rendered deterministically in headless Chromium (render(t) poses
the scene at time t) and piped straight into ffmpeg. Real footage can replace
these files later: the site only looks for the same filenames.
"""
import io, os, subprocess, sys
from playwright.sync_api import sync_playwright
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = f"file://{ROOT}/static/assets/fonts"
OUT = os.path.join(ROOT, "static", "assets", "media")
FPS, POSTER_T = 30, 13.3
FFMPEG = os.environ.get("FFMPEG") or __import__("imageio_ffmpeg").get_ffmpeg_exe()

PAGE = f"""<!doctype html><meta charset="utf-8"><style>
@font-face{{font-family:'Hanken Grotesk';font-weight:400 700;src:url({FONTS}/hanken-grotesk.woff2) format('woff2')}}
@font-face{{font-family:'IBM Plex Mono';font-weight:500;src:url({FONTS}/ibm-plex-mono-500.woff2) format('woff2')}}
@font-face{{font-family:'IBM Plex Mono';font-weight:600;src:url({FONTS}/ibm-plex-mono-600.woff2) format('woff2')}}
html,body{{margin:0;background:#FAFAF7;overflow:hidden}} svg{{display:block}}
.say{{font:600 46px 'Hanken Grotesk',sans-serif;fill:#16191B;letter-spacing:-.005em}}
.who{{font:600 19px 'IBM Plex Mono',monospace;letter-spacing:.14em;fill:#7C401E}}
.lbl{{font:600 17px 'IBM Plex Mono',monospace;letter-spacing:.08em;fill:#16191B}}
.lbl-alert{{fill:#A33A2B}}
.dimt{{font:600 18px 'IBM Plex Mono',monospace;fill:#7C401E;letter-spacing:.04em}}
.tbh{{font:600 13px 'IBM Plex Mono',monospace;fill:#16191B;letter-spacing:.08em}}
.tbl{{font:500 11px 'IBM Plex Mono',monospace;fill:#575E62;letter-spacing:.1em}}
.tbv{{font:600 15px 'IBM Plex Mono',monospace;fill:#16191B;letter-spacing:.04em}}
</style><svg id="s" width="1280" height="720" viewBox="0 0 1280 720" xmlns="http://www.w3.org/2000/svg"></svg>
<script>{open(os.path.join(ROOT, "src", "video_scene.js")).read()}</script>"""


def open_scene(pw):
    b = pw.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
    pg = b.new_page(viewport={"width": 1280, "height": 720})
    path = os.path.join(ROOT, "shots", "video_scene.html")
    open(path, "w").write(PAGE)
    pg.goto(f"file://{path}")
    pg.evaluate("document.fonts.ready")
    loaded = pg.evaluate("Promise.all([...document.fonts].map(f => f.load())).then(() => [...document.fonts].filter(f => f.status === 'loaded').length)")
    assert loaded >= 3, f"fonts not loaded ({loaded})"
    pg.evaluate("build()")
    return b, pg


def frame(pg, t):
    pg.evaluate(f"render({t:.4f})")
    return pg.screenshot(type="png")


def main():
    if "--stills" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--stills") + 1:]]
        with sync_playwright() as pw:
            b, pg = open_scene(pw)
            for t in ts:
                open(os.path.join(ROOT, "shots", f"vid_{t:05.2f}.png"), "wb").write(frame(pg, t))
            b.close()
        print("stills:", ts)
        return
    os.makedirs(OUT, exist_ok=True)
    mp4, webm = os.path.join(OUT, "site-walk.mp4"), os.path.join(OUT, "site-walk.webm")
    src = ["-f", "image2pipe", "-framerate", str(FPS), "-c:v", "png", "-i", "-"]
    enc = [
        subprocess.Popen([FFMPEG, "-y", "-loglevel", "error", *src, "-c:v", "libx264", "-preset", "slow", "-crf", "24",
                          "-tune", "animation", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", mp4], stdin=subprocess.PIPE),
        subprocess.Popen([FFMPEG, "-y", "-loglevel", "error", *src, "-c:v", "libvpx-vp9", "-crf", "40", "-b:v", "0",
                          "-row-mt", "1", "-deadline", "good", "-cpu-used", "2", "-pix_fmt", "yuv420p", "-an", webm], stdin=subprocess.PIPE),
    ]
    with sync_playwright() as pw:
        b, pg = open_scene(pw)
        n = int(round(pg.evaluate("DUR") * FPS))
        for i in range(n):
            png = frame(pg, i / FPS)
            for e in enc:
                e.stdin.write(png)
        poster = Image.open(io.BytesIO(frame(pg, POSTER_T))).convert("RGB")
        b.close()
    for e in enc:
        e.stdin.close(); e.wait()
        assert e.returncode == 0, "ffmpeg failed"
    poster.save(os.path.join(OUT, "site-walk.webp"), quality=84, method=6)
    for f in sorted(os.listdir(OUT)):
        if f.startswith("site-walk"):
            print(f"{f}: {os.path.getsize(os.path.join(OUT, f)) / 1024:.0f} KB")
    print(f"{n} frames @ {FPS} fps")


if __name__ == "__main__":
    main()
