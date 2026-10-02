import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shoot import shoot
build = sys.argv[1] if len(sys.argv) > 1 else "dist"
def at(sel, wait=1500):
    def f(pg):
        pg.wait_for_timeout(wait)
        pg.evaluate(f"document.querySelector('{sel}').scrollIntoView({{block:'center'}})")
        pg.wait_for_timeout(700)
    return f
def hero(pg): pg.wait_for_timeout(2600)
jobs = [
    ("", 1280, 800, f"m_{build}_home_1280.png", False, hero),
    ("", 390, 844, f"m_{build}_home_390.png", False, lambda pg: (pg.wait_for_timeout(2600), pg.evaluate("window.scrollTo(0, document.querySelector('.vid-frame').getBoundingClientRect().top + scrollY - 300)"), pg.wait_for_timeout(500))),
    ("", 1280, 800, f"m_{build}_homemap_1280.png", False, at(".map-frame")),
    ("", 390, 844, f"m_{build}_homemap_390.png", False, at(".map-frame")),
    ("service-areas/frisco/" + ("index.html" if build == "preview" else ""), 390, 844, f"m_{build}_frisco_390.png", False, at(".map-frame")),
    ("contact/" + ("index.html" if build == "preview" else ""), 390, 844, f"m_{build}_contact_390.png", False, at(".map-frame")),
]
shoot(jobs, build=build)
