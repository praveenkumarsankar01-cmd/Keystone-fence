"""
Static site generator for Keystone Fence & Deck Co.

    python3 build.py              -> dist/      (production: clean directory URLs)
    python3 build.py --preview    -> preview/   (explicit index.html links, for the
                                                 claude.ai artifact preview)

Every page is rendered from data_services.py / data_site.py, so navigation,
breadcrumbs, canonicals, schema and internal links stay correct as pages are
added — the same job a CMS does.
"""
import datetime
import html
import io
import json
import os
import re
import shutil
import sys
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from drawings import drawing, logo_mark                     # noqa: E402
from data_services import SILOS                             # noqa: E402
from data_site import (CONFIG, HOME, HERO_VIDEO, WHY, STEPS, COMMITMENTS, AUDIENCES, HOME_FAQS,   # noqa: E402
                       ABOUT, CITIES, ALSO_SERVING, PROJECTS)

PREVIEW = "--preview" in sys.argv
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "preview" if PREVIEW else "dist")
BASE = CONFIG["base_url"].rstrip("/")
TODAY = datetime.date.today().isoformat()
FONTS = ("https://fonts.googleapis.com/css2?family=Big+Shoulders+Display:wght@700;800;900"
         "&family=Hanken+Grotesk:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap")

E = lambda s: html.escape(str(s), quote=False)
A = lambda s: html.escape(str(s), quote=True)
SVC = {f"{s['key']}/{c['slug']}": (s, c) for s in SILOS for c in s["children"]}
CITY = {c["slug"]: c for c in CITIES}
PAGES = []          # (path, title, type, target) for sitemap + build notes
MEDIA = os.path.join(ROOT, "static", "assets", "media")
PHOTOS = os.path.join(ROOT, "photos")      # photos/<key>/*.jpg — see photos()
WORD = {3: "three", 4: "four", 5: "five", 6: "six", 7: "seven"}
N_TRADES = WORD.get(len(SILOS), str(len(SILOS)))

IC = {
    "phone": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5.5 3.5h3l1.8 4.6-2.3 1.4a11.5 11.5 0 0 0 6.5 6.5l1.4-2.3 4.6 1.8v3a2 2 0 0 1-2.1 2A16.5 16.5 0 0 1 3.5 5.6a2 2 0 0 1 2-2.1z"/></svg>',
    "arrow": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
    "check": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 12.5l5 5L20 6.5"/></svg>',
    "chev": '<svg class="chev" viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M2 4l4 4 4-4"/></svg>',
    "menu": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>',
    "close": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>',
    "camera": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 8.5h4l1.8-2.5h6.4L17 8.5h4V19H3z"/><circle cx="12" cy="13.2" r="3.6"/></svg>',
    "estimate": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 2.5h9l4 4v15H6z"/><path d="M15 2.5v4h4M9 11h7M9 14.5h7M9 18h4"/></svg>',
    "post": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M10.5 2.5h3v14h-3zM8 16.5h8l1 5H7zM13.5 6h6M13.5 11h6"/></svg>',
    "locate": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 21.5s-6.5-6.2-6.5-11a6.5 6.5 0 0 1 13 0c0 4.8-6.5 11-6.5 11z"/><circle cx="12" cy="10.5" r="2.4"/></svg>',
    "clean": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14.5 2.5l-3 9M8 11.5h8l2.5 10h-13z"/><path d="M9.5 15.5l-.6 6M12 15.5v6M14.5 15.5l.6 6"/></svg>',
    "contact": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="8" r="4"/><path d="M4 21c1-4.2 4.2-6.5 8-6.5s7 2.3 8 6.5"/></svg>',
    "warranty": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 2.5l7.5 3v6c0 4.8-3.2 8.6-7.5 10-4.3-1.4-7.5-5.2-7.5-10v-6z"/><path d="M8.5 12l2.5 2.5 4.5-5"/></svg>',
    "pause": '<svg class="i-pause" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><rect x="6" y="5" width="4" height="14" rx="1"/><rect x="14" y="5" width="4" height="14" rx="1"/></svg>',
    "play": '<svg class="i-play" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M7 4.5v15l12.5-7.5z"/></svg>',
    "ext": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 4h6v6M20 4l-9 9M18 14v6H4V6h6"/></svg>',
}


# ═══════════════════════════════════════════════════════════ linking
class Ctx:
    def __init__(self, path, absolute=False):
        self.path = path            # page directory: "", "fencing/", "fencing/wood-privacy-fence/"
        self.absolute = absolute    # 404 page: served at any URL, so links must be root-absolute


def mail_text(addr):
    """Email shown with clean break points (after @, before dots) so narrow
    columns wrap it at punctuation instead of mid-word."""
    local, _, domain = addr.partition("@")
    return E(local) + "@<wbr>" + E(domain).replace(".", "<wbr>.")


def href(ctx, target):
    m = re.match(r"([^?#]*)(.*)", target)
    p, suffix = m.group(1), m.group(2)
    page = p == "" or p.endswith("/")
    if ctx.absolute:
        return "/" + p + suffix
    rel = os.path.relpath(p.rstrip("/") or ".", ctx.path.rstrip("/") or ".")
    if page:
        rel = "" if rel == "." else rel + "/"
        if PREVIEW:
            rel += "index.html"
        elif rel == "":
            rel = "./"
    return rel + suffix


def url(path):
    return f"{BASE}/{path}"


TEL = f'tel:{CONFIG["phone_e164"]}'


# ═══════════════════════════════════════════════════════════ schema
def business(full=False):
    n = {
        "@type": "HomeAndConstructionBusiness", "@id": BASE + "/#business",
        "name": CONFIG["name"], "url": BASE + "/", "telephone": CONFIG["phone_e164"], "email": CONFIG["email"],
        "image": BASE + "/assets/og.png", "logo": BASE + "/favicon.svg",
        "address": {"@type": "PostalAddress", "addressLocality": CONFIG["city"], "addressRegion": CONFIG["region"], "addressCountry": "US"},
        "areaServed": [{"@type": "City", "name": f"{c['name']}, TX"} for c in CITIES],
        "openingHoursSpecification": [{"@type": "OpeningHoursSpecification", "dayOfWeek": d, "opens": o, "closes": c}
                                      for d, o, c in CONFIG["hours_schema"]],
    }
    if full:
        n["hasOfferCatalog"] = {"@type": "OfferCatalog", "name": "Fence, gate and deck services", "itemListElement": [
            {"@type": "OfferCatalog", "name": s["name"], "itemListElement": [
                {"@type": "Offer", "itemOffered": {"@type": "Service", "name": c["name"], "url": url(f"{s['key']}/{c['slug']}/")}}
                for c in s["children"]]} for s in SILOS]}
    return n


def crumbs_schema(trail):
    return {"@type": "BreadcrumbList", "@id": url(trail[-1][1]) + "#breadcrumb", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": url(p)} for i, (n, p) in enumerate(trail)]}


def faq_schema(path, faqs):
    return {"@type": "FAQPage", "@id": url(path) + "#faq", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}


def webpage(path, title, meta, kind="WebPage"):
    return {"@type": kind, "@id": url(path) + "#webpage", "url": url(path), "name": title, "description": meta,
            "isPartOf": {"@id": BASE + "/#website"}, "about": {"@id": BASE + "/#business"}, "inLanguage": "en-US"}


def service_schema(path, name, desc):
    return {"@type": "Service", "@id": url(path) + "#service", "name": name, "serviceType": name, "description": desc,
            "provider": {"@id": BASE + "/#business"}, "url": url(path),
            "areaServed": [{"@type": "City", "name": f"{c['name']}, TX"} for c in CITIES]}


# ═══════════════════════════════════════════════════════════ chrome
def head(ctx, path, title, meta, graph):
    robots = "" if CONFIG["index"] else '<meta name="robots" content="noindex, nofollow">\n'
    gsc = f'<meta name="google-site-verification" content="{A(CONFIG["gsc_verification"])}">\n' if CONFIG["gsc_verification"] else ""
    ga = ""
    if CONFIG["ga4_id"] and not PREVIEW:
        g = A(CONFIG["ga4_id"])
        ga = (f'<script async src="https://www.googletagmanager.com/gtag/js?id={g}"></script>\n'
              f"<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','{g}');</script>\n")
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return f"""<!doctype html>
<html lang="en-US">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{A(meta)}">
<link rel="canonical" href="{A(url(path))}">
{robots}{gsc}<meta property="og:type" content="website">
<meta property="og:site_name" content="{A(CONFIG['name'])}">
<meta property="og:title" content="{A(title)}">
<meta property="og:description" content="{A(meta)}">
<meta property="og:url" content="{A(url(path))}">
<meta property="og:image" content="{A(BASE + '/assets/og.png')}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#F1F1EC">
<link rel="icon" href="{href(ctx, 'favicon.svg')}" type="image/svg+xml">
<link rel="preload" href="{href(ctx, 'assets/fonts/big-shoulders-display.woff2')}" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{href(ctx, 'assets/fonts/hanken-grotesk.woff2')}" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{href(ctx, 'assets/site.css')}">
<script type="application/ld+json">{ld}</script>
{ga}</head>
<body data-form-mode="{'preview' if PREVIEW else 'live'}">
"""


def header(ctx, active):
    nav = []
    for s in SILOS:
        cur = ' aria-current="page"' if active == s["key"] else ""
        items = "".join(f'<li><a href="{href(ctx, s["key"] + "/" + c["slug"] + "/")}"><span class="mc">{c["code"]}</span>{E(c["name"])}</a></li>'
                        for c in s["children"])
        nav.append(f'''<div class="nav-item"><a class="nav-link" href="{href(ctx, s["key"] + "/")}"{cur}>{E(s["nav"])}{IC["chev"]}</a>
<div class="mega"><div class="mega-intro">{drawing(s["drawing"], False)}<a href="{href(ctx, s["key"] + "/")}">All {E(s["name"].lower())} →</a><small>{E(s["card"])}</small></div>
<ul class="mega-list">{items}</ul></div></div>''')
    for key, label, p in (("projects", "Projects", "projects/"), ("areas", "Service Areas", "service-areas/"), ("about", "About", "about/")):
        cur = ' aria-current="page"' if active == key else ""
        nav.append(f'<div class="nav-item"><a class="nav-link" href="{href(ctx, p)}"{cur}>{label}</a></div>')

    groups = []
    for s in SILOS:
        kids = "".join(f'<li><a href="{href(ctx, s["key"] + "/" + c["slug"] + "/")}">{E(c["name"])}</a></li>' for c in s["children"])
        groups.append(f'''<div class="d-group"><button class="d-row" type="button" aria-expanded="false">{E(s["name"])}{IC["chev"]}</button>
<ul class="d-sub"><li><a class="hub" href="{href(ctx, s["key"] + "/")}">All {E(s["name"].lower())}</a></li>{kids}</ul></div>''')
    for label, p in (("Projects", "projects/"), ("Service Areas", "service-areas/"), ("About", "about/"), ("Contact", "contact/")):
        groups.append(f'<div class="d-group"><a class="d-row" href="{href(ctx, p)}">{label}</a></div>')

    brand = (f'<a class="brand" href="{href(ctx, "")}" aria-label="{A(CONFIG["name"])} — home">{logo_mark()}'
             f'<span class="brand-word"><span class="brand-name">Keystone</span><span class="brand-sub">Fence &amp; Deck Co.</span></span></a>')
    hours = " · ".join(f"{d} {h}" for d, h in CONFIG["hours"][:2])
    return f"""<a class="skip" href="#main">Skip to content</a>
<div class="topbar"><div class="wrap topbar-in">
<span>{IC['locate']}Plano · serving Collin County &amp; North Dallas</span>
<span>{E(hours)}</span>
<a href="{TEL}" data-loc="topbar">{IC['phone']}<span class="tel">{E(CONFIG['phone'])}</span></a>
</div></div>
<header class="hdr"><div class="wrap hdr-in">
{brand}
<nav class="nav" aria-label="Main">{''.join(nav)}</nav>
<div class="hdr-cta">
<a class="hdr-tel" href="{TEL}" data-loc="header"><small>Call us</small><span>{E(CONFIG['phone'])}</span></a>
<a class="btn btn-primary" href="{href(ctx, 'free-estimate/')}">Free Estimate</a>
<a class="icon-btn" href="{TEL}" data-loc="header-mobile" aria-label="Call {A(CONFIG['phone'])}">{IC['phone']}</a>
<button class="icon-btn js-menu" type="button" aria-expanded="false" aria-controls="drawer" aria-label="Open menu">{IC['menu']}</button>
</div></div></header>
<div class="drawer" id="drawer" aria-hidden="true" role="dialog" aria-label="Menu">
<div class="drawer-top">{brand}<button class="icon-btn js-close" type="button" aria-label="Close menu" style="display:inline-flex">{IC['close']}</button></div>
<div class="drawer-body">{''.join(groups)}</div>
<div class="drawer-foot"><a class="btn btn-primary btn-block" href="{href(ctx, 'free-estimate/')}">Request a Free Estimate</a>
<a class="btn btn-line btn-block" href="{TEL}" data-loc="drawer">{IC['phone']} Call {E(CONFIG['phone'])}</a></div>
</div>
"""


def footer(ctx, estimate_page=False):
    hubs = "".join(f'<li><a href="{href(ctx, s["key"] + "/")}">{E(s["name"])}</a></li>' for s in SILOS)
    popular = ["fencing/wood-privacy-fence", "fencing/wrought-iron-fence", "gates/driveway-gates", "decks/wood-decks", "repair/fence-repair", "land-clearing/acreage-clearing", "land-clearing/forestry-mulching"]
    pop = "".join(f'<li><a href="{href(ctx, p + "/")}">{E(SVC[p][1]["name"])}</a></li>' for p in popular)
    areas = "".join(f'<li><a href="{href(ctx, "service-areas/" + c["slug"] + "/")}">{E(c["name"])}</a></li>' for c in CITIES)
    # time ranges never split ("6:00 / pm"); they wrap whole, after the day
    hours = "".join(f'<li>{E(d)}: {f"<span class=nowrap>{E(h)}</span>" if any(ch.isdigit() for ch in h) else E(h)}</li>' for d, h in CONFIG["hours"])
    disclose = ""
    if CONFIG["fictional"]:
        disclose = (f'<p class="ftr-disclose">{E(CONFIG["name"])} is a fictional company, not affiliated with any business of the same or a similar name. Website designed and built by '
                    f'<a href="{A(CONFIG["credit_url"])}">{E(CONFIG["credit_name"])}</a> · '
                    f'<a href="{href(ctx, "build-notes/")}">How this site is built</a></p>')
    mbar = (f'<div class="mbar" style="grid-template-columns:1fr"><a class="btn btn-primary" href="{TEL}" data-loc="mobile-bar">{IC["phone"]} Call {E(CONFIG["phone"])}</a></div>'
            if estimate_page else
            f'<div class="mbar"><a class="btn btn-ghost-dark" href="{TEL}" data-loc="mobile-bar">{IC["phone"]} Call</a>'
            f'<a class="btn btn-primary" href="{href(ctx, "free-estimate/")}">Free Estimate</a></div>')
    return f"""<footer class="ftr"><div class="wrap">
<div class="ftr-grid">
<div class="ftr-about">
<a class="brand" href="{href(ctx, '')}">{logo_mark()}<span class="brand-word"><span class="brand-name">Keystone</span><span class="brand-sub">Fence &amp; Deck Co.</span></span></a>
<p>Fences, gates, decks, repairs and land clearing across Plano, Collin County and North Dallas — built on steel posts and priced in writing after a walk of your property.</p>
</div>
<div><h2>Services</h2><ul>{hubs}<li><a href="{href(ctx, 'services/')}">All services</a></li></ul></div>
<div><h2>Popular</h2><ul>{pop}</ul></div>
<div><h2>Service areas</h2><ul>{areas}<li><a href="{href(ctx, 'service-areas/')}">All areas</a></li></ul></div>
<div><h2>Contact</h2><ul>
<li><a class="ftr-tel" href="{TEL}" data-loc="footer">{E(CONFIG['phone'])}</a></li>
<li><a class="ftr-mail" href="mailto:{A(CONFIG['email'])}">{mail_text(CONFIG['email'])}</a></li>
{hours}
<li><a href="{href(ctx, 'free-estimate/')}">Request a free estimate</a></li>
<li><a href="{href(ctx, 'projects/')}">Projects</a> · <a href="{href(ctx, 'about/')}">About</a> · <a href="{href(ctx, 'contact/')}">Contact</a></li>
</ul></div>
</div>
<div class="ftr-base"><p>© <span class="js-year">{datetime.date.today().year}</span> {E(CONFIG['name'])} · <a href="{href(ctx, 'privacy/')}">Privacy</a></p>{disclose}</div>
</div></footer>
{mbar}
<script>window.KEYSTONE_FORM={json.dumps({"endpoint": CONFIG["form_endpoint"], "key": CONFIG["form_access_key"], "phone": CONFIG["phone"], "mode": "preview" if PREVIEW else "live"})};</script>
<script src="{href(ctx, 'assets/site.js')}" defer></script>
</body>
</html>
"""


def crumbs(ctx, trail):
    items = []
    for i, (n, p) in enumerate(trail):
        if i == len(trail) - 1:
            items.append(f'<li><span aria-current="page">{E(n)}</span></li>')
        else:
            items.append(f'<li><a href="{href(ctx, p)}">{E(n)}</a></li>')
    return f'<nav class="crumbs" aria-label="Breadcrumb"><div class="wrap"><ol>{"".join(items)}</ol></div></nav>'


def write(path, html_text, title, kind, target=""):
    PAGES.append((path, title, kind, target))
    fn = os.path.join(OUT, path, "index.html") if not path.endswith(".html") else os.path.join(OUT, path)
    os.makedirs(os.path.dirname(fn), exist_ok=True)
    with open(fn, "w", encoding="utf-8") as f:
        f.write(html_text)


def page(path, title, meta, body, graph, active=None, trail=None, estimate_page=False, kind="", target=""):
    ctx = Ctx(path)
    g = [business(full=(path == "")), webpage(path, title, meta)] + graph
    if path == "":
        g.insert(0, {"@type": "WebSite", "@id": BASE + "/#website", "url": BASE + "/", "name": CONFIG["name"], "publisher": {"@id": BASE + "/#business"}})
    if trail:
        g.append(crumbs_schema(trail))
        g[1]["breadcrumb"] = {"@id": url(trail[-1][1]) + "#breadcrumb"}
    out = head(ctx, path, title, meta, g) + header(ctx, active)
    if trail:
        out += crumbs(ctx, trail)
    out += f'<main id="main">{body(ctx)}</main>' + footer(ctx, estimate_page)
    write(path, out, title, kind, target)


# ═══════════════════════════════════════════════════════════ blocks
def sheet(key, tag, labels=True):
    return f'<figure class="sheet-frame"><span class="sheet-tag">{E(tag)}</span>{drawing(key, labels)}</figure>'


def btns(ctx, service=None, line_cls="btn-line"):
    q = f"?service={service}" if service else ""
    return (f'<div class="btn-row"><a class="btn btn-primary" href="{href(ctx, "free-estimate/" + q)}">Request a free estimate {IC["arrow"]}</a>'
            f'<a class="btn {line_cls}" href="{TEL}" data-loc="hero">{IC["phone"]} <span class="tel">{E(CONFIG["phone"])}</span></a></div>')


def svc_card(ctx, path, sub=None):
    s, c = SVC[path]
    return (f'<a class="card" href="{href(ctx, path + "/")}"><div class="card-art">{drawing(c["drawing"], False)}</div>'
            f'<div class="card-body"><span class="card-code">{c["code"]}</span><h3>{E(c["name"])}</h3><p>{E(sub or c["card"])}</p>'
            f'<span class="card-more">View service {IC["arrow"]}</span></div></a>')


def silo_card(ctx, s):
    links = "".join(f'<li><a href="{href(ctx, s["key"] + "/" + c["slug"] + "/")}"><span>{E(c["name"])}</span><span class="mc">{c["code"]}</span></a></li>'
                    for c in s["children"][:4])
    return (f'<div class="card silo-card"><div class="card-art">{drawing(s["drawing"], False)}</div><div class="card-body">'
            f'<div class="silo-head"><span class="card-code">{s["letter"]} — {E(s["nav"])}</span><span class="silo-count">{len(s["children"])} services</span></div>'
            f'<h3><a href="{href(ctx, s["key"] + "/")}">{E(s["name"])}</a></h3><p>{E(s["card"])}</p>'
            f'<ul class="card-links">{links}</ul><a class="card-more" href="{href(ctx, s["key"] + "/")}">All {E(s["nav"].lower())} {IC["arrow"]}</a></div></div>')


def faq_block(faqs, title="Common questions", code="FAQ"):
    items = "".join(f'<details><summary>{E(q)}</summary><div class="a"><p>{E(a)}</p></div></details>' for q, a in faqs)
    return f'<div class="sec-head"><span class="code">{E(code)}</span><h2>{E(title)}</h2></div><div class="faq">{items}</div>'


def factors_block(factors, title="What affects your estimate"):
    lis = "".join(f"<li><strong>{E(t)}</strong><span>{E(d)}</span></li>" for t, d in factors)
    return (f'<h2>{E(title)}</h2><ul class="factors">{lis}</ul>'
            '<div class="note"><strong>Why we don\'t post prices online</strong>Two fences of the same length can differ widely in cost once grade, '
            'access, gates and what\'s in the ground are counted. We would rather give you one accurate written number than a range that doesn\'t hold up.</div>')


def compare_table(cols, rows, note):
    th = "".join(f'<th scope="col">{E(c)}</th>' for c in cols)
    trs = "".join("<tr>" + f'<th scope="row">{E(r[0])}</th>' + "".join(f"<td>{E(x)}</td>" for x in r[1:]) + "</tr>" for r in rows)
    return f'<div class="spec-wrap"><table class="compare"><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div><p class="help">{E(note)}</p>'


def cta_band(ctx, title="Let's walk your property line.", text=None, service=None):
    text = text or "Tell us about the project and we'll schedule a visit. You'll get an itemized written estimate — no prices guessed online, no pressure."
    q = f"?service={service}" if service else ""
    return f"""<section class="sec band"><div class="wrap cta-band">
<div><span class="code">Free on-site estimate</span><h2 style="margin:14px 0 14px">{E(title)}</h2><p class="lede" style="margin:0">{E(text)}</p></div>
<div><a class="btn btn-primary" href="{href(ctx, 'free-estimate/' + q)}">Request a free estimate {IC['arrow']}</a>
<p style="margin:18px 0 0;font:500 12px var(--mono);letter-spacing:.12em;text-transform:uppercase">Or call</p>
<a class="tel-big" href="{TEL}" data-loc="cta-band">{E(CONFIG['phone'])}</a></div>
</div></section>"""


def areas_chips(ctx, lead="We serve"):
    cities = "".join(f'<li><a href="{href(ctx, "service-areas/" + c["slug"] + "/")}">{IC["locate"]}{E(c["name"])}</a></li>' for c in CITIES)
    also = "".join(f"<li><span>{E(n)}</span></li>" for n in ALSO_SERVING)
    return (f'<ul class="chips" aria-label="{A(lead)}">{cities}</ul>'
            f'<p class="help" style="margin:16px 0 8px">Also serving nearby:</p><ul class="chips">{also}</ul>')


def coverage_svg(ctx, current=None):
    roads = [("M318 400 L328 320 L336 250 L360 196 L395 125 L412 18", "US-75", 418, 30),
             ("M196 400 L188 250 L174 170 L194 76 L200 12", "DNT", 206, 22),
             ("M28 262 L170 190 L300 160 L395 125 L470 92", "SH-121", 30, 252),
             ("M24 334 L300 316 L512 300", "PGBT", 478, 292)]
    parts = [f'<circle cx="300" cy="250" r="{r}" class="cv-ring"/>' for r in (110, 200)]
    for d, lbl, lx, ly in roads:
        parts.append(f'<path d="{d}" class="cv-road"/><text x="{lx}" y="{ly}" class="cv-sub">{lbl}</text>')
    for c in CITIES:
        x, y = c["xy"]
        cur = c["slug"] == current
        cls = "cv-home" if c["slug"] == "plano" else "cv-dot"
        r = 8 if cur else 5.5
        ring = f'<circle cx="{x}" cy="{y}" r="13" fill="none" stroke="var(--cedar)" stroke-width="1.5"/>' if cur else ""
        parts.append(f'<a class="cv-link" href="{href(ctx, "service-areas/" + c["slug"] + "/")}">{ring}<circle cx="{x}" cy="{y}" r="{r}" class="{cls}"/>'
                     f'<text x="{x + 12}" y="{y - 2}" class="cv-lbl">{E(c["name"].upper())}</text>'
                     f'<text x="{x + 12}" y="{y + 11}" class="cv-sub">{"HOME BASE" if c["slug"] == "plano" else E(c["county"].upper())}</text></a>')
    parts.append('<text x="300" y="392" text-anchor="middle" class="cv-sub">↓ DALLAS</text>')
    return (f'<svg viewBox="0 0 520 400" role="img" aria-labelledby="cv-t">'
            f'<title id="cv-t">Schematic map of the North Dallas cities Keystone serves, centred on Plano</title>{"".join(parts)}</svg>')


def gmap(ctx, query, zoom, place, note, current=None):
    """Google Map of a place. Live builds embed Google's keyless map (lazy-loaded);
    the artifact preview can't load third-party frames, so it shows the schematic."""
    q = urllib.parse.quote_plus(query)
    link = f"https://www.google.com/maps/search/?api=1&query={q}"
    if PREVIEW:
        box = (f'<div class="map-box map-fallback">{coverage_svg(ctx, current)}</div>'
               f'<p class="map-note">Preview: schematic shown · the live Google Map of {E(place)} loads here on the published site</p>')
    else:
        box = (f'<div class="map-box"><iframe src="https://maps.google.com/maps?q={q}&amp;t=m&amp;z={zoom}&amp;output=embed&amp;iwloc=near" '
               f'title="Google Map of {A(place)}" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe></div>')
    return (f'<figure class="sheet-frame map-frame"><span class="sheet-tag">Map · {E(place)}</span>{box}'
            f'<figcaption class="map-cap"><span>{E(note)}</span><a href="{A(link)}" target="_blank" rel="noopener">Open in Google Maps {IC["ext"]}<span class="sr-only"> (opens in a new tab)</span></a></figcaption></figure>')


def hero_media(ctx):
    """Home-hero video when its file exists, otherwise the F-01 elevation sheet."""
    v = dict(HERO_VIDEO)
    if not os.path.exists(os.path.join(MEDIA, v["mp4"])):
        return sheet("board_on_board", "Sheet F-01 · Elevation")
    real = os.path.join(MEDIA, "site-walk.json")     # written by ingest_video.py for real footage
    if os.path.exists(real):
        v.update(json.load(open(real, encoding="utf-8")), transcript=[])
    said = " ".join(f"{E(who)}: “{E(line)}”" for who, line in v["transcript"])
    return (f'<figure class="sheet-frame vid-frame"><span class="sheet-tag">{E(v["tag"])}</span>'
            f'<button class="vid-btn" type="button" hidden>{IC["pause"]}{IC["play"]}<span class="vid-lbl">Pause</span><span class="sr-only"> video</span></button>'
            f'<div class="vid-box"><video class="js-vid" muted loop playsinline preload="metadata" '
            f'poster="{href(ctx, "assets/media/" + v["poster"])}" aria-describedby="vid-desc">'
            f'<source src="{href(ctx, "assets/media/" + v["mp4"])}" type="video/mp4">'
            + (f'<source src="{href(ctx, "assets/media/" + v["webm"])}" type="video/webm">' if os.path.exists(os.path.join(MEDIA, v.get("webm", "-"))) else "")
            + '</video></div>'
            f'<figcaption id="vid-desc" class="sr-only">{E(v["desc"])} {said}</figcaption></figure>')


# ── photos ────────────────────────────────────────────────────────────────
# Drop images into photos/<key>/ — key is "home", a silo ("fencing"), a service
# ("fencing/wood-privacy-fence") or a project ("projects/F-01"). An optional
# captions.json maps file name -> {"alt": ..., "caption": ...}. Each image is
# rotated per its EXIF, converted to sRGB, stripped of all metadata (GPS
# included) and written at 800 and 1600 px wide as WebP and JPEG.
_PHOTO_CACHE = {}


def photos(key):
    if key in _PHOTO_CACHE:
        return _PHOTO_CACHE[key]
    src_dir, found = os.path.join(PHOTOS, *key.split("/")), []
    if os.path.isdir(src_dir):
        meta_path = os.path.join(src_dir, "captions.json")
        meta = json.load(open(meta_path, encoding="utf-8")) if os.path.exists(meta_path) else {}
        for f in sorted(os.listdir(src_dir)):
            if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                found.append(_process_photo(os.path.join(src_dir, f), key, meta.get(f, {})))
    _PHOTO_CACHE[key] = found
    return found


def _process_photo(src, key, meta):
    from PIL import Image, ImageCms, ImageOps
    slug = re.sub(r"[^a-z0-9]+", "-", f"{key}-{os.path.splitext(os.path.basename(src))[0]}".lower()).strip("-")
    im = ImageOps.exif_transpose(Image.open(src))
    icc = im.info.get("icc_profile")
    if icc:
        try:
            im = ImageCms.profileToProfile(im, ImageCms.ImageCmsProfile(io.BytesIO(icc)), ImageCms.createProfile("sRGB"), outputMode="RGB")
        except Exception:
            pass
    im = im.convert("RGB")
    w0, h0 = im.size
    widths = sorted({w for w in (800, 1600) if w < w0} | {min(w0, 1600)})
    dst = os.path.join(OUT, "assets", "photos")
    os.makedirs(dst, exist_ok=True)
    for w in widths:
        r = im.resize((w, round(h0 * w / w0)), Image.LANCZOS)
        r.save(os.path.join(dst, f"{slug}-{w}.webp"), "WEBP", quality=80, method=6)
        r.save(os.path.join(dst, f"{slug}-{w}.jpg"), "JPEG", quality=82, optimize=True, progressive=True)
    name = re.sub(r"^[\d\s_-]+", "", os.path.splitext(os.path.basename(src))[0]).replace("-", " ").replace("_", " ").strip()
    return dict(slug=slug, widths=widths, ratio=h0 / w0, alt=meta.get("alt", name.capitalize()), caption=meta.get("caption", ""))


def picture(ctx, p, sizes):
    base = "assets/photos/" + p["slug"]
    def srcset(ext):
        return ", ".join(f'{href(ctx, f"{base}-{w}.{ext}")} {w}w' for w in p["widths"])
    w, small = p["widths"][-1], href(ctx, f"{base}-{p['widths'][0]}.jpg")
    return (f'<picture><source type="image/webp" srcset="{srcset("webp")}" sizes="{sizes}">'
            f'<img src="{small}" srcset="{srcset("jpg")}" sizes="{sizes}" '
            f'width="{w}" height="{round(w * p["ratio"])}" alt="{A(p["alt"])}" loading="lazy" decoding="async"></picture>')


def photo_strip(ctx, keys, title, cls="sec tight"):
    shots = [p for k in keys for p in photos(k)][:3]
    if not shots:
        return ""
    figs = "".join(f'<figure class="ph">{picture(ctx, p, "(max-width: 620px) 82vw, 380px")}'
                   + (f"<figcaption>{E(p['caption'])}</figcaption>" if p["caption"] else "") + "</figure>" for p in shots)
    note = '<p class="help" style="margin:12px 0 0">Photos are illustrative.</p>' if CONFIG["fictional"] else ""
    return (f'<section class="{cls}"><div class="wrap"><div class="sec-head"><span class="code">Gallery</span><h2>{E(title)}</h2></div>'
            f'<div class="ph-grid">{figs}</div>{note}</div></section>')


def hidden_inputs(kind, subject):
    return (f'<input type="hidden" name="access_key" value="{A(CONFIG["form_access_key"])}">'
            f'<input type="hidden" name="subject" value="{A(subject)}">'
            f'<input type="hidden" name="from_name" value="{A(CONFIG["short"])} website">'
            f'<input type="hidden" name="form" value="{kind}">'
            '<input type="checkbox" name="botcheck" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">')


def fld(fid, name, label, kind="text", req=True, auto=None, err="Please fill this in.", extra="", help_=None, area=False, rows=5):
    mark = ' <span class="req" aria-hidden="true">*</span>' if req else ' <span class="opt">(optional)</span>'
    attrs = (f'id="{fid}" name="{name}"' + (" required" if req else "") + (f' autocomplete="{auto}"' if auto else "") +
             f' aria-describedby="{fid}-e{" " + fid + "-h" if help_ else ""}"' + extra)
    ctl = (f'<textarea class="textarea" rows="{rows}" {attrs}></textarea>' if area else f'<input class="input" type="{kind}" {attrs}>')
    hp = f'<span class="help" id="{fid}-h">{E(help_)}</span>' if help_ else ""
    return f'<div class="field"><label for="{fid}">{E(label)}{mark}</label>{ctl}{hp}<span class="err" id="{fid}-e">{E(err)}</span></div>'


def service_select(fid, preselect=None):
    groups = []
    for s in SILOS:
        opts = "".join(f'<option value="{A(s["name"] + " — " + c["name"])}" data-slug="{c["slug"]}"{" selected" if c["slug"] == preselect else ""}>{E(c["name"])}</option>'
                       for c in s["children"])
        groups.append(f'<optgroup label="{A(s["name"])}">{opts}</optgroup>')
    return (f'<div class="field"><label for="{fid}">Service needed <span class="req" aria-hidden="true">*</span></label>'
            f'<select class="select" id="{fid}" name="service" required aria-describedby="{fid}-e"><option value="">Choose a service…</option>'
            f'{"".join(groups)}<option value="Not sure — help me choose" data-slug="not-sure">Not sure yet — help me choose</option></select>'
            f'<span class="err" id="{fid}-e">Choose the service closest to your project.</span></div>')


def choice(name, legend, opts, req=True, err="Choose one."):
    mark = ' <span class="req" aria-hidden="true">*</span>' if req else ' <span class="opt">(optional)</span>'
    items = "".join(f'<label><input type="radio" name="{name}" value="{A(o)}"><span>{E(o)}</span></label>' for o in opts)
    return (f'<fieldset{" data-required" if req else ""}><legend class="legend">{E(legend)}{mark}</legend>'
            f'<div class="choice" style="margin-top:8px">{items}</div><span class="err">{E(err)}</span></fieldset>')


def success_block(heading, steps):
    lis = "".join(f"<li>{E(s)}</li>" for s in steps)
    return (f'<div class="success" role="status" tabindex="-1"><span class="stamp">{IC["check"].replace("<svg", "<svg width=16 height=16")} Request received</span>'
            f'<h2 style="font-size:2rem">{E(heading)}</h2><ol>{lis}</ol>'
            '<p class="note js-photo-note" hidden><strong>Your photos didn\'t come through</strong>Your request arrived, but the photos were too large to send. '
            f'Reply to our email or text them to {E(CONFIG["phone"])} and we\'ll add them to your file.</p>'
            '<p class="help js-preview-note" hidden>Preview: nothing was sent. On the live site this request is emailed to the team.</p>'
            f'<p style="margin:0">Need us sooner? Call <a href="{TEL}" class="tel">{E(CONFIG["phone"])}</a>.</p></div>')


def quick_form(ctx, svc_name, slug):
    return f"""<div class="quote-card" id="quote" data-form-shell>
<h2>Free estimate</h2>
<p>Tell us a little about the job and we'll call to book a visit. No prices guessed online.</p>
<form class="form js-lead" data-form="quick" novalidate>
{hidden_inputs("quick", f"Quick estimate request — {svc_name}")}
<input type="hidden" name="service" value="{A(svc_name)}">
{fld("q-name", "name", "Name", auto="name", err="Please enter your name.")}
{fld("q-phone", "phone", "Phone", kind="tel", auto="tel", err="Enter a phone number with area code.", extra=' data-phone inputmode="tel"')}
{fld("q-addr", "address", "Project address or ZIP", auto="street-address", err="Where is the project?")}
{fld("q-msg", "message", "A few details", req=False, area=True, rows=3, help_="Rough length, height, gates, timeline — whatever you know.")}
<button class="btn btn-primary btn-block" type="submit">Request my estimate {IC['arrow']}</button>
<div class="form-status" role="alert"></div>
<p class="help" style="margin:0">Want to add photos? <a href="{href(ctx, 'free-estimate/?service=' + slug)}">Use the full estimate form</a>.</p>
</form>
{success_block("Thanks — we'll be in touch.", ["We'll call within one business day to book a visit.", "We walk the property and talk through options.", "You get an itemized written estimate by email."])}
</div>"""


# ═══════════════════════════════════════════════════════════ pages
def build_home():
    def body(ctx):
        proof = "".join(f"<li>{IC['check']}{E(p)}</li>" for p in HOME["proof"])
        silos = "".join(silo_card(ctx, s) for s in SILOS)
        pts = "".join(f'<li>{IC["check"]}<div><strong>{E(t)}</strong><br><span style="font-weight:400;color:var(--graphite)">{E(d)}</span></div></li>' for t, d in WHY["points"])
        steps = "".join(f"<li><h3>{E(t)}</h3><p>{E(d)}</p></li>" for t, d in STEPS)
        feat = "".join(project_card(ctx, p) for p in PROJECTS[:1] + PROJECTS[5:6] + PROJECTS[8:9])
        aud = "".join(f"<div><h3>{E(t)}</h3><p>{E(d)}</p></div>" for t, d in AUDIENCES)
        com = "".join(f"<div>{IC[i]}<h3>{E(t)}</h3><p>{E(d)}</p></div>" for i, t, d in COMMITMENTS)
        return f"""
<section class="hero"><div class="wrap hero-grid">
<div><span class="code">{E(HOME['eyebrow'])}</span><h1>{E(HOME['h1'])}</h1><p class="lede">{E(HOME['lede'])}</p>{btns(ctx)}
<ul class="hero-proof">{proof}</ul></div>
{hero_media(ctx)}
</div></section>

<section class="sec"><div class="wrap">
<div class="sec-head"><span class="code">{N_TRADES.capitalize()} trades · one crew</span><h2>What we build</h2>
<p class="lede">Every service has its own page, its own specs and the same standards underneath. Start with the trade that fits your project.</p></div>
<div class="grid silo-grid">{silos}
<div class="card silo-cta"><div class="card-body">
<span class="card-code">Not sure where to start?</span>
<h3>Most jobs touch more than one trade</h3>
<p>A new fence often starts with clearing the line; a deck often starts with grading. Tell us the project and we'll scope every part of it.</p>
<a class="btn btn-primary" href="{href(ctx, 'free-estimate/')}">Request a free estimate {IC['arrow']}</a>
<a class="card-more" href="{href(ctx, 'services/')}">See every service {IC['arrow']}</a>
</div></div></div>
</div></section>
{photo_strip(ctx, ["home"], "The work, up close", "sec tight alt")}
<section class="sec sheet rule-top"><div class="wrap split">
<div><span class="code">{E(WHY['code'])}</span><h2 style="margin:14px 0 18px">{E(WHY['title'])}</h2>
{''.join(f'<p>{E(p)}</p>' for p in WHY['body'])}<ul class="checks" style="margin-top:20px">{pts}</ul>
<p style="margin:0"><a href="{href(ctx, 'repair/post-replacement/')}"><strong>Already leaning? Read about post replacement</strong></a></p></div>
{sheet("post_section", "Sheet R-04 · Section")}
</div></section>

<section class="sec alt"><div class="wrap">
<div class="sec-head"><span class="code">How it works</span><h2>How an estimate works</h2>
<p class="lede">No online price guesses. Four steps from first call to finished fence.</p></div>
<ol class="steps">{steps}</ol>
</div></section>

<section class="sec"><div class="wrap">
<div class="sec-head"><span class="code">Typical projects</span><h2>What a job looks like</h2>
<p class="lede">Typical scopes for the work we do most, with the specs that drive the estimate.</p></div>
<div class="proj proj-rail">{feat}</div>
<p style="margin:22px 0 0"><a href="{href(ctx, 'projects/')}"><strong>See all project types</strong></a></p>
</div></section>

<section class="sec sheet rule-top"><div class="wrap">
<div class="sec-head"><span class="code">Who we build for</span><h2>Residential and commercial</h2></div>
<div class="aud">{aud}</div>
</div></section>

<section class="sec alt"><div class="wrap">
<div class="sec-head"><span class="code">Our standards</span><h2>What you can hold us to</h2>
<p class="lede">Not reviews — commitments. Each of these is written into how we quote and build.</p></div>
<div class="commit">{com}</div>
</div></section>

<section class="sec"><div class="wrap split">
<div><span class="code">Service areas</span><h2 style="margin:14px 0 16px">Based in Plano, working across Collin County</h2>
<p class="lede" style="margin-bottom:22px">Our crews work from Plano across North Dallas. Every city page covers the local details — HOAs, alleys, permits and soil.</p>
{areas_chips(ctx)}</div>
{gmap(ctx, "Collin County, Texas", 10, "Collin County, TX", "Based in Plano · serving Collin County & North Dallas")}
</div></section>

<section class="sec sheet rule-top"><div class="wrap measure">{faq_block(HOME_FAQS)}</div></section>
{cta_band(ctx)}
"""
    page("", HOME["title"], HOME["meta"], body, [faq_schema("", HOME_FAQS)], kind="Home", target="fence company plano tx")


def project_card(ctx, p):
    s = next(x for x in SILOS if x["key"] == p["silo"])
    spec = "".join(f"<li><span>{E(k)}</span><span>{E(v)}</span></li>" for k, v in p["spec"])
    shot = photos("projects/" + p["code"])
    art = picture(ctx, shot[0], "(max-width: 620px) 86vw, 380px") if shot else drawing(p["drawing"], False)
    return (f'<article class="card proj-card" data-silo="{p["silo"]}"><div class="card-art{" has-photo" if shot else ""}">{art}</div>'
            f'<div class="card-body"><span class="card-code">{p["code"]} · {E(s["nav"])}</span><h3>{E(p["title"])}</h3>'
            f'<span class="proj-meta">{E(p["where"])} · {E(p["who"])}</span><p>{E(p["story"])}</p><ul class="proj-spec">{spec}</ul></div></article>')


def build_hub(s):
    path = s["key"] + "/"
    trail = [("Home", ""), (s["name"], path)]

    def body(ctx):
        cards = "".join(svc_card(ctx, f"{s['key']}/{c['slug']}") for c in s["children"])
        return f"""
<section class="page-hero"><div class="wrap hero-grid">
<div><span class="code">{s['letter']} — {E(s['name'])}</span><h1>{E(s['h1'])}</h1><p class="lede">{E(s['lede'])}</p>{btns(ctx)}</div>
{sheet(s['drawing'], f"Sheet {s['children'][0]['code']} · Elevation")}
</div></section>
<section class="sec tight"><div class="wrap measure prose">{''.join(f'<p>{E(p)}</p>' for p in s['intro'])}</div></section>
{photo_strip(ctx, [s['key']], s['name'] + ' up close', "sec tight ph-sec")}
<section class="sec tight" style="padding-top:0"><div class="wrap">
<div class="sec-head"><span class="code">{len(s['children'])} services</span><h2>{E(s['name'])} services</h2></div>
<div class="grid g3">{cards}</div></div></section>
<section class="sec alt"><div class="wrap">
<div class="sec-head"><span class="code">Guide</span><h2>{E(s['guide_title'])}</h2></div>
{compare_table(s['guide_cols'], s['guide_rows'], s['guide_note'])}
</div></section>
<section class="sec"><div class="wrap measure prose">{factors_block(s['factors'])}</div></section>
<section class="sec sheet rule-top"><div class="wrap measure">{faq_block(s['faqs'])}</div></section>
<section class="sec tight"><div class="wrap"><div class="sec-head"><span class="code">Service areas</span><h2>Where we build</h2></div>{areas_chips(ctx)}</div></section>
{cta_band(ctx)}
"""
    graph = [service_schema(path, s["name"], s["meta"]), faq_schema(path, s["faqs"]),
             {"@type": "ItemList", "@id": url(path) + "#services", "itemListElement": [
                 {"@type": "ListItem", "position": i + 1, "url": url(f"{s['key']}/{c['slug']}/"), "name": c["name"]} for i, c in enumerate(s["children"])]}]
    page(path, s["title"], s["meta"], body, graph, active=s["key"], trail=trail, kind="Silo hub", target=s["h1"].lower())


def build_service(s, c):
    path = f"{s['key']}/{c['slug']}/"
    trail = [("Home", ""), (s["name"], s["key"] + "/"), (c["name"], path)]

    def body(ctx):
        opts = "".join(
            f'<div class="option">{f"""<div class="card-art">{drawing(d, False)}</div>""" if d else ""}<div class="option-body"><h3>{E(n)}</h3><p>{E(t)}</p></div></div>'
            for n, t, d in c["options"])
        inc = "".join(f"<li>{IC['check']}<span>{E(i)}</span></li>" for i in c["included"])
        spec = "".join(f'<tr><th scope="row">{E(k)}</th><td>{E(v)}</td></tr>' for k, v in c["specs"])
        here = ' aria-current="page"'
        sib = "".join(f'<li><a href="{href(ctx, s["key"] + "/" + x["slug"] + "/")}"{here if x is c else ""}>{E(x["name"])}</a></li>'
                      for x in s["children"])
        cities = "".join(f'<li><a href="{href(ctx, "service-areas/" + y["slug"] + "/")}">{E(c["name"])} in {E(y["name"])}</a></li>' for y in CITIES)
        rel = "".join(svc_card(ctx, r) for r in c["related"])
        return f"""
<section class="page-hero"><div class="wrap hero-grid">
<div><span class="code">{c['code']} · {E(s['name'])}</span><h1>{E(c['h1'])}</h1><p class="lede">{E(c['lede'])}</p>{btns(ctx, c['slug'])}</div>
{sheet(c['drawing'], f"Sheet {c['code']} · {'Section' if c['drawing'] == 'post_section' else 'Elevation'}")}
</div></section>
<section class="sec"><div class="wrap svc-layout">
<div class="prose">
<h2>Overview</h2>{''.join(f'<p>{E(p)}</p>' for p in c['overview'])}
<h2>Styles and options</h2><div class="options">{opts}</div>
<h2>What's included</h2><ul class="checks two">{inc}</ul>
<h2>Specifications</h2><div class="spec-wrap"><table class="spec"><tbody>{spec}</tbody></table></div>
{factors_block(c['factors'])}
<div style="margin-top:2.4em">{faq_block(c['faqs'])}</div>
</div>
<aside class="aside" aria-label="Request an estimate">
{quick_form(ctx, s['name'] + ' — ' + c['name'], c['slug'])}
<div class="aside-list"><h3>{E(s['name'])}</h3><ul>{sib}</ul></div>
<div class="aside-list"><h3>Where we build</h3><ul>{cities}</ul></div>
</aside>
</div></section>
{photo_strip(ctx, [s['key'] + '/' + c['slug']], c['name'] + ' up close', "sec tight ph-sec")}
<section class="sec alt"><div class="wrap"><div class="sec-head"><span class="code">Related</span><h2>Often paired with</h2></div>
<div class="related">{rel}</div></div></section>
{cta_band(ctx, service=c['slug'])}
"""
    graph = [service_schema(path, c["name"], c["meta"]), faq_schema(path, c["faqs"])]
    page(path, c["title"], c["meta"], body, graph, active=s["key"], trail=trail, kind="Service", target=c["h1"].lower())


def build_services_index():
    path = "services/"
    title = "Fence, Gate & Deck Services in Plano, TX | Keystone Fence & Deck"
    meta = "Every fence, gate, deck and repair service Keystone Fence & Deck Co. offers across Plano, Collin County and North Dallas, in one place."
    trail = [("Home", ""), ("All services", path)]

    def body(ctx):
        out = []
        for s in SILOS:
            cards = "".join(svc_card(ctx, f"{s['key']}/{c['slug']}") for c in s["children"])
            out.append(f'<section class="sec tight"><div class="wrap"><div class="sec-head"><span class="code">{s["letter"]} — {E(s["nav"])}</span>'
                       f'<h2><a href="{href(ctx, s["key"] + "/")}" style="color:inherit;text-decoration:none">{E(s["name"])}</a></h2><p>{E(s["lede"])}</p></div>'
                       f'<div class="grid g3">{cards}</div></div></section>')
        return (f'<section class="page-hero"><div class="wrap"><span class="code">Catalog</span><h1>All services</h1>'
                f'<p class="lede">{sum(len(s["children"]) for s in SILOS)} services across {N_TRADES} trades. Each has its own page with options, specs and what affects the estimate.</p>{btns(ctx)}</div></section>'
                + "".join(out) + cta_band(ctx))
    page(path, title, meta, body, [], trail=trail, kind="Service index", target="fence gate deck services plano")


def build_areas():
    path = "service-areas/"
    title = "Service Areas — Plano, Frisco, McKinney & More | Keystone Fence & Deck"
    meta = "Keystone Fence & Deck Co. builds fences, gates and decks across Plano, Frisco, McKinney, Allen, Richardson, Prosper and surrounding North Dallas cities."
    trail = [("Home", ""), ("Service areas", path)]

    def body(ctx):
        cards = "".join(f'<a class="card" href="{href(ctx, "service-areas/" + c["slug"] + "/")}"><div class="card-body">'
                        f'<span class="card-code">{E(c["county"])}</span><h3>{E(c["name"])}, TX</h3><p>{E(c["lede"])}</p>'
                        f'<span class="card-more">Fencing in {E(c["name"])} {IC["arrow"]}</span></div></a>' for c in CITIES)
        return f"""
<section class="page-hero"><div class="wrap hero-grid">
<div><span class="code">Service areas</span><h1>Where we build</h1><p class="lede">Based in Plano and working across Collin County and North Dallas. Each city page covers what's different about building there.</p>{btns(ctx)}</div>
{gmap(ctx, "Collin County, Texas", 10, "Collin County, TX", "Based in Plano · serving Collin County & North Dallas")}
</div></section>
<section class="sec"><div class="wrap"><div class="grid g3">{cards}</div>
<div style="margin-top:36px">{areas_chips(ctx)}</div></div></section>
{cta_band(ctx)}
"""
    page(path, title, meta, body, [], active="areas", trail=trail, kind="Area hub", target="fence contractor collin county")


def build_city(c):
    path = f"service-areas/{c['slug']}/"
    trail = [("Home", ""), ("Service areas", "service-areas/"), (c["name"], path)]

    def body(ctx):
        notes = "".join(f"<div>{IC['locate']}<h3>{E(t)}</h3><p>{E(d)}</p></div>" for t, d in c["notes"])
        feat = "".join(svc_card(ctx, p, sub=f"{SVC[p][1]['card']} Serving {c['name']}.") for p in c["featured"])
        hoods = "".join(f"<li><span>{E(n)}</span></li>" for n in c["neighborhoods"])
        near = "".join(f'<li><a href="{href(ctx, "service-areas/" + n + "/")}">{IC["locate"]}{E(CITY[n]["name"])}</a></li>' for n in c["nearby"])
        hubs = "".join(f'<li><a href="{href(ctx, s["key"] + "/")}">{E(s["name"])} in {E(c["name"])}</a></li>' for s in SILOS)
        return f"""
<section class="page-hero"><div class="wrap hero-grid">
<div><span class="code">Service area · {E(c['county'])}</span><h1>Fence &amp; Deck Contractor in {E(c['name'])}, TX</h1><p class="lede">{E(c['lede'])}</p>{btns(ctx)}</div>
{gmap(ctx, c['name'] + ", TX", c.get('zoom', 12), c['name'] + ", TX", c['county'], current=c['slug'])}
</div></section>
<section class="sec"><div class="wrap">
<div class="measure prose" style="margin-bottom:36px">{''.join(f'<p>{E(p)}</p>' for p in c['intro'])}</div>
<div class="sec-head"><span class="code">Local considerations</span><h2>Building in {E(c['name'])}</h2></div>
<div class="commit">{notes}</div>
</div></section>
<section class="sec alt"><div class="wrap">
<div class="sec-head"><span class="code">Popular in {E(c['name'])}</span><h2>What we build most in {E(c['name'])}</h2></div>
<div class="grid g3">{feat}</div>
<div class="aside-list" style="margin-top:22px"><h3>All trades in {E(c['name'])}</h3><ul style="grid-template-columns:repeat(auto-fit,minmax(220px,1fr))">{hubs}</ul></div>
</div></section>
<section class="sec"><div class="wrap split" style="align-items:start">
<div><span class="code">Neighborhoods</span><h2 style="margin:14px 0 16px">Neighborhoods we work in</h2><ul class="chips">{hoods}</ul></div>
<div><span class="code">Nearby</span><h2 style="margin:14px 0 16px">Nearby cities</h2><ul class="chips">{near}</ul>
<p style="margin:16px 0 0"><a href="{href(ctx, 'service-areas/')}"><strong>All service areas</strong></a></p></div>
</div></section>
<section class="sec sheet rule-top"><div class="wrap measure">{faq_block(c['faqs'], f"Questions from {c['name']} homeowners")}</div></section>
{cta_band(ctx, title=f"Planning a project in {c['name']}?")}
"""
    graph = [faq_schema(path, c["faqs"]),
             {"@type": "Service", "@id": url(path) + "#service", "name": f"Fence and deck contractor in {c['name']}, TX",
              "provider": {"@id": BASE + "/#business"}, "areaServed": {"@type": "City", "name": f"{c['name']}, TX"}, "url": url(path)}]
    page(path, c["title"], c["meta"], body, graph, active="areas", trail=trail, kind="City", target=f"fence company {c['name'].lower()} tx")


def build_projects():
    path = "projects/"
    title = "Fence, Gate & Deck Projects | Keystone Fence & Deck Co."
    meta = "Typical fence, gate, deck and repair project scopes across Plano and North Dallas, with the specs that shape each estimate."
    trail = [("Home", ""), ("Projects", path)]

    def body(ctx):
        filt = '<button type="button" data-filter="all" aria-pressed="true">All</button>' + "".join(
            f'<button type="button" data-filter="{s["key"]}" aria-pressed="false">{E(s["nav"])}</button>' for s in SILOS)
        cards = "".join(project_card(ctx, p) for p in PROJECTS)
        sample = ('<p class="note"><strong>About these projects</strong>These are typical scopes for the work we do — what each kind of job involves and the '
                  'specs that drive the estimate. They are representative, not records of specific jobs.</p>') if CONFIG["fictional"] else ""
        return f"""
<section class="page-hero"><div class="wrap"><span class="code">Projects</span><h1>What our jobs look like</h1>
<p class="lede">From a single walk gate to a 1,600-foot pasture fence: the scope, the specs and how long each kind of job typically takes.</p></div></section>
<section class="sec"><div class="wrap">{sample}
<div class="filters" role="group" aria-label="Filter projects by trade">{filt}</div><p class="sr-only js-filter-count" aria-live="polite"></p>
<div class="proj">{cards}</div></div></section>
{cta_band(ctx, title="Have a project like one of these?")}
"""
    page(path, title, meta, body, [], active="projects", trail=trail, kind="Projects", target="fence projects plano")


def build_about():
    path = "about/"
    trail = [("Home", ""), ("About", path)]

    def body(ctx):
        creds = "".join(f"<div>{IC['warranty']}<h3>{E(t)}</h3><p>{E(d)}</p></div>" for t, d in ABOUT["creds"])
        com = "".join(f"<div>{IC[i]}<h3>{E(t)}</h3><p>{E(d)}</p></div>" for i, t, d in COMMITMENTS)
        aud = "".join(f"<div><h3>{E(t)}</h3><p>{E(d)}</p></div>" for t, d in AUDIENCES)
        return f"""
<section class="page-hero"><div class="wrap hero-grid">
<div><span class="code">About</span><h1>{E(ABOUT['h1'])}</h1><p class="lede">{E(ABOUT['lede'])}</p>{btns(ctx)}</div>
{sheet("pipe", "Sheet F-04 · The H-brace in our mark")}
</div></section>
<section class="sec"><div class="wrap measure prose">{''.join(f'<p>{E(p)}</p>' for p in ABOUT['story'])}
<p>Look closely at our mark: a post with two diagonal braces. It's the H-brace from a ranch-fence corner — the part that keeps a long run tight for decades — and it happens to make a K.</p></div></section>
<section class="sec alt"><div class="wrap"><div class="sec-head"><span class="code">Credentials</span><h2>The basics, covered</h2></div><div class="commit">{creds}</div></div></section>
<section class="sec"><div class="wrap"><div class="sec-head"><span class="code">Our standards</span><h2>What you can hold us to</h2></div><div class="commit">{com}</div></div></section>
<section class="sec sheet rule-top"><div class="wrap"><div class="sec-head"><span class="code">Who we build for</span><h2>Residential and commercial</h2></div><div class="aud">{aud}</div></div></section>
<section class="sec tight"><div class="wrap"><div class="sec-head"><span class="code">Service areas</span><h2>Where we work</h2></div>{areas_chips(ctx)}</div></section>
{cta_band(ctx)}
"""
    page(path, ABOUT["title"], ABOUT["meta"], body, [{"@type": "AboutPage", "@id": url(path) + "#about", "url": url(path), "about": {"@id": BASE + "/#business"}}],
         active="about", trail=trail, kind="About", target="about keystone fence")


def build_estimate():
    path = "free-estimate/"
    title = "Request a Free Fence or Deck Estimate | Keystone Fence & Deck"
    meta = "Request a free on-site estimate for fencing, gates, decks or repairs in Plano and North Dallas. Add photos, and get an itemized written estimate."
    trail = [("Home", ""), ("Free estimate", path)]

    def body(ctx):
        steps = "".join(f"<li><h3>{E(t)}</h3><p>{E(d)}</p></li>" for t, d in STEPS)
        return f"""
<section class="page-hero"><div class="wrap"><span class="code">Free · on site · in writing</span><h1>Request a free estimate</h1>
<p class="lede">Two short steps. Add photos if you have them — they help us arrive prepared. We'll contact you within one business day to book a visit.</p></div></section>
<section class="sec"><div class="wrap est-layout">
<div class="form-shell" data-form-shell>
<form class="form js-lead" data-form="estimate" novalidate>
{hidden_inputs("estimate", "New estimate request — Keystone website")}
<div class="progress" aria-hidden="true"><div class="on">1 · You and the project</div><div>2 · Details and photos</div></div>
<div class="step-panel">
<div class="row2">{fld("e-name", "name", "Full name", auto="name", err="Please enter your name.")}{fld("e-phone", "phone", "Phone", kind="tel", auto="tel", err="Enter a phone number with area code.", extra=' data-phone inputmode="tel"')}</div>
{fld("e-email", "email", "Email", kind="email", auto="email", err="Enter a valid email address.")}
{choice("contact_method", "Best way to reach you", ["Call", "Text", "Email"], err="Choose how you'd like us to contact you.")}
<div class="row2">{fld("e-addr", "address", "Project address", auto="street-address", err="Enter the project address.")}{fld("e-zip", "city_zip", "City or ZIP", auto="postal-code", err="Enter the city or ZIP code.")}</div>
{choice("customer_type", "I am a", ["Homeowner", "HOA / Property manager", "Builder / GC", "Commercial owner", "Realtor / Investor", "Other"], err="Choose the closest match.")}
{service_select("e-service")}
<div class="form-actions"><span class="help">Step 1 of 2</span><button class="btn btn-primary" type="button" data-next>Continue to details {IC['arrow']}</button></div>
</div>
<div class="step-panel" hidden>
{fld("e-desc", "description", "Tell us about the project", area=True, rows=6, err="A sentence or two helps us prepare.", help_="Roughly how many feet? Height? Material you're leaning toward? Gates? Anything about slope, access or your HOA?")}
<div class="row2">
<div class="field"><label for="e-time">Timeline <span class="opt">(optional)</span></label><select class="select" id="e-time" name="timeline"><option value="">Choose…</option><option>As soon as possible</option><option>Within a month</option><option>1–3 months</option><option>Just planning</option></select></div>
{fld("e-best", "best_time", "Best time to reach you", req=False, help_="e.g. weekday mornings")}
</div>
{choice("hoa", "Is the property in an HOA?", ["Yes", "No", "Not sure"], req=False)}
<div class="field"><span class="legend">Photos <span class="opt">(optional)</span></span>
<div class="drop">{IC['camera']}<strong>Add photos of the area</strong><span class="js-photo-count">Up to 8 photos</span>
<input type="file" name="photos" accept="image/*" multiple aria-label="Add photos of the project area"></div>
<div class="thumbs" aria-live="polite"></div>
<span class="help">Wide shots of the fence line, the gate area or the old fence work best. Large phone photos are resized before sending.</span></div>
<p class="consent">By sending this form you agree we may contact you about your project using your preferred method. We never sell your information. <a href="{href(ctx, 'privacy/')}">Privacy policy</a>.</p>
<div class="form-status" role="alert"></div>
<div class="form-actions"><button class="btn btn-line" type="button" data-back>← Back</button><button class="btn btn-primary" type="submit">Send my estimate request {IC['arrow']}</button></div>
</div>
</form>
{success_block("Thanks — we've got your request.", ["We'll contact you within one business day to book a time to walk your property.", "On site, we measure and check grade, drainage, utilities and HOA rules.", "You get an itemized written estimate by email — no pressure, no expiring price."])}
</div>
<aside class="aside" aria-label="What happens next">
<div class="quote-card"><h2>Rather talk?</h2><p>Call and we'll take the details by phone.</p><a class="btn btn-dark btn-block" href="{TEL}" data-loc="estimate-aside">{IC['phone']} {E(CONFIG['phone'])}</a>
<ul class="help" style="list-style:none;padding:0;margin:14px 0 0">{''.join(f'<li>{E(d)}: {E(h)}</li>' for d, h in CONFIG['hours'])}</ul></div>
<div class="aside-list"><h3>What happens next</h3><ol class="steps" style="grid-template-columns:1fr;border:0;background:none;gap:0">{steps}</ol></div>
</aside>
</div></section>
"""
    page(path, title, meta, body, [{"@type": "ContactPage", "@id": url(path) + "#contact", "url": url(path)}],
         trail=trail, estimate_page=True, kind="Estimate form", target="free fence estimate plano")


def build_contact():
    path = "contact/"
    title = "Contact Keystone Fence & Deck Co. | Plano, TX"
    meta = "Call, email or message Keystone Fence & Deck Co. in Plano, TX. Hours, service area and a quick contact form."
    trail = [("Home", ""), ("Contact", path)]

    def body(ctx):
        hours = "".join(f'<tr><th scope="row">{E(d)}</th><td>{E(h)}</td></tr>' for d, h in CONFIG["hours"])
        return f"""
<section class="page-hero"><div class="wrap"><span class="code">Contact</span><h1>Talk to us</h1>
<p class="lede">For a project estimate, the <a href="{href(ctx, 'free-estimate/')}">estimate form</a> is fastest. For anything else, call, email or send a message.</p></div></section>
<section class="sec"><div class="wrap split" style="align-items:start">
<div>
<h2 style="margin-bottom:18px">Reach us</h2>
<table class="spec"><tbody>
<tr><th scope="row">Phone</th><td><a class="tel" href="{TEL}" data-loc="contact">{E(CONFIG['phone'])}</a></td></tr>
<tr><th scope="row">Email</th><td><a href="mailto:{A(CONFIG['email'])}">{mail_text(CONFIG['email'])}</a></td></tr>
<tr><th scope="row">Based in</th><td>Plano, Texas — serving Collin County and North Dallas</td></tr>
{hours}
</tbody></table>
<div style="margin-top:24px">{areas_chips(ctx)}</div>
<div style="margin-top:32px">{gmap(ctx, "Collin County, Texas", 10, "Collin County, TX", "No walk-in office · we come to you")}</div>
</div>
<div class="form-shell" data-form-shell>
<h2 style="font-size:2rem;margin-bottom:6px">Send a message</h2>
<form class="form js-lead" data-form="contact" novalidate>
{hidden_inputs("contact", "Website message — Keystone")}
{fld("c-name", "name", "Name", auto="name", err="Please enter your name.")}
<div class="row2">{fld("c-phone", "phone", "Phone", kind="tel", auto="tel", err="Enter a phone number with area code.", extra=' data-phone inputmode="tel"')}{fld("c-email", "email", "Email", kind="email", auto="email", err="Enter a valid email address.")}</div>
{fld("c-msg", "message", "Message", area=True, rows=5, err="Please add a short message.")}
<div class="form-status" role="alert"></div>
<button class="btn btn-primary" type="submit">Send message {IC['arrow']}</button>
</form>
{success_block("Message received.", ["We reply to messages within one business day.", "For a project, we'll suggest booking an on-site estimate."])}
</div>
</div></section>
"""
    page(path, title, meta, body, [{"@type": "ContactPage", "@id": url(path) + "#contact", "url": url(path)}],
         trail=trail, kind="Contact", target="contact fence company plano")


def build_privacy():
    path = "privacy/"
    title = "Privacy Policy | Keystone Fence & Deck Co."
    meta = "How Keystone Fence & Deck Co. collects, uses and protects the information you send through this website."
    trail = [("Home", ""), ("Privacy", path)]
    secs = [
        ("What we collect", "When you request an estimate or send a message, we collect what you enter: your name, phone, email, project address, the service you need, your project description and any photos you attach. If analytics is enabled, we also collect anonymous usage data such as pages visited and the device type."),
        ("How we use it", "We use your details to contact you about your project, schedule site visits, prepare estimates and keep records of work. We don't sell or rent your information, and we don't use it for unrelated marketing."),
        ("Who processes it", "Form submissions are delivered to us by email through our form provider. Analytics, when enabled, is provided by Google Analytics. These providers process data on our behalf."),
        ("Maps", "Some pages show an embedded Google Map. When it loads, Google receives your IP address and may set cookies, under Google's own privacy policy."),
        ("How long we keep it", "We keep estimate requests and job records for as long as needed to serve you and meet our business and legal obligations."),
        ("Your choices", f"You can ask us to access, correct or delete the information we hold about you by emailing {CONFIG['email']} or calling {CONFIG['phone']}."),
        ("Changes", "We may update this policy as the site changes. The date below shows when it was last revised."),
    ]

    def body(ctx):
        return (f'<section class="page-hero"><div class="wrap"><span class="code">Legal</span><h1>Privacy policy</h1></div></section>'
                f'<section class="sec"><div class="wrap measure prose">'
                + "".join(f"<h2>{E(t)}</h2><p>{E(d)}</p>" for t, d in secs)
                + f'<p class="help">Last updated {TODAY}.</p></div></section>')
    page(path, title, meta, body, [], trail=trail, kind="Legal")


def build_notes():
    path = "build-notes/"
    title = "How This Site Is Built | Keystone Fence & Deck Co."
    meta = "The architecture behind this contractor website: service silos, URL structure, internal linking, schema, conversion system and how it maps to WordPress."
    trail = [("Home", ""), ("How this site is built", path)]

    def body(ctx):
        silos = "".join(
            f'<div class="tree-silo"><a href="{href(ctx, s["key"] + "/")}">/{s["key"]}/</a><ul>'
            + "".join(f'<li><a href="{href(ctx, s["key"] + "/" + c["slug"] + "/")}">{c["slug"]}/</a></li>' for c in s["children"])
            + "</ul></div>" for s in SILOS)
        areas = " · ".join(f'<a href="{href(ctx, "service-areas/" + c["slug"] + "/")}">/{c["slug"]}/</a>' for c in CITIES)
        rows = "".join(f'<tr><td>/{E(p.replace("index.html", ""))}</td><td>{E(k)}</td><td>{E(t)}</td></tr>'
                       for p, _, k, t in PAGES if k not in ("Legal", "404"))
        tmpl = [
            ("Home", "Brand + head term (fence company Plano)", "Hero film, silo cards, process, standards, service-area map, FAQ"),
            ("Silo hub", "The trade's head term (fence installation Plano)", "Child grid, comparison guide, estimate factors, FAQ, ItemList schema"),
            ("Service", "One specific service + city", "Elevation drawing, options, inclusions, spec table, factors, FAQ, sticky quote form, related services"),
            ("City", "Service + city intent (fence company Frisco TX)", "Local considerations, featured services with local anchors, neighborhoods, nearby cities"),
            ("Estimate", "Conversion, not ranking", "Two-step form, service prefill, photo upload, next-step reassurance"),
        ]
        trows = "".join(f"<tr><td>{E(a)}</td><td>{E(b)}</td><td>{E(c)}</td></tr>" for a, b, c in tmpl)
        rules = [
            "Every service page links up to its hub (breadcrumb and sidebar) and the hub links down to every child.",
            "Each service links sideways to two or three related services — one or more in another silo, where jobs genuinely pair (privacy fence → staining, walk gates).",
            "Every service page links to every city page with descriptive anchors (\"Wood Privacy Fence in Frisco\"); every city page links back to its top services and all four hubs.",
            "The footer carries hubs, cities and six popular services only — not every URL — so link weight stays concentrated.",
            "Every estimate CTA on a service page passes ?service= so the form arrives pre-filled.",
        ]
        schema = [
            ("All pages", "HomeAndConstructionBusiness (service-area business: city and region, no street address), WebPage, BreadcrumbList"),
            ("Home", "WebSite, OfferCatalog of every service, FAQPage"),
            ("Silo hub", "Service, ItemList of child services, FAQPage"),
            ("Service", "Service with provider and areaServed, FAQPage"),
            ("City", "Service scoped to the city, FAQPage"),
        ]
        srows = "".join(f"<tr><td>{E(a)}</td><td>{E(b)}</td></tr>" for a, b in schema)
        return f"""
<section class="page-hero"><div class="wrap"><span class="code">Build notes</span><h1>How this site is built</h1>
<p class="lede">A working website for a multi-service local contractor, built so each trade can rank on its own. {E(CONFIG['name'])} is fictional; the architecture, templates and lead system are real.</p></div></section>

<section class="sec"><div class="wrap">
<div class="sec-head"><span class="code">01 · Structure</span><h2>{N_TRADES.capitalize()} silos, one site</h2>
<p class="lede">Each trade is a self-contained topic cluster: a hub page for the head term and child pages for specific services. Internal links run down from the hub, sideways between related services and up through breadcrumbs — so each cluster builds its own relevance instead of competing with the others.</p></div>
<div class="tree"><div class="tree-root">/ (home)</div><div class="tree-silos">{silos}</div>
<div class="tree-areas"><strong>Location layer:</strong> <a href="{href(ctx, 'service-areas/')}">/service-areas/</a> → {areas}</div></div>
<p class="help" style="margin-top:14px">The same pattern carries any multi-trade contractor: swap {E(" / ".join(x["nav"] for x in SILOS))} for, say, Demolition / Land Clearing / Tree Services / Site Cleanup, and the templates, linking rules and schema carry over unchanged. Adding a trade is one data entry — the Land Clearing silo was added that way, and every menu, footer, sitemap and city page picked it up automatically.</p>
</div></section>

<section class="sec alt"><div class="wrap">
<div class="sec-head"><span class="code">02 · Templates</span><h2>Five page types</h2></div>
<div class="spec-wrap"><table class="compare"><thead><tr><th scope="col">Template</th><th scope="col">Built to rank for</th><th scope="col">What's on it</th></tr></thead><tbody>{trows}</tbody></table></div>
</div></section>

<section class="sec"><div class="wrap measure prose">
<span class="code">03 · Internal linking</span><h2 style="margin-top:14px">Linking rules</h2>
<ul class="checks">{''.join(f"<li>{IC['check']}<span>{E(r)}</span></li>" for r in rules)}</ul>
<span class="code" style="margin-top:28px">04 · Structured data</span><h2 style="margin-top:14px">Schema by page type</h2>
<div class="spec-wrap"><table class="compare"><thead><tr><th scope="col">Page</th><th scope="col">JSON-LD</th></tr></thead><tbody>{srows}</tbody></table></div>
<p class="help">FAQPage markup stays for machine readability and AI answer engines, but the build doesn't count on FAQ rich results — Google limited those to government and health sites in 2023.</p>
<span class="code" style="margin-top:28px">05 · On-page</span><h2 style="margin-top:14px">Implemented on every page</h2>
<ul class="checks two">{''.join(f"<li>{IC['check']}<span>{E(x)}</span></li>" for x in ["Unique title, 70 characters or fewer", "Unique meta description, 165 or fewer", "One H1, logical H2/H3 below it", "Canonical URL", "Breadcrumbs, visible and in schema", "Open Graph and social image", "XML sitemap and robots.txt", "Indexing switch in one config value"])}</ul>
<span class="code" style="margin-top:28px">06 · Conversion</span><h2 style="margin-top:14px">Lead system</h2>
<ul class="checks">{''.join(f"<li>{IC['check']}<span>{E(x)}</span></li>" for x in ["Free Estimate and click-to-call in the header, plus a sticky call/estimate bar on phones", "A quote card on every service page, pre-labelled with that service", "Two-step estimate form: contact first, details and photos second", "Phone photos resized in the browser before upload, so large images don't fail", "If the form provider refuses photos, the lead is still delivered without them", "Honeypot spam trap; GA4 generate_lead and click_to_call events when analytics is on"])}</ul>
<span class="code" style="margin-top:28px">07 · Performance</span><h2 style="margin-top:14px">Light by design</h2>
<p>Every illustration is inline SVG drawn in code, crisp on any screen. The hero film is a 16-second, 660 KB H.264 loop rendered from the same drawing code: it shows its poster first, stays still for reduced-motion and Save-Data visitors, and pauses off-screen. Maps load lazily. Photos dropped into the photos folder are resized to 800 and 1600 px WebP and JPEG with all metadata, GPS included, stripped. One stylesheet, one deferred script, self-hosted fonts.</p>
<span class="code" style="margin-top:28px">08 · WordPress</span><h2 style="margin-top:14px">How it maps to WordPress</h2>
<p>The URL tree becomes the page hierarchy one to one (parent and child pages with identical slugs). Each template becomes a block pattern; titles, metas and schema move to Rank Math or Yoast; the estimate form becomes Gravity Forms or WPForms with file upload; GA4 and Search Console connect through Site Kit. Adding a city is one new page from the city template.</p>
</div></section>

<section class="sec alt"><div class="wrap">
<div class="sec-head"><span class="code">09 · URL map</span><h2>Every page and its target</h2></div>
<div class="spec-wrap"><table class="url-table"><thead><tr><th scope="col">URL</th><th scope="col">Type</th><th scope="col">Primary target</th></tr></thead><tbody>{rows}</tbody></table></div>
</div></section>
"""
    page(path, title, meta, body, [], trail=trail, kind="Build notes")


def build_404():
    ctx = Ctx("", absolute=True)
    title = "Page not found | Keystone Fence & Deck Co."
    meta = "That page doesn't exist."
    body = f"""<main id="main"><section class="sec"><div class="wrap split">
<div><span class="code">404</span><h1 style="margin:14px 0 18px">This line doesn't go anywhere.</h1>
<p class="lede">The page you were after has moved or never existed. Try one of these instead.</p>
<div class="btn-row"><a class="btn btn-primary" href="/free-estimate/">Request a free estimate {IC['arrow']}</a><a class="btn btn-line" href="/">Home</a></div>
<ul class="chips" style="margin-top:22px">{''.join(f'<li><a href="/{s["key"]}/">{E(s["name"])}</a></li>' for s in SILOS)}</ul></div>
{sheet("removal", "Sheet R-05 · Removed")}
</div></section></main>"""
    out = head(ctx, "404.html", title, meta, [business()]).replace('<link rel="canonical"', '<meta name="robots" content="noindex"><link rel="canonical"', 1)
    out += header(ctx, None) + body + footer(ctx)
    write("404.html", out, title, "404")


# ═══════════════════════════════════════════════════════════ assets
def favicon():
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40"><rect width="40" height="40" rx="6" fill="#F1F1EC"/>'
            '<rect x="2.5" y="2.5" width="35" height="35" fill="none" stroke="#16191B" stroke-width="2"/>'
            '<rect x="11" y="7" width="5.5" height="26" fill="#16191B"/>'
            '<path d="M16.5 20 L29 7.5 L32.5 7.5 L32.5 10 L20.6 21.6 Z" fill="#A0552A"/>'
            '<path d="M18.4 18.6 L32.5 30 L32.5 33 L29 33 L16.5 22.4 Z" fill="#A0552A"/></svg>')


def sitemap():
    urls = "".join(f"<url><loc>{E(url(p))}</loc><lastmod>{TODAY}</lastmod></url>"
                   for p, _, k, _ in PAGES if k not in ("404",))
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n'


def robots():
    note = "" if CONFIG["index"] else "# Crawling is allowed so search engines can read each page's noindex tag.\n"
    return f"{note}User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n"


def vercel():
    cfg = {"trailingSlash": True, "headers": [
        {"source": "/assets/(.*)", "headers": [{"key": "Cache-Control", "value": "public, max-age=604800"}]}]}
    if not CONFIG["index"]:
        cfg["headers"].append({"source": "/(.*)", "headers": [{"key": "X-Robots-Tag", "value": "noindex, nofollow"}]})
    return json.dumps(cfg, indent=2) + "\n"


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    shutil.copytree(os.path.join(ROOT, "static", "assets"), os.path.join(OUT, "assets"))
    build_home()
    build_services_index()
    for s in SILOS:
        build_hub(s)
        for c in s["children"]:
            build_service(s, c)
    build_areas()
    for c in CITIES:
        build_city(c)
    build_projects()
    build_about()
    build_estimate()
    build_contact()
    build_privacy()
    build_notes()                     # last: it lists every page
    if not PREVIEW:
        build_404()
        for name, text in (("sitemap.xml", sitemap()), ("robots.txt", robots()), ("vercel.json", vercel())):
            with open(os.path.join(OUT, name), "w") as f:
                f.write(text)
    with open(os.path.join(OUT, "favicon.svg"), "w") as f:
        f.write(favicon())
    print(f"{'preview' if PREVIEW else 'production'} build: {len(PAGES)} pages -> {OUT}")


if __name__ == "__main__":
    main()
