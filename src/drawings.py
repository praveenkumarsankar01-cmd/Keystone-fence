"""
Keystone Fence & Deck Co. — elevation drawing library.

Every illustration on the site is an architectural elevation or section,
drawn parametrically so the same function serves a full-size hero sheet
(with dimensions and a title block) and a small card thumbnail (lines
only). Strokes use non-scaling-stroke so line weight stays crisp at any
size, and colours come from CSS custom properties on the page.

Units: 16 viewBox units = 1 foot.
"""
import math

S = 16          # units per foot
_UID = [0]


def _plain(s):
    return (s.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
             .replace("&quot;", '"'))


def ft(v):
    return v * S


def fmt_ft(feet):
    """6.0 -> 6'-0\"   4.5 -> 4'-6\""""
    f = int(feet)
    i = round((feet - f) * 12)
    if i == 12:
        f, i = f + 1, 0
    return f"{f}'-{i}\""


class D:
    def __init__(self, w, h, title, labels=True):
        _UID[0] += 1
        self.id = f"k{_UID[0]}"
        self.w, self.h, self.title, self.labels = w, h, title, labels
        self.parts, self.defs = [], []

    # primitives -------------------------------------------------------
    def add(self, s):
        self.parts.append(s)

    def line(self, x1, y1, x2, y2, cls="k-ln"):
        self.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" class="{cls}"/>')

    def rect(self, x, y, w, h, cls="k-ln", rx=0):
        r = f' rx="{rx}"' if rx else ""
        self.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{max(w,0):.1f}" height="{max(h,0):.1f}"{r} class="{cls}"/>')

    def path(self, d, cls="k-ln"):
        self.add(f'<path d="{d}" class="{cls}"/>')

    def circle(self, cx, cy, r, cls="k-ln"):
        self.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" class="{cls}"/>')

    def text(self, x, y, s, cls="k-lb", anchor="start", rot=None):
        if not self.labels:
            return
        t = f' transform="rotate({rot} {x:.1f} {y:.1f})"' if rot is not None else ""
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" class="{cls}"{t}>{s}</text>')

    # patterns ---------------------------------------------------------
    def soil(self):
        pid = f"{self.id}-soil"
        if not any(pid in d for d in self.defs):
            self.defs.append(
                f'<pattern id="{pid}" width="9" height="9" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
                f'<line x1="0" y1="0" x2="0" y2="9" class="k-hatch"/></pattern>')
        return f"url(#{pid})"

    def stipple(self):
        pid = f"{self.id}-conc"
        if not any(pid in d for d in self.defs):
            self.defs.append(
                f'<pattern id="{pid}" width="10" height="10" patternUnits="userSpaceOnUse">'
                f'<rect width="10" height="10" class="k-conc-bg"/><circle cx="2" cy="3" r=".9" class="k-dot"/><circle cx="7" cy="7" r=".7" class="k-dot"/>'
                f'<circle cx="8" cy="1.5" r=".5" class="k-dot"/></pattern>')
        return f"url(#{pid})"

    def gravel(self):
        pid = f"{self.id}-grav"
        if not any(pid in d for d in self.defs):
            self.defs.append(
                f'<pattern id="{pid}" width="12" height="8" patternUnits="userSpaceOnUse">'
                f'<rect width="12" height="8" class="k-grav-bg"/><circle cx="3" cy="3" r="1.8" class="k-pebble"/><circle cx="9" cy="5.5" r="1.4" class="k-pebble"/></pattern>')
        return f"url(#{pid})"

    def mesh(self):
        pid = f"{self.id}-mesh"
        if not any(pid in d for d in self.defs):
            self.defs.append(
                f'<pattern id="{pid}" width="9" height="9" patternUnits="userSpaceOnUse">'
                f'<path d="M0 4.5 L4.5 0 L9 4.5 L4.5 9 Z" class="k-wire"/></pattern>')
        return f"url(#{pid})"

    def brick(self):
        pid = f"{self.id}-brk"
        if not any(pid in d for d in self.defs):
            self.defs.append(
                f'<pattern id="{pid}" width="16" height="8" patternUnits="userSpaceOnUse">'
                f'<rect width="16" height="8" class="k-brick-bg"/><path d="M0 0H16M0 4H16M4 0V4M12 4V8" class="k-mortar"/></pattern>')
        return f"url(#{pid})"

    # architectural dimensions ----------------------------------------
    def _tick(self, x, y):
        self.line(x - 3, y + 3, x + 3, y - 3, "k-dm")

    def dim_h(self, x1, x2, y, label, ext_from=None):
        if not self.labels:
            return
        if ext_from is not None:
            self.line(x1, ext_from, x1, y + 4, "k-ext")
            self.line(x2, ext_from, x2, y + 4, "k-ext")
        self.line(x1 - 4, y, x2 + 4, y, "k-dm")
        self._tick(x1, y)
        self._tick(x2, y)
        mx = (x1 + x2) / 2
        tw = len(label) * 6.2 + 8
        self.rect(mx - tw / 2, y - 6.5, tw, 13, "k-knock")
        self.text(mx, y + 3.4, label, "k-dt", "middle")

    def dim_v(self, y1, y2, x, label, ext_from=None):
        if not self.labels:
            return
        if ext_from is not None:
            self.line(ext_from, y1, x - 4, y1, "k-ext")
            self.line(ext_from, y2, x - 4, y2, "k-ext")
        self.line(x, y1 - 4, x, y2 + 4, "k-dm")
        self._tick(x, y1)
        self._tick(x, y2)
        my = (y1 + y2) / 2
        tw = len(label) * 6.2 + 8
        self.rect(x - 6.5, my - tw / 2, 13, tw, "k-knock")
        self.text(x + 3.4, my, label, "k-dt", "middle", rot=-90)

    def callout(self, x, y, tx, ty, label, anchor="start"):
        """Leader line from a point on the drawing to a note."""
        if not self.labels:
            return
        mark = len(self.parts)
        self.circle(x, y, 1.8, "k-pin")
        self.line(x, y, tx, ty, "k-lead")
        self._note_body(tx + (4 if anchor == "start" else -4), ty, label, anchor)
        self._group(mark, "co")

    def note(self, x, y, label, anchor="start"):
        if not self.labels:
            return
        mark = len(self.parts)
        self._note_body(x, y, label, anchor)
        self._group(mark, "co")

    def _note_body(self, x, y, label, anchor):
        w = len(_plain(label)) * 5.45 + 6
        bx = x - 3 if anchor == "start" else (x - w + 3 if anchor == "end" else x - w / 2)
        self.rect(bx, y - 6, w, 12, "k-knock")
        self.text(x, y + 3.2, label, "k-note", anchor)

    def _group(self, mark, cls):
        inner = "".join(self.parts[mark:])
        del self.parts[mark:]
        self.parts.append(f'<g class="{cls}">{inner}</g>')

    def ground(self, x1, x2, gy, depth=14):
        self.add(f'<rect x="{x1:.1f}" y="{gy:.1f}" width="{x2-x1:.1f}" height="{depth}" fill="{self.soil()}" class="k-soil"/>')
        self.line(x1, gy, x2, gy, "k-grade")

    def title_block(self, sheet, name, scale="1/2&quot; = 1'-0&quot;"):
        if not self.labels:
            return
        mark = len(self.parts)
        bw, bh = 196, 46
        x, y = self.w - bw - 10, self.h - bh - 10
        self.rect(x, y, bw, bh, "k-tb")
        self.line(x, y + 16, x + bw, y + 16, "k-th")
        self.line(x + 54, y + 16, x + 54, y + bh, "k-th")
        self.text(x + 8, y + 11.5, "KEYSTONE FENCE &amp; DECK CO.", "k-tbh")
        self.text(x + 8, y + 29, "SHEET", "k-tbl")
        self.text(x + 8, y + 40, sheet, "k-tbv")
        self.text(x + 62, y + 29, name, "k-tbv")
        self.text(x + 62, y + 40, "SCALE " + scale, "k-tbl")
        self._group(mark, "tb")

    def svg(self, cls=""):
        defs = f"<defs>{''.join(self.defs)}</defs>" if self.defs else ""
        return (f'<svg class="drawing {cls}" viewBox="0 0 {self.w} {self.h}" role="img" '
                f'aria-labelledby="{self.id}-t" preserveAspectRatio="xMidYMid meet">'
                f'<title id="{self.id}-t">{self.title}</title>{defs}{"".join(self.parts)}</svg>')


# ======================================================================
#  FENCE ELEVATIONS
# ======================================================================

def _boards(d, x0, x1, top, bot, style):
    """Fill one bay with boards in the given style."""
    bw = 7.3                       # 1x6 face, 5.5"
    if style == "bob":             # board-on-board: back layer + overlapping front
        x = x0
        while x < x1:
            d.rect(x, top, min(bw, x1 - x), bot - top, "k-wd2")
            x += bw * 1.55
        x = x0 + bw * 0.78
        while x < x1:
            d.rect(x, top, min(bw, x1 - x), bot - top, "k-wd")
            x += bw * 1.55
    elif style == "shadow":        # shadowbox: alternate faces, strong tone change
        x, i = x0, 0
        while x < x1:
            d.rect(x, top, min(bw, x1 - x), bot - top, "k-wd" if i % 2 else "k-wd3")
            x += bw
            i += 1
    else:                          # side-by-side
        x = x0
        while x < x1:
            d.rect(x, top, min(bw - .6, x1 - x), bot - top, "k-wd")
            x += bw


def fence_wood(d, x0, gy, bays=3, bay=8, h=8, style="bob", post="steel", cap=True, kick=True):
    pw = 6
    top = gy - ft(h)
    cap_h, trim_h, kick_h = (4, 6, 8) if cap else (0, 0, 0)
    if not kick:
        kick_h = 0
    span = bays * ft(bay)
    for i in range(bays):
        a = x0 + i * ft(bay) + pw / 2
        b = x0 + (i + 1) * ft(bay) - pw / 2
        _boards(d, a, b, top + cap_h, gy - kick_h - 2, style)
    for i in range(bays + 1):
        px = x0 + i * ft(bay)
        d.rect(px - pw / 2, top + cap_h, pw, gy - top - cap_h, "k-st" if post == "steel" else "k-wd2")
    if kick_h:
        d.rect(x0, gy - kick_h - 2, span, kick_h, "k-wd2")
    if cap:
        d.rect(x0 - 3, top, span + 6, cap_h, "k-wd")
        d.rect(x0, top + cap_h, span, trim_h, "k-wd")
    return top


def fence_horizontal(d, x0, gy, bays=3, bay=6, h=6):
    pw = 7
    top = gy - ft(h)
    span = bays * ft(bay)
    y = top + 4
    while y < gy - 4:
        hgt = min(8.2, gy - 4 - y)
        d.rect(x0, y, span, hgt, "k-wd")
        y += 8.2 + 1.4
    for i in range(bays + 1):
        px = x0 + i * ft(bay)
        d.rect(px - pw / 2, top, pw, gy - top, "k-st")
    d.rect(x0 - 2, top, span + 4, 4, "k-st")
    return top


def fence_iron(d, x0, gy, bays=3, bay=8, h=5, spear=True, gap=6.2):
    pw = 6
    top = gy - ft(h)
    rail_t = top + (10 if spear else 4)
    rail_b = gy - 12
    span = bays * ft(bay)
    for i in range(bays):
        a = x0 + i * ft(bay) + pw / 2 + 3
        b = x0 + (i + 1) * ft(bay) - pw / 2 - 2
        x = a
        while x <= b:
            d.line(x, top + (3 if spear else 4), x, rail_b + 3, "k-picket")
            if spear and d.labels is not None:
                d.path(f"M{x-2:.1f} {top+4:.1f} L{x:.1f} {top-1.5:.1f} L{x+2:.1f} {top+4:.1f} Z", "k-finial")
            x += gap
    d.rect(x0, rail_t, span, 3, "k-st")
    d.rect(x0, rail_t + 7, span, 2.4, "k-st")
    d.rect(x0, rail_b, span, 3, "k-st")
    for i in range(bays + 1):
        px = x0 + i * ft(bay)
        d.rect(px - pw / 2, top + 2, pw, gy - top - 2, "k-st")
        d.circle(px, top, 4.2, "k-cap")
    return top


def fence_pipe(d, x0, gy, bays=3, bay=10, h=4.5, mesh=True, brace=True):
    pw = 5
    top = gy - ft(h)
    span = bays * ft(bay)
    if mesh:
        d.add(f'<rect x="{x0:.1f}" y="{top+10:.1f}" width="{span:.1f}" height="{gy-top-14:.1f}" '
              f'fill="none" class="k-grid-box"/>')
        gx = x0
        while gx <= x0 + span:
            d.line(gx, top + 10, gx, gy - 4, "k-wire")
            gx += 8
        gyy = top + 10
        while gyy <= gy - 4:
            d.line(x0, gyy, x0 + span, gyy, "k-wire")
            gyy += 7 if gyy > gy - 40 else 10
    for r in (top + 4, top + (gy - top) * .45, gy - 14):
        d.rect(x0, r - 1.8, span, 3.6, "k-pipe", rx=1.8)
    for i in range(bays + 1):
        px = x0 + i * ft(bay)
        d.rect(px - pw / 2, top - 2, pw, gy - top + 2, "k-st")
        d.path(f"M{px-3.6:.1f} {top-1:.1f} Q{px:.1f} {top-7:.1f} {px+3.6:.1f} {top-1:.1f} Z", "k-st")
    if brace:
        a, b = x0, x0 + ft(bay)
        mid = top + (gy - top) * .32
        d.rect(a, mid - 1.6, b - a, 3.2, "k-pipe", rx=1.6)
        d.line(a + 3, gy - 6, b - 3, mid + 2, "k-brace")
        d.line(a + 3, mid + 2, b - 3, gy - 6, "k-brace-2")
    return top


def fence_chainlink(d, x0, gy, bays=3, bay=10, h=6, barbed=True):
    top = gy - ft(h)
    span = bays * ft(bay)
    cid = f"{d.id}-cl"
    d.defs.append(f'<clipPath id="{cid}"><rect x="{x0}" y="{top+3}" width="{span}" height="{gy-top-5}"/></clipPath>')
    d.add(f'<rect x="{x0:.1f}" y="{top+3:.1f}" width="{span:.1f}" height="{gy-top-5:.1f}" fill="{d.mesh()}" class="k-meshfill"/>')
    d.rect(x0, top, span, 3, "k-st")
    d.line(x0, gy - 3, x0 + span, gy - 3, "k-wire-t")
    for i in range(bays + 1):
        px = x0 + i * ft(bay)
        terminal = i in (0, bays)
        w = 6 if terminal else 4
        d.rect(px - w / 2, top - 2, w, gy - top + 2, "k-st")
        if barbed:
            ax = px + 12
            d.line(px, top - 1, ax, top - 13, "k-arm")
    if barbed:
        for k in range(3):
            yy = top - 4 - k * 4.2
            xx = x0 + 4 + k * 4
            d.line(xx, yy, x0 + span + 4 + k * 4, yy, "k-barb")
            bx = xx + 6
            while bx < x0 + span + k * 4:
                d.path(f"M{bx-1.6:.1f} {yy-1.6:.1f} L{bx+1.6:.1f} {yy+1.6:.1f} M{bx+1.6:.1f} {yy-1.6:.1f} L{bx-1.6:.1f} {yy+1.6:.1f}", "k-barb")
                bx += 11
    return top


# ======================================================================
#  SHEETS — each returns an SVG string. labels=False for card thumbnails.
# ======================================================================

def _sheet(w, h, title, labels):
    return D(w, h, title, labels)


def sheet_board_on_board(labels=True, h=8):
    d = _sheet(560, 268, f"Elevation of a {h}-foot board-on-board cedar privacy fence with steel posts", labels)
    gy, x0 = 196, 52
    top = fence_wood(d, x0, gy, bays=3, bay=8, h=h, style="bob")
    d.ground(20, 540, gy)
    d.dim_v(top, gy, 30, fmt_ft(h), ext_from=x0 - 4)
    d.dim_h(x0, x0 + ft(8), gy + 30, "8'-0\" O.C.", ext_from=gy + 2)
    d.callout(x0 + ft(16), top + 2, x0 + ft(16) + 40, top - 22, "CAP &amp; TRIM")
    d.callout(x0 + ft(8), top + 70, x0 + ft(8) + 46, top + 52, "GALV. STEEL POST")
    d.callout(x0 + ft(20), gy - 6, x0 + ft(20) + 30, gy + 22, "ROT BOARD")
    d.title_block("F-01", "BOARD-ON-BOARD CEDAR")
    return d.svg()


def sheet_side_by_side(labels=True):
    d = _sheet(560, 280, "Elevation of a 6-foot side-by-side wood privacy fence", labels)
    gy, x0 = 216, 52
    top = fence_wood(d, x0, gy, bays=3, bay=8, h=6, style="sbs", post="wood", cap=False)
    d.ground(20, 540, gy)
    d.dim_v(top, gy, 30, "6'-0\"", ext_from=x0 - 4)
    d.dim_h(x0, x0 + ft(8), gy + 30, "8'-0\" O.C.", ext_from=gy + 2)
    d.title_block("F-01b", "SIDE-BY-SIDE PINE")
    return d.svg()


def sheet_shadowbox(labels=True):
    d = _sheet(560, 300, "Elevation of an 8-foot shadowbox cedar fence", labels)
    gy, x0 = 230, 52
    top = fence_wood(d, x0, gy, bays=3, bay=8, h=8, style="shadow")
    d.ground(20, 540, gy)
    d.dim_v(top, gy, 30, "8'-0\"", ext_from=x0 - 4)
    d.title_block("F-01c", "SHADOWBOX CEDAR")
    return d.svg()


def sheet_horizontal(labels=True):
    d = _sheet(560, 260, "Elevation of a modern horizontal cedar slat fence with black steel posts", labels)
    gy, x0 = 200, 56
    top = fence_horizontal(d, x0, gy, bays=3, bay=8, h=6)
    d.ground(20, 540, gy)
    d.dim_v(top, gy, 32, "6'-0\"", ext_from=x0 - 4)
    d.dim_h(x0, x0 + ft(8), gy + 30, "8'-0\" O.C.", ext_from=gy + 2)
    d.callout(x0 + ft(8), top + 30, x0 + ft(8) + 46, top - 12, "2x2 STEEL POST")
    d.callout(x0 + ft(18), top + 52, x0 + ft(18) + 34, top + 30, "1x6 CEDAR, 3/8\" GAP")
    d.title_block("F-02", "HORIZONTAL SLAT")
    return d.svg()


def sheet_iron(labels=True):
    d = _sheet(560, 250, "Elevation of a 5-foot ornamental steel fence with spear-top pickets", labels)
    gy, x0 = 188, 52
    top = fence_iron(d, x0, gy, bays=3, bay=8, h=5)
    d.ground(20, 540, gy)
    d.dim_v(top, gy, 30, "5'-0\"", ext_from=x0 - 4)
    d.dim_h(x0, x0 + ft(8), gy + 30, "8'-0\" PANEL", ext_from=gy + 2)
    d.callout(x0 + ft(12) + 6, top + 1, x0 + ft(12) + 46, top - 18, "SPEAR FINIAL")
    d.title_block("F-03", "ORNAMENTAL STEEL")
    return d.svg()


def sheet_pipe(labels=True):
    d = _sheet(580, 250, "Elevation of a pipe ranch fence with welded wire and an H-brace corner", labels)
    gy, x0 = 188, 48
    top = fence_pipe(d, x0, gy, bays=3, bay=10, h=4.5)
    d.ground(16, 564, gy)
    d.dim_v(top, gy, 28, "4'-6\"", ext_from=x0 - 4)
    d.dim_h(x0 + ft(10), x0 + ft(20), gy + 30, "10'-0\" O.C.", ext_from=gy + 2)
    d.callout(x0 + ft(5), top + 22, x0 + ft(5) + 30, top - 14, "H-BRACE CORNER")
    d.title_block("F-04", "PIPE &amp; RANCH")
    return d.svg()


def sheet_pool(labels=True):
    d = _sheet(560, 250, "Elevation of a 4-foot pool barrier fence with a self-closing, self-latching gate", labels)
    gy, x0 = 188, 52
    top = fence_iron(d, x0, gy, bays=2, bay=8, h=4, spear=False, gap=5.4)
    gx = x0 + ft(16) + 6
    gw = ft(4)
    d.rect(gx, top + 4, gw, gy - top - 8, "k-gate")
    x = gx + 5
    while x < gx + gw - 3:
        d.line(x, top + 6, x, gy - 6, "k-picket")
        x += 5.4
    d.rect(gx + gw + 3, top - 2, 6, gy - top + 2, "k-st")
    if labels:
        d.path(f"M{gx-2:.1f} {top+16:.1f} l3 3 l-3 3 l3 3 l-3 3", "k-spring")
    d.rect(gx + gw - 8, top + 4, 7, 10, "k-st")
    d.ground(20, 540, gy)
    d.dim_v(top, gy, 30, "4'-0\" MIN.", ext_from=x0 - 4)
    d.callout(gx - 1, top + 22, gx - 60, top - 16, "SPRING HINGE", "end")
    d.callout(gx + gw - 4, top + 9, gx + gw + 26, top - 16, "SELF-LATCHING")
    d.callout(x0 + ft(4) + 3, top + 30, x0 + ft(4) - 30, top - 30, "&lt; 4\" OPENINGS")
    d.title_block("F-05", "POOL BARRIER")
    return d.svg()


def sheet_chainlink(labels=True):
    d = _sheet(580, 270, "Elevation of a commercial chain link fence with three-strand barbed wire", labels)
    gy, x0 = 210, 50
    top = fence_chainlink(d, x0, gy, bays=3, bay=10, h=6)
    d.ground(16, 564, gy)
    d.dim_v(top, gy, 28, "6'-0\"", ext_from=x0 - 4)
    d.callout(x0 + ft(15), top - 8, x0 + ft(15) + 40, top - 32, "3-STRAND BARBED WIRE")
    d.callout(x0 + ft(25), top + 50, x0 + ft(25) + 30, top + 26, "9 GA. MESH")
    d.title_block("F-06", "COMMERCIAL CHAIN LINK")
    return d.svg()


# ---------------------------------------------------------------- gates

def _pier(d, x, gy, h, w=22):
    top = gy - ft(h)
    d.add(f'<rect x="{x:.1f}" y="{top:.1f}" width="{w}" height="{gy-top:.1f}" fill="{d.brick()}" class="k-pier"/>')
    d.rect(x - 3, top - 5, w + 6, 5, "k-capstone")
    return top


def sheet_driveway_gate(labels=True):
    d = _sheet(580, 280, "Elevation of an arched double-swing steel driveway gate between masonry piers", labels)
    gy = 220
    pl, pr = 70, 488
    _pier(d, pl, gy, 7)
    _pier(d, pr, gy, 7)
    a, b = pl + 22 + 4, pr - 4
    mid = (a + b) / 2
    base_top = gy - ft(5)
    arch = 22
    for (l, r, side) in ((a, mid - 1.5, 0), (mid + 1.5, b, 1)):
        d.path(f"M{l:.1f} {gy-8:.1f} L{l:.1f} {base_top + (arch if side == 0 else 0):.1f} "
               f"Q{(l+r)/2:.1f} {base_top + (arch*0.35 if side == 0 else arch*0.35):.1f} {r:.1f} {base_top + (0 if side == 0 else arch):.1f} "
               f"L{r:.1f} {gy-8:.1f} Z", "k-gate")
        x = l + 6
        while x < r - 3:
            t = (x - l) / (r - l)
            ytop = (base_top + arch) * (1 - t) + base_top * t if side == 0 else base_top * (1 - t) + (base_top + arch) * t
            sag = -4 * arch * 0.35 * t * (1 - t)
            d.line(x, ytop + sag + 2, x, gy - 9, "k-picket")
            x += 7
        d.rect(l, gy - 30, r - l, 2.4, "k-st")
    d.ground(20, 560, gy)
    d.dim_h(a, b, gy + 30, "16'-0\" CLEAR OPENING", ext_from=gy + 2)
    d.dim_v(base_top, gy, pl - 22, "5'-0\"", ext_from=a)
    d.callout(mid, base_top + 14, mid + 44, base_top - 22, "ARCHED TOP RAIL")
    d.title_block("G-01", "DOUBLE-SWING DRIVE GATE")
    return d.svg()


def sheet_slide_gate(labels=True):
    d = _sheet(600, 270, "Elevation of a steel slide gate on a track with an automatic operator", labels)
    gy = 210
    x0 = 120
    w = ft(18)
    top = gy - ft(6)
    d.rect(x0, top, w, gy - top - 10, "k-gate")
    x = x0 + 6
    while x < x0 + w - 3:
        d.line(x, top + 2, x, gy - 12, "k-picket")
        x += 7
    d.rect(x0, top + 26, w, 2.4, "k-st")
    for wx in (x0 + 24, x0 + w - 24):
        d.circle(wx, gy - 5, 4.5, "k-wheel")
    d.line(x0 - 60, gy - 1, x0 + w + 20, gy - 1, "k-track")
    d.rect(x0 - 50, gy - 34, 34, 30, "k-operator")
    d.rect(x0 - 46, gy - 30, 26, 4, "k-op-vent")
    d.rect(x0 + w + 8, top - 4, 7, gy - top + 4, "k-st")
    d.rect(x0 - 12, top - 4, 7, gy - top + 4, "k-st")
    d.ground(20, 580, gy)
    d.dim_v(top, gy, x0 + w + 40, "6'-0\"", ext_from=x0 + w + 16)
    d.callout(x0 - 33, gy - 32, 22, top - 12, "GATE OPERATOR")
    d.callout(x0 + 24, gy - 5, x0 + 70, gy + 26, "V-GROOVE WHEELS")
    d.title_block("G-02", "SLIDE GATE + OPERATOR")
    return d.svg()


def sheet_walk_gate(labels=True):
    d = _sheet(560, 280, "Elevation of a cedar walk gate built on a welded steel frame within a privacy fence", labels)
    gy = 216
    x0 = 50
    top = fence_wood(d, x0, gy, bays=1, bay=8, h=6, style="bob", cap=True)
    gx = x0 + ft(8) + 6
    gw = ft(4)
    _boards(d, gx + 2, gx + gw - 2, top + 6, gy - 6, "bob")
    d.rect(gx, top + 4, gw, gy - top - 8, "k-frame")
    d.line(gx + 3, gy - 10, gx + gw - 3, top + 8, "k-frame-ln")
    for hy in (top + 18, gy - 26):
        d.rect(gx - 3, hy - 2, 18, 4, "k-st")
    d.rect(gx + gw - 10, top + (gy - top) * .48, 6, 9, "k-st")
    d.rect(gx + gw + 3, top, 6, gy - top, "k-st")
    fence_wood(d, gx + gw + 6, gy, bays=1, bay=8, h=6, style="bob", cap=True)
    d.ground(20, 540, gy)
    d.dim_h(gx, gx + gw, gy + 30, "4'-0\" GATE", ext_from=gy + 2)
    d.callout(gx + gw / 2, top + (gy - top) / 2, gx + gw / 2 + 40, top - 20, "WELDED STEEL FRAME")
    d.callout(gx + 4, top + 18, gx - 50, top - 10, "HEAVY STRAP HINGE", "end")
    d.title_block("G-03", "CEDAR WALK GATE")
    return d.svg()


def sheet_access(labels=True):
    d = _sheet(580, 270, "Elevation of a gated entry with a keypad pedestal, photo eyes and intercom", labels)
    gy = 210
    x0 = 210
    w = ft(14)
    top = gy - ft(5.5)
    d.rect(x0, top, w, gy - top - 8, "k-gate")
    x = x0 + 6
    while x < x0 + w - 3:
        d.line(x, top + 2, x, gy - 10, "k-picket")
        x += 7
    d.rect(x0 - 8, top - 6, 7, gy - top + 6, "k-st")
    d.rect(x0 + w + 1, top - 6, 7, gy - top + 6, "k-st")
    d.rect(x0 - 8 - 4, gy - 40, 4, 6, "k-eye")
    d.rect(x0 + w + 8, gy - 40, 4, 6, "k-eye")
    px = 96
    d.path(f"M{px:.1f} {gy:.1f} L{px:.1f} {gy-62:.1f} Q{px:.1f} {gy-74:.1f} {px+12:.1f} {gy-74:.1f} L{px+22:.1f} {gy-74:.1f}", "k-goose")
    d.rect(px + 18, gy - 84, 18, 24, "k-keypad")
    for r in range(3):
        for c in range(3):
            d.rect(px + 21 + c * 4.6, gy - 80 + r * 5.2, 3, 3, "k-key")
    d.ground(20, 560, gy)
    d.callout(px + 36, gy - 72, px + 70, gy - 104, "KEYPAD / INTERCOM")
    d.callout(x0 + w + 10, gy - 37, x0 + w + 30, top - 22, "PHOTO-EYE BEAM")
    d.title_block("G-04", "ACCESS CONTROL")
    return d.svg()


def sheet_gate_repair(labels=True):
    d = _sheet(540, 280, "Elevation of a sagging wood gate corrected with an anti-sag cable and turnbuckle", labels)
    gy = 216
    gx, gw = 170, ft(5)
    top = gy - ft(6)
    d.rect(gx, top, gw, gy - top - 6, "k-ghost")
    d.path(f"M{gx:.1f} {top:.1f} L{gx+gw:.1f} {top+9:.1f} L{gx+gw:.1f} {gy+2:.1f} L{gx:.1f} {gy-6:.1f} Z", "k-sag")
    _boards(d, gx + 2, gx + gw - 2, top + 3, gy - 8, "sbs")
    d.rect(gx - 7, top - 6, 7, gy - top + 6, "k-st")
    d.line(gx + 4, top + 6, gx + gw - 6, gy - 12, "k-cable")
    tx, ty = gx + gw * .52, top + (gy - top) * .52
    d.rect(tx - 7, ty - 3, 14, 6, "k-turnbuckle", rx=3)
    d.ground(20, 520, gy)
    d.callout(tx, ty, tx + 70, ty - 40, "ANTI-SAG CABLE + TURNBUCKLE")
    d.callout(gx + gw, top + 8, gx + gw + 40, top - 16, "DROPPED LATCH SIDE")
    d.callout(gx + gw / 2, top, gx + gw / 2 - 40, top - 22, "TRUE LINE", "end")
    d.title_block("G-05", "GATE REALIGNMENT")
    return d.svg()


# ----------------------------------------------------------------- decks

def _house(d, x, gy, top):
    d.rect(x, top, 22, gy - top, "k-wall")
    y = top + 6
    while y < gy:
        d.line(x, y, x + 22, y, "k-siding")
        y += 7


def sheet_wood_deck(labels=True, composite=False):
    title = ("Side elevation of a composite deck with aluminum rail, beam, posts and footings" if composite
             else "Side elevation of a wood deck with railing, beam, posts, footings and stairs")
    d = _sheet(600, 300, title, labels)
    gy = 226
    hx = 40
    _house(d, hx, gy, 40)
    deck_y = gy - ft(3)
    x1 = hx + 22
    x2 = x1 + ft(16)
    d.rect(x1, deck_y, x2 - x1, 5, "k-deckboard" if composite else "k-wd")
    d.rect(x1, deck_y + 5, x2 - x1, 12, "k-joist")
    d.rect(x1, deck_y + 5, 4, 12, "k-st")
    d.rect(x2 - 34, deck_y + 17, 30, 9, "k-beam")
    for px in (x2 - 30, x2 - 12):
        d.rect(px, deck_y + 26, 7, gy - deck_y - 26, "k-post")
    for px in (x2 - 32, x2 - 14):
        d.add(f'<rect x="{px:.1f}" y="{gy:.1f}" width="12" height="18" fill="{d.stipple()}" class="k-footing"/>')
    rail_top = deck_y - ft(3)
    d.rect(x1 + 30, rail_top, x2 - x1 - 30, 4, "k-st" if composite else "k-wd")
    d.rect(x1 + 30, deck_y - 8, x2 - x1 - 30, 3, "k-st" if composite else "k-wd2")
    for px in (x1 + 30, x1 + 30 + (x2 - x1 - 30) / 2, x2 - 4):
        d.rect(px, rail_top, 5, deck_y - rail_top, "k-st" if composite else "k-post")
    if composite:
        b = x1 + 38
        while b < x2 - 6:
            d.line(b, rail_top + 4, b, deck_y - 8, "k-baluster")
            b += 6
    else:
        b = x1 + 38
        while b < x2 - 6:
            d.rect(b, rail_top + 4, 2.6, deck_y - rail_top - 12, "k-wd2")
            b += 7.5
    sx = x2
    steps = 4
    rise = (gy - deck_y) / steps
    run = 15
    p = f"M{sx:.1f} {deck_y:.1f} "
    for i in range(steps):
        p += f"L{sx + run*i:.1f} {deck_y + rise*(i+1):.1f} L{sx + run*(i+1):.1f} {deck_y + rise*(i+1):.1f} "
    d.path(p, "k-stair")
    d.line(sx, deck_y + 12, sx + run * steps, gy, "k-stringer")
    d.ground(16, 580, gy, depth=24)
    d.dim_v(deck_y, gy, x2 + run * steps + 22, "3'-0\"", ext_from=x2 + run * steps + 4)
    d.dim_v(rail_top, deck_y, x1 + 14, "3'-0\" GUARD", ext_from=x1 + 30)
    d.callout(x2 - 26, gy + 9, x2 - 60, gy + 38, "CONCRETE PIER FOOTING", "end")
    d.callout(x1 + 2, deck_y + 11, x1 + 40, deck_y + 32, "LEDGER, FLASHED + BOLTED")
    if composite:
        d.callout(x1 + 120, deck_y + 2, x1 + 150, deck_y - 64, "CAPPED COMPOSITE DECKING")
    d.title_block("D-02" if composite else "D-01", "COMPOSITE DECK" if composite else "CEDAR DECK")
    return d.svg()


def sheet_pergola(labels=True):
    d = _sheet(580, 280, "Front elevation of a cedar pergola with beams, rafters and purlins", labels)
    gy = 222
    xL, xR = 110, 470
    top = gy - ft(9)
    for px in (xL, xR):
        d.rect(px, top + 22, 10, gy - top - 22, "k-post")
        d.add(f'<rect x="{px-6:.1f}" y="{gy:.1f}" width="22" height="16" fill="{d.stipple()}" class="k-footing"/>')
    d.rect(xL - 30, top + 12, xR - xL + 70, 10, "k-beam")
    for i in range(14):
        rx = xL - 26 + i * ((xR - xL + 62) / 13)
        d.path(f"M{rx:.1f} {top+12:.1f} L{rx:.1f} {top:.1f} L{rx+5:.1f} {top:.1f} L{rx+5:.1f} {top+6:.1f} L{rx+3:.1f} {top+12:.1f} Z", "k-wd")
    d.rect(xL - 34, top - 5, xR - xL + 78, 5, "k-wd2")
    d.line(xL + 10, top + 22 + 18, xL + 28, top + 22, "k-brace")
    d.line(xR, top + 22 + 18, xR - 18, top + 22, "k-brace")
    d.ground(20, 560, gy)
    d.dim_v(top, gy, xR + 50, "9'-0\"", ext_from=xR + 14)
    d.dim_h(xL + 5, xR + 5, gy + 30, "12'-0\" POST TO POST", ext_from=gy + 2)
    d.callout(xL + 120, top - 2, xL + 150, top - 26, "2x2 PURLINS")
    d.callout(xL + 40, top + 6, xL - 70, top - 26, "SHAPED RAFTER TAILS")
    d.title_block("D-03", "CEDAR PERGOLA")
    return d.svg()


def sheet_patio_cover(labels=True):
    d = _sheet(580, 280, "Side elevation of an attached patio cover with a sloped roof tied into the house", labels)
    gy = 224
    hx = 40
    _house(d, hx, gy, 30)
    x1 = hx + 22
    x2 = x1 + ft(14)
    ry1 = gy - ft(10)
    ry2 = gy - ft(8.4)
    d.path(f"M{x1:.1f} {ry1:.1f} L{x2+18:.1f} {ry2:.1f} L{x2+18:.1f} {ry2+6:.1f} L{x1:.1f} {ry1+6:.1f} Z", "k-roof")
    for i in range(1, 16):
        t = i / 16
        xx = x1 + t * (x2 + 18 - x1)
        yy = ry1 + t * (ry2 - ry1)
        d.line(xx, yy, xx, yy + 6, "k-seam")
    d.rect(x2 - 16, ry2 + 4, 26, 10, "k-beam")
    d.rect(x2 - 8, ry2 + 14, 9, gy - ry2 - 14, "k-post")
    d.add(f'<rect x="{x2-14:.1f}" y="{gy:.1f}" width="22" height="16" fill="{d.stipple()}" class="k-footing"/>')
    d.add(f'<rect x="{x1:.1f}" y="{gy-3:.1f}" width="{x2-x1+10:.1f}" height="3" class="k-slab"/>')
    d.ground(16, 560, gy)
    d.dim_v(ry2 + 14, gy, x2 + 50, "8'-0\" CLEAR", ext_from=x2 + 4)
    d.callout((x1 + x2) / 2, (ry1 + ry2) / 2, (x1 + x2) / 2 + 30, ry1 - 22, "STANDING-SEAM METAL ROOF")
    d.callout(x1 + 2, ry1 + 3, x1 + 40, ry1 + 40, "LEDGER INTO WALL FRAMING")
    d.title_block("D-04", "ATTACHED PATIO COVER")
    return d.svg()


def sheet_deck_repair(labels=True):
    d = _sheet(580, 260, "Side elevation of a deck with rotted boards and a sistered joist marked for repair", labels)
    gy = 200
    x1, x2 = 60, 520
    deck_y = gy - ft(2.5)
    b = x1
    i = 0
    while b < x2:
        bad = i in (5, 6, 7, 18)
        d.rect(b, deck_y, 21, 5, "k-rot" if bad else "k-wd")
        b += 22
        i += 1
    d.rect(x1, deck_y + 5, x2 - x1, 12, "k-joist")
    d.rect(x1 + 140, deck_y + 7, 100, 8, "k-sister")
    for px in (x1 + 30, (x1 + x2) / 2, x2 - 40):
        d.rect(px, deck_y + 17, 7, gy - deck_y - 17, "k-post")
    d.ground(20, 560, gy)
    d.callout(x1 + 130, deck_y + 2, x1 + 100, deck_y - 36, "SOFT BOARDS REPLACED", "end")
    d.callout(x1 + 190, deck_y + 11, x1 + 70, deck_y + 42, "SISTERED JOIST")
    d.title_block("D-05", "DECK REPAIR")
    return d.svg()


# ---------------------------------------------------------------- repair

def sheet_fence_repair(labels=True):
    d = _sheet(560, 280, "Elevation of a wood fence with replaced boards and a straightened post", labels)
    gy, x0 = 216, 52
    top = fence_wood(d, x0, gy, bays=3, bay=8, h=6, style="sbs", post="wood", cap=False)
    nx = x0 + ft(9)
    for k in range(4):
        d.rect(nx + k * 7.3, top, 6.7, gy - top - 2, "k-new")
    px = x0 + ft(16)
    d.line(px + 10, top - 4, px, gy, "k-old")
    d.ground(20, 540, gy)
    d.callout(nx + 14, top + 30, nx + 50, top - 16, "MATCHED REPLACEMENT BOARDS")
    d.callout(px + 6, top + 10, px + 40, top + 40, "POST RESET PLUMB")
    d.title_block("R-01", "FENCE REPAIR")
    return d.svg()


def sheet_storm(labels=True):
    d = _sheet(560, 280, "Elevation of a storm-damaged fence section leaning under wind load", labels)
    gy, x0 = 216, 70
    fence_wood(d, x0, gy, bays=1, bay=8, h=6, style="sbs", post="wood", cap=False)
    sx = x0 + ft(8) + 3
    top = gy - ft(6)
    lean = 46
    for k in range(16):
        bx = sx + k * 7.3
        brk = k in (4, 5, 9)
        h = gy - top - (22 if brk else 2)
        d.path(f"M{bx:.1f} {gy-2:.1f} L{bx+lean*(h/(gy-top)):.1f} {gy-2-h:.1f} L{bx+6.7+lean*(h/(gy-top)):.1f} {gy-2-h:.1f} L{bx+6.7:.1f} {gy-2:.1f} Z",
               "k-wd" if not brk else "k-broken")
    d.line(sx + ft(8), gy, sx + ft(8) + lean, top, "k-old")
    for k in range(3):
        y = top + 20 + k * 26
        d.path(f"M{20:.1f} {y:.1f} C {36} {y-8}, {50} {y+8}, {64} {y}", "k-wind")
        d.path(f"M{60:.1f} {y-4:.1f} L{66:.1f} {y:.1f} L{60:.1f} {y+4:.1f}", "k-wind")
    d.ground(16, 540, gy)
    d.callout(sx + ft(8) + 20, top + 20, sx + ft(8) + 60, top - 14, "SNAPPED POST AT GRADE")
    d.callout(sx + 40, gy - 50, sx + 10, gy + 30, "BROKEN PICKETS", "end")
    d.title_block("R-02", "STORM DAMAGE")
    return d.svg()


def sheet_staining(labels=True):
    d = _sheet(560, 280, "Elevation of a fence half stained and sealed, half weathered grey", labels)
    gy, x0 = 216, 52
    top = gy - ft(6)
    bw = 7.3
    x = x0
    n = int(ft(24) / bw)
    for k in range(n):
        d.rect(x0 + k * bw, top, bw - .6, gy - top - 2, "k-stained" if k < n * .55 else "k-weathered")
    for i in range(4):
        d.rect(x0 + i * ft(8) - 3, top, 6, gy - top, "k-wd2")
    edge = x0 + n * .55 * bw
    d.line(edge, top - 10, edge, gy + 4, "k-wetedge")
    d.ground(20, 540, gy)
    d.note(edge - 8, top - 16, "STAINED + SEALED", "end")
    d.note(edge + 8, top - 16, "WEATHERED", "start")
    d.title_block("R-03", "STAIN &amp; SEAL")
    return d.svg()


def sheet_post_section(labels=True, caption="POST SETTING IN CLAY"):
    d = _sheet(420, 380, "Section through a steel fence post set in a concrete footing in expansive clay soil", labels)
    gy = 150
    cx = 214
    d.rect(20, gy, 380, 210, "k-clay-bg")
    d.add(f'<rect x="20" y="{gy}" width="380" height="210" fill="{d.soil()}" class="k-soil"/>')
    fw = 44
    depth = ft(3) + 10
    d.add(f'<path d="M{cx-fw/2:.1f} {gy:.1f} L{cx-fw/2-6:.1f} {gy+depth:.1f} L{cx+fw/2+6:.1f} {gy+depth:.1f} L{cx+fw/2:.1f} {gy:.1f} Z" fill="{d.stipple()}" class="k-concrete"/>')
    d.add(f'<rect x="{cx-fw/2-6:.1f}" y="{gy+depth:.1f}" width="{fw+12:.1f}" height="14" fill="{d.gravel()}" class="k-gravel"/>')
    d.path(f"M{cx-fw/2-4:.1f} {gy:.1f} Q{cx:.1f} {gy-8:.1f} {cx+fw/2+4:.1f} {gy:.1f}", "k-crown")
    d.rect(cx - 5, 20, 10, gy + depth - 30, "k-st")
    d.rect(cx + 5, 40, 30, 7, "k-wd")
    d.rect(cx + 5, 100, 30, 7, "k-wd")
    d.rect(cx + 35, 30, 7.3, 120, "k-wd")
    d.line(20, gy, 400, gy, "k-grade")
    d.dim_v(gy, gy + depth, cx - fw / 2 - 30, "3'-0\" EMBED", ext_from=cx - fw / 2 - 8)
    d.callout(cx + fw / 2 + 2, gy - 3, cx + 52, gy - 36, "CROWNED TOP SHEDS WATER")
    d.callout(cx - 4, 70, cx - 50, 52, "2-3/8\" STEEL POST", "end")
    d.callout(cx + fw / 2 - 2, gy + 26, cx + 84, gy + 26, "CONCRETE FOOTING")
    d.callout(cx + fw / 2 + 6, gy + depth + 7, cx + 84, gy + depth + 7, "GRAVEL BASE")
    d.callout(80, gy + 100, 34, gy + 132, "EXPANSIVE CLAY")
    d.note(38, gy + 148, "SWELLS WET, SHRINKS DRY")
    d.title_block("R-04", caption, scale="1&quot; = 1'-0&quot;")
    return d.svg()


def sheet_removal(labels=True):
    d = _sheet(580, 270, "Elevation of an old fence being removed and hauled away, with post holes backfilled", labels)
    gy, x0 = 210, 40
    top = gy - ft(6)
    d.rect(x0, top, ft(16), gy - top, "k-remove")
    x = x0
    while x < x0 + ft(16):
        d.line(x, top, x, gy, "k-remove-ln")
        x += 7.3
    for k in range(3):
        px = x0 + k * ft(8)
        d.add(f'<rect x="{px-7:.1f}" y="{gy:.1f}" width="14" height="22" fill="{d.soil()}" class="k-backfill"/>')
    tx = 360
    d.path(f"M{tx:.1f} {gy-50:.1f} L{tx+170:.1f} {gy-50:.1f} L{tx+170:.1f} {gy-14:.1f} L{tx:.1f} {gy-14:.1f} Z", "k-trailer")
    d.circle(tx + 40, gy - 8, 7, "k-wheel")
    d.circle(tx + 130, gy - 8, 7, "k-wheel")
    d.line(tx, gy - 30, tx - 26, gy - 20, "k-st-ln")
    for k in range(5):
        d.rect(tx + 10 + k * 30, gy - 62 - (k % 2) * 4, 26, 6, "k-wd2")
    d.path(f"M{x0+ft(16)+16:.1f} {top+40:.1f} L{tx-20:.1f} {top+40:.1f}", "k-arrow")
    d.path(f"M{tx-28:.1f} {top+34:.1f} L{tx-20:.1f} {top+40:.1f} L{tx-28:.1f} {top+46:.1f}", "k-arrow")
    d.ground(16, 564, gy, depth=26)
    d.callout(x0 + ft(8), gy + 12, x0 + 30, gy + 44, "FOOTINGS PULLED + BACKFILLED")
    d.note(tx + 85, gy - 76, "HAUL-OFF", "middle")
    d.title_block("R-05", "FENCE REMOVAL")
    return d.svg()


# --------------------------------------------------------- land clearing

def _cloud(d, pts, base="k-canopy"):
    """Union-of-circles canopy: outline layer first, fill layer on top, so
    the cloud reads as one clean shape instead of overlapping rings."""
    for x, y, r in pts:
        d.circle(x, y, r + .9, base + "-ol")
    for x, y, r in pts:
        d.circle(x, y, r, base)


def _tree(d, x, gy, h=150, spread=46, keeper=False):
    trunk_top = gy - h * .45
    d.rect(x - 3.5, trunk_top, 7, gy - trunk_top, "k-trunk")
    cy = gy - h * .68
    pts = [(x, cy - spread * .35, spread * .55), (x - spread * .55, cy + 2, spread * .45),
           (x + spread * .55, cy + 4, spread * .45), (x - spread * .2, cy + spread * .3, spread * .42),
           (x + spread * .25, cy - spread * .05, spread * .5)]
    _cloud(d, pts, "k-keeper" if keeper else "k-canopy")
    if keeper:
        d.rect(x - 4.5, gy - 34, 9, 6, "k-flag")


def _brush(d, x0, x1, gy, h=28, seed=3):
    x, i = x0, seed
    pts = []
    while x < x1:
        r = h * (.42 + ((i * 37) % 10) / 40)
        pts.append((x, gy - r * .78, r))
        x += r * 1.15
        i += 1
    _cloud(d, pts, "k-scrub")


def _sapling(d, x, gy, h=70, lean=0):
    top_x = x + lean
    d.line(x, gy, top_x, gy - h * .55, "k-stem")
    _cloud(d, [(top_x, gy - h * .7, h * .22), (top_x - h * .14, gy - h * .58, h * .17), (top_x + h * .15, gy - h * .6, h * .18)], "k-scrub")


def _stake(d, x, gy):
    d.rect(x - 1.6, gy - 34, 3.2, 34, "k-stake")
    d.path(f"M{x+1.6:.1f} {gy-34:.1f} L{x+15:.1f} {gy-29:.1f} L{x+1.6:.1f} {gy-24:.1f} Z", "k-flag")


def _mulch(d, x1, x2, gy):
    pid = f"{d.id}-chips"
    if not any(pid in q for q in d.defs):
        d.defs.append(f'<pattern id="{pid}" width="12" height="6" patternUnits="userSpaceOnUse">'
                      f'<rect width="12" height="6" class="k-mulch-bg"/><path d="M1 4l3-2M6 5l3-3M9 2l2 2" class="k-chip"/></pattern>')
    d.add(f'<rect x="{x1:.1f}" y="{gy-5:.1f}" width="{x2-x1:.1f}" height="5" fill="url(#{pid})" class="k-mulch"/>')


def _ctl(d, x, gy, head="mulcher", flip=False, scale=1.0):
    """Compact track loader, side elevation. Local origin is the rear of the
    track at grade; the machine faces +x (or -x when flipped)."""
    sx = -scale if flip else scale
    g = [f'<g transform="translate({x:.1f} {gy:.1f}) scale({sx} {scale})">']
    R = lambda a, b, w, h, c, rx=0: g.append(f'<rect x="{a}" y="{b}" width="{w}" height="{h}"{f" rx={chr(34)}{rx}{chr(34)}" if rx else ""} class="{c}"/>')
    P = lambda dd, c: g.append(f'<path d="{dd}" class="{c}"/>')
    C = lambda a, b, r, c: g.append(f'<circle cx="{a}" cy="{b}" r="{r}" class="{c}"/>')
    L = lambda a, b, c2, d2, c: g.append(f'<line x1="{a}" y1="{b}" x2="{c2}" y2="{d2}" class="{c}"/>')
    R(0, -26, 150, 26, "k-track-out", 13)
    R(5, -21, 140, 16, "k-track-in", 8)
    C(14, -13, 10, "k-wheel"); C(136, -13, 10, "k-wheel")
    for wx in (48, 76, 104):
        C(wx, -7, 5, "k-wheel")
    R(10, -48, 132, 22, "k-machine")
    R(2, -72, 58, 24, "k-machine")
    R(54, -112, 60, 64, "k-cab")
    R(61, -104, 46, 48, "k-glass")
    L(66, -96, 80, -62, "k-glare")
    R(50, -117, 68, 6, "k-st")
    L(30, -54, 70, -80, "k-cyl")
    P("M12 -50 L20 -94 L36 -98 L158 -52 L158 -40 L142 -40 L36 -82 L28 -50 Z", "k-arm")
    C(26, -90, 3, "k-pin-pivot")
    if head == "mulcher":
        P("M152 -52 L198 -52 Q216 -52 216 -34 L216 -8 L152 -8 Z", "k-head")
        C(186, -23, 15, "k-drum")
        for k in range(12):
            a = k * math.pi / 6
            L(186 + 15 * math.cos(a), -23 + 15 * math.sin(a), 186 + 20 * math.cos(a), -23 + 20 * math.sin(a), "k-teeth")
        L(152, -4, 216, -4, "k-skid")
    elif head == "cutter":
        P("M152 -22 L226 -22 L230 -14 L230 -4 L152 -4 Z", "k-head")
        R(172, -31, 38, 9, "k-head")
        L(158, -7, 224, -7, "k-blade")
    else:
        P("M152 -46 L178 -46 L202 -6 L202 -1 L152 -1 Z", "k-head")
        L(178, -46, 202, -6, "k-edge")
    g.append("</g>")
    d.add("".join(g))


def sheet_land_clearing(labels=True):
    d = _sheet(600, 300, "Elevation of acreage being cleared: dense brush and small trees mulched, a flagged keeper oak left standing", labels)
    gy = 226
    for tx, th, sp in ((34, 150, 40), (92, 120, 34), (150, 170, 46)):
        _tree(d, tx, gy, th, sp)
    _brush(d, 10, 210, gy, 30)
    _sapling(d, 196, gy, 66, 10)
    _ctl(d, 432, gy, "mulcher", flip=True)
    _mulch(d, 222, 588, gy)
    _tree(d, 536, gy, 190, 50, keeper=True)
    d.ground(8, 592, gy)
    d.callout(120, gy - 24, 70, gy - 128 - 30, "BRUSH + SMALL TREES")
    d.callout(250, gy - 22, 286, gy - 150, "MULCHING HEAD")
    d.callout(536, gy - 31, 496, gy - 214, "KEEPER OAK, FLAGGED", "end")
    d.callout(330, gy - 3, 300, gy + 32, "MULCH LEFT AS GROUND COVER", "end")
    d.title_block("L-01", "ACREAGE CLEARING")
    return d.svg()


def sheet_lot_clearing(labels=True):
    d = _sheet(600, 304, "Elevation of a residential lot cleared between survey stakes, brush on one side and clean ground on the other", labels)
    gy = 208
    _stake(d, 34, gy)
    _stake(d, 566, gy)
    _brush(d, 46, 250, gy, 34, seed=5)
    _sapling(d, 120, gy, 80, -6)
    _sapling(d, 210, gy, 64, 8)
    d.rect(150, gy - 16, 46, 7, "k-debris")
    d.line(158, gy - 9, 188, gy - 20, "k-debris-ln")
    _ctl(d, 470, gy, "bucket", flip=True)
    d.ground(10, 590, gy)
    d.dim_h(34, 566, gy + 26, "LOT LIMITS", ext_from=gy + 2)
    d.callout(34, gy - 30, 70, gy - 120, "SURVEY STAKE")
    d.callout(172, gy - 13, 196, gy - 104, "DUMPED DEBRIS")
    d.callout(520, gy - 3, 560, gy - 128, "CLEARED TO GRADE", "end")
    d.title_block("L-02", "LOT CLEARING")
    return d.svg()


def sheet_brush(labels=True):
    d = _sheet(600, 270, "Elevation of a rotary brush cutter on a track loader cutting dense privet and greenbriar near grade", labels)
    gy = 204
    _brush(d, 12, 300, gy, 44, seed=2)
    for sx, sh, ln in ((60, 92, -8), (150, 84, 6), (250, 74, 10)):
        _sapling(d, sx, gy, sh, ln)
    _ctl(d, 540, gy, "cutter", flip=True)
    x = 300
    while x < 588:
        d.line(x, gy, x + 1.5, gy - 4, "k-stubble")
        x += 6
    d.ground(8, 592, gy)
    d.callout(150, gy - 40, 110, gy - 150, "PRIVET + GREENBRIAR")
    d.callout(318, gy - 14, 360, gy - 150, "ROTARY BRUSH CUTTER")
    d.callout(470, gy - 3, 420, gy + 30, "CUT NEAR GRADE")
    d.title_block("L-03", "BRUSH CLEARING")
    return d.svg()


def sheet_fence_line(labels=True):
    d = _sheet(600, 300, "Plan of a cleared strip along a property line, with survey pins, new fence posts and flagged keeper trees", labels)
    y0, y1, line_y = 104, 200, 152
    pid = f"{d.id}-scrubplan"
    d.defs.append(f'<pattern id="{pid}" width="14" height="12" patternUnits="userSpaceOnUse">'
                  f'<path d="M2 6a3 3 0 0 1 6 0a3 3 0 0 1 4 1" class="k-scrubplan"/></pattern>')
    d.add(f'<rect x="20" y="22" width="560" height="{y0-22}" fill="url(#{pid})" class="k-planzone"/>')
    d.add(f'<rect x="20" y="{y1}" width="560" height="{258-y1}" fill="url(#{pid})" class="k-planzone"/>')
    d.rect(20, y0, 560, y1 - y0, "k-strip")
    for tx, ty, r, keep in ((70, 52, 20, False), (190, 60, 26, True), (330, 46, 18, False), (470, 58, 24, False),
                            (110, 236, 22, False), (240, 244, 18, False), (340, 230, 26, True)):
        d.circle(tx, ty, r, "k-plantree-keep" if keep else "k-plantree")
        d.circle(tx, ty, r * .45, "k-plantree-in")
        d.circle(tx, ty, 1.6, "k-st")
    d.line(20, line_y, 580, line_y, "k-propline")
    for px in range(60, 560, 40):
        d.rect(px - 3, line_y - 3, 6, 6, "k-st")
    for px in (30, 570):
        d.circle(px, line_y, 5, "k-pinplan")
        d.line(px - 7, line_y, px + 7, line_y, "k-th")
        d.line(px, line_y - 7, px, line_y + 7, "k-th")
    d.dim_v(y0, y1, 44, "12'-0\" CLEARED", ext_from=20)
    d.callout(30, line_y + 4, 70, line_y + 30, "SURVEY PIN")
    d.callout(220, line_y, 250, line_y - 28, "NEW POSTS ON THE LINE")
    d.callout(190 + 18, 60 - 18, 240, 30, "KEEPER TREE, FLAGGED")
    d.text(560, line_y - 7, "PROPERTY LINE", "k-note", "end")
    d.title_block("L-04", "FENCE LINE CLEARING", scale="1&quot; = 20'-0&quot;")
    return d.svg()


def sheet_mulching(labels=True):
    d = _sheet(600, 290, "Elevation of a forestry mulching head grinding a small tree into mulch left on the ground", labels)
    gy = 222
    _mulch(d, 12, 330, gy)
    _ctl(d, 60, gy, "mulcher", flip=False, scale=1.25)
    _sapling(d, 352, gy, 96, -14)
    _brush(d, 360, 470, gy, 26, seed=7)
    _tree(d, 540, gy, 180, 44, keeper=True)
    d.ground(8, 592, gy)
    d.callout(60 + 186 * 1.25, gy - 23 * 1.25, 360, gy - 170, "CARBIDE-TOOTH DRUM")
    d.callout(140, gy - 3, 110, gy + 34, "MULCH LEFT ON THE SOIL")
    d.callout(540, gy - 31, 500, gy - 206, "KEEPER TREE, FLAGGED", "end")
    d.title_block("L-05", "FORESTRY MULCHING")
    return d.svg()


def sheet_grading(labels=True):
    d = _sheet(600, 290, "Section through a yard regraded to fall away from the foundation, showing existing grade, finished grade, cut and fill", labels)
    hx = 70
    d.rect(18, 70, hx - 18, 108, "k-wall")
    y = 76
    while y < 176:
        d.line(18, y, hx, y, "k-siding")
        y += 7
    d.rect(10, 170, hx - 6, 12, "k-slab")
    xs = list(range(hx, 581, 6))
    ye = lambda x: 196 - (x - hx) * .055 + 3 * math.sin(x / 37)        # drains toward the house
    def yf(x):
        t = x - hx
        return 176 + (t / 160) * 8 if t <= 160 else 184 + (t - 160) * .03   # 6" in the first 10'
    fill_pts, cut_pts = [], []
    for x in xs:
        a, b = ye(x), yf(x)
        (fill_pts if b < a else cut_pts).append((x, a, b))
    def poly(pts, cls):
        if len(pts) < 2:
            return
        top = " ".join(f"{x:.1f},{min(a, b):.1f}" for x, a, b in pts)
        bot = " ".join(f"{x:.1f},{max(a, b):.1f}" for x, a, b in reversed(pts))
        d.add(f'<polygon points="{top} {bot}" class="{cls}"/>')
    poly(fill_pts, "k-fillzone")
    poly(cut_pts, "k-cutzone")
    d.add(f'<path d="M{hx} {yf(hx):.1f} ' + " ".join(f"L{x} {yf(x):.1f}" for x in xs) + f' L580 270 L{hx} 270 Z" fill="{d.soil()}" class="k-soil"/>')
    d.path(f"M{hx} {ye(hx):.1f} " + " ".join(f"L{x} {ye(x):.1f}" for x in xs), "k-oldgrade")
    d.path(f"M{hx} {yf(hx):.1f} " + " ".join(f"L{x} {yf(x):.1f}" for x in xs), "k-grade")
    for ax in (300, 420):
        d.path(f"M{ax} {yf(ax)-12:.1f} L{ax+34} {yf(ax+34)-12:.1f} M{ax+28} {yf(ax+28)-16:.1f} L{ax+34} {yf(ax+34)-12:.1f} L{ax+28} {yf(ax+28)-8:.1f}", "k-arrow")
    d.dim_h(hx, hx + 160, 236, "10'-0\"", ext_from=yf(hx + 160) + 4)
    d.dim_v(yf(hx), yf(hx + 160), hx + 186, "6\" FALL", ext_from=hx + 164)
    d.callout(110, (yf(110) + ye(110)) / 2, 140, 120, "FILL, COMPACTED IN LIFTS")
    d.callout(500, (yf(500) + ye(500)) / 2, 520, 120, "CUT")
    d.callout(262, ye(262), 226, 262, "EXISTING GRADE")
    d.callout(360, yf(360) - 14, 392, 96, "WATER RUNS AWAY")
    d.title_block("L-06", "SITE GRADING", scale="1/4&quot; = 1'-0&quot;")
    return d.svg()


# ----------------------------------------------------------- brand mark

def logo_mark(size=36):
    """A fence post with two diagonal braces: reads as a K, and is the
    brace you see on every ranch-fence corner in Texas."""
    return (f'<svg class="brand-mark" width="{size}" height="{size}" viewBox="0 0 40 40" aria-hidden="true">'
            f'<rect x="1" y="1" width="38" height="38" class="bm-frame"/>'
            f'<rect x="11" y="7" width="5.5" height="26" class="bm-post"/>'
            f'<path d="M16.5 20 L29 7.5 L32.5 7.5 L32.5 10 L20.6 21.6 Z" class="bm-brace"/>'
            f'<path d="M18.4 18.6 L32.5 30 L32.5 33 L29 33 L16.5 22.4 Z" class="bm-brace"/>'
            f'</svg>')


SHEETS = {
    "board_on_board": sheet_board_on_board,
    "side_by_side": sheet_side_by_side,
    "shadowbox": sheet_shadowbox,
    "horizontal": sheet_horizontal,
    "iron": sheet_iron,
    "pipe": sheet_pipe,
    "pool": sheet_pool,
    "chainlink": sheet_chainlink,
    "driveway_gate": sheet_driveway_gate,
    "slide_gate": sheet_slide_gate,
    "walk_gate": sheet_walk_gate,
    "access": sheet_access,
    "gate_repair": sheet_gate_repair,
    "wood_deck": sheet_wood_deck,
    "composite_deck": lambda labels=True: sheet_wood_deck(labels, composite=True),
    "pergola": sheet_pergola,
    "patio_cover": sheet_patio_cover,
    "deck_repair": sheet_deck_repair,
    "fence_repair": sheet_fence_repair,
    "storm": sheet_storm,
    "staining": sheet_staining,
    "post_section": sheet_post_section,
    "removal": sheet_removal,
    "land_clearing": sheet_land_clearing,
    "lot_clearing": sheet_lot_clearing,
    "brush": sheet_brush,
    "fence_line": sheet_fence_line,
    "mulching": sheet_mulching,
    "grading": sheet_grading,
}


def drawing(key, labels=True):
    return SHEETS[key](labels=labels)
