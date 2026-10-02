"""Audit a build: links, headings, metadata, schema, IDs, tag balance."""
import json, os, re, sys
from html.parser import HTMLParser

ROOT = sys.argv[1]
PREVIEW = "preview" in ROOT
VOID = {"area","base","br","col","embed","hr","img","input","link","meta","source","track","wbr",
        "path","circle","rect","line","stop","polyline","polygon","ellipse","use"}

class P(HTMLParser):
    def __init__(s):
        super().__init__(convert_charrefs=True)
        s.stack, s.errors, s.ids, s.hrefs, s.h1, s.title, s.meta, s.canon, s.ld = [], [], [], [], 0, None, None, None, []
        s._in_title = s._in_ld = False; s._buf = ""
    def handle_starttag(s, t, a):
        a = dict(a)
        if "id" in a: s.ids.append(a["id"])
        if t == "a" and "href" in a: s.hrefs.append(a["href"])
        if t in ("link",) and a.get("rel") in ("stylesheet","icon") : s.hrefs.append(a["href"])
        if t == "script" and a.get("src"): s.hrefs.append(a["src"])
        if t in ("source", "img", "video") and a.get("src"): s.hrefs.append(a["src"])
        if t == "video" and a.get("poster"): s.hrefs.append(a["poster"])
        for part in (a.get("srcset") or "").split(","):
            if part.strip(): s.hrefs.append(part.split()[0])
        if t == "h1": s.h1 += 1
        if t == "title" and not s.stack_has("svg"): s._in_title = True; s._buf = ""
        if t == "meta" and a.get("name") == "description": s.meta = a.get("content")
        if t == "link" and a.get("rel") == "canonical": s.canon = a.get("href")
        if t == "script" and a.get("type") == "application/ld+json": s._in_ld = True; s._buf = ""
        if t not in VOID: s.stack.append(t)
    def handle_startendtag(s, t, a):
        a = dict(a)
        if "id" in a: s.ids.append(a["id"])
    def stack_has(s, t): return t in s.stack
    def handle_endtag(s, t):
        if t == "title" and s._in_title: s.title = s._buf.strip(); s._in_title = False
        if t == "script" and s._in_ld: s.ld.append(s._buf); s._in_ld = False
        if t in VOID: return
        if not s.stack: s.errors.append(f"stray </{t}>"); return
        if s.stack[-1] == t: s.stack.pop(); return
        if t in s.stack:
            while s.stack and s.stack[-1] != t: s.errors.append(f"unclosed <{s.stack.pop()}> before </{t}>")
            s.stack.pop()
        else: s.errors.append(f"stray </{t}>")
    def handle_data(s, d):
        if s._in_title or s._in_ld: s._buf += d

pages = []
for dp, _, fs in os.walk(ROOT):
    for f in fs:
        if f.endswith(".html"): pages.append(os.path.join(dp, f))

problems, titles, metas, n_links = [], {}, {}, 0
for fp in sorted(pages):
    rel = os.path.relpath(fp, ROOT)
    p = P(); p.feed(open(fp, encoding="utf-8").read())
    is404 = rel == "404.html"
    if p.h1 != 1: problems.append(f"{rel}: {p.h1} <h1>")
    if not p.title: problems.append(f"{rel}: no <title>")
    if not p.meta: problems.append(f"{rel}: no meta description")
    if not p.canon: problems.append(f"{rel}: no canonical")
    titles.setdefault(p.title, []).append(rel); metas.setdefault(p.meta, []).append(rel)
    if p.title and len(p.title) > 70: problems.append(f"{rel}: title {len(p.title)} chars")
    if p.meta and len(p.meta) > 165: problems.append(f"{rel}: meta {len(p.meta)} chars")
    dup = {i for i in p.ids if p.ids.count(i) > 1}
    if dup: problems.append(f"{rel}: duplicate ids {sorted(dup)[:5]}")
    for e in p.errors[:3]: problems.append(f"{rel}: {e}")
    for blob in p.ld:
        try: json.loads(blob)
        except Exception as ex: problems.append(f"{rel}: bad JSON-LD {ex}")
    for h in p.hrefs:
        if re.match(r"^(https?:|tel:|mailto:|#|data:)", h): continue
        n_links += 1
        target = h.split("#")[0].split("?")[0]
        if is404:
            path = os.path.join(ROOT, target.lstrip("/"))
        else:
            path = os.path.normpath(os.path.join(os.path.dirname(fp), target))
        if target.endswith("/") or target in ("./", ""):
            path = os.path.join(path, "index.html")
        if not os.path.exists(path): problems.append(f"{rel}: broken link {h}")
for t, ps in titles.items():
    if len(ps) > 1 and not any("404" in x for x in ps): problems.append(f"duplicate title {t!r}: {ps}")
for m, ps in metas.items():
    if len(ps) > 1: problems.append(f"duplicate meta: {ps}")
print(f"{ROOT.split('/')[-1]}: {len(pages)} pages, {n_links} internal links checked")
print("\n".join(problems[:40]) if problems else "  no problems found")
print(f"  ({len(problems)} problems)")
