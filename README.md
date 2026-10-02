# Keystone Fence & Deck Co. — website

A complete, data-driven website for a multi-trade local contractor: five trade
silos (fencing, gates, decks, repair, land clearing), 27 service pages, six city
pages, projects, about, estimate and contact forms — 48 pages from one generator.

> Keystone is a fictional company. The site ships `noindex` and says so in the
> footer. Swap in a real business in `src/data_site.py` and flip `index=True`.

## Build

```bash
python3 src/build.py            # production -> dist/  (clean URLs)
python3 src/build.py --preview  # preview    -> preview/ (explicit index.html links)
```

No dependencies for a plain build. Photos need Pillow (`pip install -r requirements.txt`).

## Go live

Edit `CONFIG` in `src/data_site.py`:

- `name`, `phone`, `email`, `base_url` — the real business
- `form_access_key` — a [Web3Forms](https://web3forms.com) key (estimate + contact forms email you)
- `ga4_id`, `gsc_verification` — optional analytics / Search Console
- `index=True` and `fictional=False` — and remove the `X-Robots-Tag` header from `vercel.json`

Deploy on Vercel from this repo: `vercel.json` builds with `python3 src/build.py` and serves `dist/`.

## Media

- **Hero video** — `static/assets/media/site-walk.*`. `python3 src/video.py` renders the
  illustrated version; `python3 src/ingest_video.py clip.mp4 --start 2 --dur 15 --desc "..."`
  swaps in real footage (trimmed, 1280x720, audio removed).
- **Photos** — drop images into `photos/<key>/` (see `photos/README.txt`). The build rotates
  them upright, strips all metadata (GPS included) and writes 800/1600 px WebP + JPEG.
- **Maps** — live builds embed Google Maps (keyless); the preview build shows a schematic.

## Checks

```bash
pip install -r requirements-dev.txt
python3 src/audit.py dist      # links, H1s, titles/metas, canonicals, JSON-LD, IDs
python3 src/sweep.py dist      # horizontal overflow, every page at 320-1440 px
python3 src/test_forms.py      # estimate + contact form flows
python3 src/test_video.py      # hero video: autoplay, pause, reduced motion
```
