"""Real street maps, rendered once from OpenStreetMap tiles.

    python3 src/static_maps.py      # fetches tiles (cached in .tiles/), writes static/assets/maps/*.{webp,jpg}

The home page's full-width map uses the wide render in every build. The artifact
preview can't load Google's map frame, so its city, area and contact pages use
these too, with the service cities pinned on top (build.py places the pins with
project()); live builds embed Google Maps there. Map data © OpenStreetMap
contributors, ODbL; every map shows that credit. Run it again only when a city
or a framing below changes: it fetches 20 to 40 tiles per map.
"""
import io, math, os, sys, time, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data_site import CITIES

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "static", "assets", "maps")
W, H = 800, 600                     # framed maps; the home page's wide map sets its own size
TILES = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
UA = "KeystoneFenceSiteBuilder/1.0 (+https://github.com/praveenkumarsankar01-cmd/Keystone-fence)"
PLANO = next(c for c in CITIES if c["slug"] == "plano")

# key -> (lat, lon, zoom, fx, fy, width, height): that point sits at fraction (fx, fy) of the frame.
# Framed maps keep their pins left of centre, clear of the key map in the top-right corner;
# the wide map centres the service area between the cities card (left) and the key (right).
MAPS = {"collin-county": (*PLANO["ll"], 11, 0.36, 0.71, W, H),
        "collin-county-wide": (33.0927, -96.7196, 11, 0.5, 0.5, 1800, 720)}
MAPS.update({c["slug"]: (*c["ll"], 12, 0.4, 0.62, W, H) for c in CITIES})


def _world(lat, lon, z):
    n = 256 * 2 ** z
    s = math.sin(math.radians(lat))
    return (lon + 180) / 360 * n, (0.5 - math.log((1 + s) / (1 - s)) / (4 * math.pi)) * n


def size(key):
    return MAPS[key][5:]


def _origin(key):
    lat, lon, z, fx, fy, w, h = MAPS[key]
    x, y = _world(lat, lon, z)
    return x - fx * w, y - fy * h, z


def project(key, lat, lon):
    """Fraction (0-1) across and down the map where lat/lon falls."""
    x0, y0, z = _origin(key)
    x, y = _world(lat, lon, z)
    w, h = size(key)
    return (x - x0) / w, (y - y0) / h


def px_per_mile(key):
    lat, z = MAPS[key][0], MAPS[key][2]
    return 1609.344 / (156543.03392 * math.cos(math.radians(lat)) / 2 ** z)


def render(key, cache):
    from PIL import Image, ImageEnhance
    x0, y0, z = _origin(key)
    w, h = size(key)
    canvas = Image.new("RGB", (w, h))
    for tx in range(int(x0 // 256), int((x0 + w) // 256) + 1):
        for ty in range(int(y0 // 256), int((y0 + h) // 256) + 1):
            path = os.path.join(cache, f"{z}-{tx}-{ty}.png")
            if not os.path.exists(path):
                req = urllib.request.Request(TILES.format(z=z, x=tx, y=ty), headers={"User-Agent": UA})
                open(path, "wb").write(urllib.request.urlopen(req, timeout=30).read())
                time.sleep(0.25)
            canvas.paste(Image.open(path).convert("RGB"), (round(tx * 256 - x0), round(ty * 256 - y0)))
    # Quieter colours so the pins and the site's palette lead; streets and labels stay legible.
    canvas = ImageEnhance.Color(canvas).enhance(0.55)
    canvas = Image.blend(canvas, Image.new("RGB", (w, h), (241, 241, 236)), 0.12)
    canvas.save(os.path.join(OUT, key + ".webp"), "WEBP", quality=80, method=6)
    canvas.save(os.path.join(OUT, key + ".jpg"), "JPEG", quality=82, optimize=True, progressive=True)
    print(key, f"z{z}", f"{os.path.getsize(os.path.join(OUT, key + '.webp')) // 1024} KB webp")


if __name__ == "__main__":
    cache = os.path.join(ROOT, ".tiles")
    os.makedirs(cache, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    for key in sys.argv[1:] or MAPS:
        render(key, cache)
