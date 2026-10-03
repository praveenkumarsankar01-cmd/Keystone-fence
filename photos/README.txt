Drop photos here and rebuild (python3 src/build.py). Folder = where they show:

  photos/home/                        "The work, up close" strip on the home page
  photos/fencing/   (any silo key)    strip on that trade's hub page
  photos/fencing/wood-privacy-fence/  strip on that service page
  photos/projects/F-01/               replaces the drawing on that project card

Up to 3 per strip. JPG, PNG or WebP, any size. Optional captions.json in the
same folder: {"file.jpg": {"alt": "What the photo shows", "caption": "Short caption"}}.
The build rotates each photo upright, converts it to sRGB, strips all metadata
(GPS included) and writes 800 and 1600 px WebP + JPEG versions.

Record each file's source page, author and licence in photos/CREDITS.md.
