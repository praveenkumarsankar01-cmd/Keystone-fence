"""Street maps in the look of Google Maps, rendered once from OpenStreetMap data.

    python3 src/static_maps.py [key ...]      # writes static/assets/maps/<key>.{webp,jpg}

Each map is drawn by MapLibre GL in headless Chromium from OpenFreeMap vector tiles,
recoloured to Google's current palette (near-white land, grey-blue roads without
casings, mint parks, cream commercial areas), then saved as an image. The preview
build shows these maps, since the artifact preview can't load Google's map frame;
build.py pins the service cities on top with project(). Live pages embed Google Maps.
Credit (shown on every map): OpenFreeMap, © OpenMapTiles, data © OpenStreetMap
contributors (ODbL). Run it again only when a city or a framing below changes.
"""
import io, json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data_site import CITIES

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "static", "assets", "maps")
STYLE = "https://tiles.openfreemap.org/styles/liberty"
MAPLIBRE = "https://unpkg.com/maplibre-gl@5.24.0/dist/maplibre-gl"
PLANO = next(c for c in CITIES if c["slug"] == "plano")

# key -> (lat, lon, zoom, fx, fy, width, height, scale): the point sits at fraction (fx, fy) of a
# width x height CSS-px frame, sized close to how big the map shows on the page so its labels read
# at their natural size; scale is the device-pixel ratio of the saved image. Zoom uses 256-px tiles.
# Framed maps keep their pins left of centre, clear of the key map in the top-right corner.
MAPS = {"collin-county": (*PLANO["ll"], 10.5, 0.36, 0.71, 560, 420, 2),
        "collin-county-wide": (33.0927, -96.7196, 10.75, 0.5, 0.5, 1500, 600, 1.6)}
MAPS.update({c["slug"]: (*c["ll"], 11.5, 0.4, 0.62, 560, 420, 2) for c in CITIES})

# Google's palette, applied over the "liberty" style's layers. The map's own labels for the
# cities build.py pins are hidden, so each shows once, as a red pin label.
RESTYLE = r"""
(map, pinned) => {
  const hide = /^(natural_earth|park_outline|landuse_residential|road_area_pattern|building-3d)$|_casing$|^road_one_way/;
  const fill = {background: '#f8f8f8', park: '#d2f2e0', landcover_grass: '#d2f2e0', landuse_pitch: '#d2f2e0',
    landuse_track: '#d2f2e0', landcover_wood: '#c8eed8', landcover_wetland: '#d0efe6', landuse_cemetery: '#dbefe3',
    landuse_hospital: '#fbe8e7', landuse_school: '#f4f1ea', landcover_sand: '#f5efe0', landcover_ice: '#ffffff',
    water: '#9dd3f3', aeroway_fill: '#eceff3', building: '#eceef1'};
  const road = [[/motorway(?!_link)/, '#b9c7d5'], [/trunk_primary/, '#cad4de'], [/secondary_tertiary/, '#d6dee6'],
    [/rail/, '#c3c8ce'], [/path_pedestrian/, '#e2e7eb'], [/./, '#dee4e9']];
  for (const l of map.getStyle().layers) {
    const id = l.id;
    if (hide.test(id)) { map.setLayoutProperty(id, 'visibility', 'none'); continue; }
    if (fill[id]) {
      const key = l.type === 'background' ? 'background-color' : 'fill-color';
      map.setPaintProperty(id, key, fill[id]);
      if (l.type === 'fill') { map.setPaintProperty(id, 'fill-opacity', 1); if (l.paint && l.paint['fill-pattern']) map.setPaintProperty(id, 'fill-pattern', undefined); }
      if (id === 'building') map.setPaintProperty(id, 'fill-outline-color', '#e1e4e8');
    } else if (/^(road|bridge|tunnel)_/.test(id) && l.type === 'line') {
      map.setPaintProperty(id, 'line-color', road.find(([re]) => re.test(id))[1]);
      if (id.startsWith('tunnel_')) map.setPaintProperty(id, 'line-opacity', 0.55);
    } else if (/^waterway/.test(id) && l.type === 'line') {
      map.setPaintProperty(id, 'line-color', '#9dd3f3');
    } else if (/^aeroway_(runway|taxiway)$/.test(id)) {
      map.setPaintProperty(id, 'line-color', '#d8dee6');
    } else if (/^boundary/.test(id)) {
      map.setPaintProperty(id, 'line-color', '#a8adb3');
    } else if (l.type === 'symbol' && l.layout && l.layout['text-field'] !== undefined) {
      const color = /^(water|waterway)/.test(id) ? '#3b7fc0' : /^label_(city|town|village|other)/.test(id) ? '#3c4043'
                  : /^poi/.test(id) ? null : '#5f6368';
      if (color) map.setPaintProperty(id, 'text-color', color);
      map.setPaintProperty(id, 'text-halo-color', '#ffffff');
      map.setPaintProperty(id, 'text-halo-width', 1.6);
      if (/^label_(city|town|village|other)/.test(id))
        for (const prop of ['text-opacity', 'icon-opacity'])
          map.setPaintProperty(id, prop, ['case', ['in', ['get', 'name'], ['literal', pinned]], 0, 1]);
    }
  }
  map.addLayer({id: 'landuse_commercial', type: 'fill', source: 'openmaptiles', 'source-layer': 'landuse',
    filter: ['in', ['get', 'class'], ['literal', ['commercial', 'retail', 'industrial']]],
    paint: {'fill-color': '#fdf6e9'}}, 'water');
}
"""

PAGE = """<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="{lib}.css"><script src="{lib}.js"></script>
<style>html,body,#m{{margin:0;width:100%;height:100%;background:#f8f8f8}}</style></head>
<body><div id="m"></div><script>
const map = new maplibregl.Map({{container: 'm', style: '{style}', center: [{lon}, {lat}], zoom: {zoom},
  interactive: false, attributionControl: false, fadeDuration: 0, canvasContextAttributes: {{preserveDrawingBuffer: true}}}});
map.on('load', () => {{ ({restyle})(map, {pinned}); map.once('idle', () => {{ window.done = true; }}); map.triggerRepaint(); }});
map.on('error', e => {{ window.mapError = String(e.error && e.error.message || e); }});
</script></body></html>"""


def _world(lat, lon, z):
    n = 256 * 2 ** z
    s = math.sin(math.radians(lat))
    return (lon + 180) / 360 * n, (0.5 - math.log((1 + s) / (1 - s)) / (4 * math.pi)) * n


def size(key):
    return MAPS[key][5:7]


def _origin(key):
    lat, lon, z, fx, fy, w, h, _ = MAPS[key]
    x, y = _world(lat, lon, z)
    return x - fx * w, y - fy * h, z


def project(key, lat, lon):
    """Fraction (0-1) across and down the map where lat/lon falls."""
    x0, y0, z = _origin(key)
    x, y = _world(lat, lon, z)
    w, h = size(key)
    return (x - x0) / w, (y - y0) / h


def pinned(key):
    """Service cities that fall inside the map, with where: [(city, fx, fy)]."""
    return [(c, *xy) for c in CITIES for xy in [project(key, *c["ll"])] if 0.03 < xy[0] < 0.97 and 0.04 < xy[1] < 0.96]


def px_per_mile(key):
    lat, z = MAPS[key][0], MAPS[key][2]
    return 1609.344 / (156543.03392 * math.cos(math.radians(lat)) / 2 ** z)


def _centre(key):
    x0, y0, z = _origin(key)
    w, h = size(key)
    n = 256 * 2 ** z
    cx, cy = x0 + w / 2, y0 + h / 2
    return math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * cy / n)))), cx / n * 360 - 180


def render(browser, key):
    from PIL import Image
    w, h = size(key)
    lat, lon = _centre(key)
    ctx = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=MAPS[key][7])
    pg = ctx.new_page()
    # MapLibre's zoom counts 512-px tiles, one level below the 256-px convention used here.
    pg.set_content(PAGE.format(lib=MAPLIBRE, style=STYLE, lat=lat, lon=lon, zoom=MAPS[key][2] - 1, restyle=RESTYLE,
                               pinned=json.dumps([c["name"] for c, _, _ in pinned(key)])))
    pg.wait_for_function("window.done === true || window.mapError", timeout=120000)
    if not pg.evaluate("window.done === true"):
        raise RuntimeError(f"{key}: {pg.evaluate('window.mapError')}")
    pg.wait_for_timeout(400)
    im = Image.open(io.BytesIO(pg.screenshot(type="png"))).convert("RGB")
    ctx.close()
    im.save(os.path.join(OUT, key + ".webp"), "WEBP", quality=82, method=6)
    im.save(os.path.join(OUT, key + ".jpg"), "JPEG", quality=84, optimize=True, progressive=True)
    print(key, f"{im.size[0]}x{im.size[1]}", f"{os.path.getsize(os.path.join(OUT, key + '.webp')) // 1024} KB webp")


if __name__ == "__main__":
    from playwright.sync_api import sync_playwright
    os.makedirs(OUT, exist_ok=True)
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
                               proxy={"server": proxy} if proxy else None,
                               args=["--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
        for key in sys.argv[1:] or MAPS:
            render(b, key)
        b.close()
