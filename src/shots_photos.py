import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shoot import shoot
def at(sel):
    def f(pg):
        pg.evaluate(f"document.querySelector('{sel}').scrollIntoView({{block:'center'}})"); pg.wait_for_timeout(900)
    return f
shoot([("", 1280, 800, "p_home_1280.png", False, at(".ph-grid")),
       ("", 390, 844, "p_home_390.png", False, at(".ph-grid")),
       ("fencing/", 390, 844, "p_fencing_390.png", False, at(".ph-grid")),
       ("projects/", 1280, 800, "p_projects_1280.png", False, at(".has-photo"))])
