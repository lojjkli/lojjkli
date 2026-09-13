# Models folder

Drop the four `.glb` files the viewer loads here:

```
emerald.glb   crystal.glb   sword.glb   utrm.glb
```

They are not in git - add them manually. Until they exist the viewer shows
`MODEL NOT FOUND · missing from /models/`.

## About "stop people downloading these from devtools"

This cannot be prevented, and it is worth being precise about why rather than
shipping something that only looks like it works.

To display a 3D model, the browser has to download the whole file and hand it
to the GPU. By the time anything is on screen, the complete `.glb` already sits
in the visitor's browser cache and in memory. Every "protection" for this is
some form of making the file slightly harder to *find*, never harder to *have*:

- **Blocking right-click / F12 / devtools** - defeated by Ctrl+U, by the
  Network tab, by `curl`, by reading the page source, or by opening the cache
  folder. It also breaks normal browsing for everyone else, and the bytes are
  still fully downloaded either way. Not implemented here on purpose.
- **Obfuscated or hashed filenames** - the URL is still right there in the
  Network tab the moment the model loads.
- **Blob URLs / fetch + ObjectURL** - same bytes, one extra click to find.
- **DRM** - does not exist for glTF, and would not survive a screen-capable GPU
  anyway.

Anyone determined enough to open devtools will get the file. The only question
worth asking is what they get when they do.

### What actually works

**Serve preview-quality models, keep the sellable ones private.** Decimate the
mesh and downscale the textures for anything that goes in the web viewer. A
visitor spinning a sword on a portfolio page cannot tell a 4k-texture, 30k-tri
model from a 512px, 5k-tri one at that size - but the version they can pull out
of devtools is then not the version a client is paying for.

In Blender: Decimate modifier (~0.2-0.4 ratio is usually invisible at web
viewer size), resize textures to 512 or 1024, then export with Draco
compression on. Smaller files, faster page, and the leaked asset is worth
little on its own.

**Turn on Cloudflare Hotlink Protection** for the site. That does not stop
someone saving the file, but it does stop other sites embedding your models
straight off your bandwidth, which is the more common and more annoying
problem.

**Keep source files off the web entirely.** `.blend`, high-res texture sets,
and anything with modifier history or UV layout intact should never be reachable
from the site at any URL.
