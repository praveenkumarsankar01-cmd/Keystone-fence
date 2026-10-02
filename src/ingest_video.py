"""Swap real footage into the home-hero video slot.

    python3 src/ingest_video.py clip.mov --start 2 --dur 15 --desc "A contractor and a homeowner talk at a backyard fence."

Trims, crops to 16:9, scales to 1280x720, removes audio and writes
static/assets/media/site-walk.{mp4,webm,webp} plus site-walk.json (the
description screen readers get). Rebuild afterwards. `python3 src/video.py`
restores the illustrated version.
"""
import argparse, json, os, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FF = os.environ.get("FFMPEG") or __import__("imageio_ffmpeg").get_ffmpeg_exe()
ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("--start", type=float, default=0); ap.add_argument("--dur", type=float, default=15)
ap.add_argument("--desc", required=True); ap.add_argument("--tag", default="Site walk")
ap.add_argument("--out", default=os.path.join(ROOT, "static", "assets", "media"))
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
o = lambda ext: os.path.join(a.out, "site-walk." + ext)
vf = "scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,fps=30,format=yuv420p"
cut = ["-ss", str(a.start), "-t", str(a.dur), "-i", a.src, "-an", "-map_metadata", "-1", "-vf", vf]
run = lambda *args: subprocess.run([FF, "-y", "-loglevel", "error", *args], check=True)
run(*cut, "-c:v", "libx264", "-preset", "slow", "-crf", "25", "-maxrate", "2500k", "-bufsize", "5000k", "-movflags", "+faststart", o("mp4"))
run(*cut, "-c:v", "libvpx-vp9", "-crf", "36", "-b:v", "2000k", "-row-mt", "1", "-deadline", "good", "-cpu-used", "2", o("webm"))
run("-ss", str(a.start + min(a.dur / 2, 3)), "-i", a.src, "-frames:v", "1", "-vf", vf.replace(",fps=30", ""), "-c:v", "libwebp", "-quality", "82", o("webp"))
json.dump({"desc": a.desc, "tag": a.tag}, open(o("json"), "w"), indent=1)
for ext in ("mp4", "webm", "webp"):
    print(f"site-walk.{ext}: {os.path.getsize(o(ext)) / 1024:.0f} KB")
