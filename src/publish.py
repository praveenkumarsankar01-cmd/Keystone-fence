"""Make publish/index.html (artifact fragment) + publish/files.json from preview/."""
import json, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "preview")
s = open(os.path.join(P, "index.html"), encoding="utf-8").read()
s = re.sub(r"<!doctype html>\s*|</?html[^>]*>\s*|</?head>\s*|</?body[^>]*>\s*", "", s, flags=re.I)
os.makedirs(os.path.join(ROOT, "publish"), exist_ok=True)
open(os.path.join(ROOT, "publish", "index.html"), "w", encoding="utf-8").write(s)
files = sorted(os.path.relpath(os.path.join(d, f), P).replace(os.sep, "/") for d, _, fs in os.walk(P) for f in fs if os.path.relpath(os.path.join(d, f), P) != "index.html")
json.dump(files, open(os.path.join(ROOT, "publish", "files.json"), "w"), indent=0)
print(len(files), "supporting files;", sum(os.path.getsize(os.path.join(P, f)) for f in files) // 1024, "KB")
