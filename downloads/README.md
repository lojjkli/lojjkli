# Public downloads

`ZValues.zip` (the built `.exe` plus `ZValues-README.txt` for whoever
downloads it) is served as a **static asset of the site itself**, from
`site/public/`. The site links to it at `/ZValues.zip`.

There is no bucket, no subdomain, no dashboard step, and no separate deploy.
Drop the file in `site/public/`, push, done.

## Why not a separate R2 bucket + dl.lojjkli.site

This folder used to describe exactly that, and the reasoning was wrong.

The argument was that unpredictable download traffic - one Discord post and
it's 10x - could eat into the Workers 100,000 requests/day account pool that
the mod depends on to enforce bans, so downloads should live on R2's separate
billing pool.

That premise is false. Cloudflare's own docs state it plainly: **"Requests to
static assets are free and unlimited"**, free plan included. A request only
counts against the Workers quota when it actually invokes Worker *code*.
Serving a file out of `site/public/` never does. So there was nothing to
protect the quota from, and the separate bucket bought nothing while adding a
bucket to create, a DNS record, a dashboard-only custom-domain step, and a
second place to remember to upload to.

It also silently broke the download: the subdomain was never actually created,
so the button pointed at a host that did not resolve
(`DNS_PROBE_FINISHED_NXDOMAIN`) - complexity that was never needed, failing in
a way that looked like a site bug.

A same-origin link has a second real advantage: the `download` attribute is
**ignored on cross-origin links**. At `/ZValues.zip` it actually applies.

## Building and publishing a release

```bash
# 1. Build the exe on Windows (build.bat in the ZValues source).
#    PyInstaller does not cross-compile, so this step is Windows-only.

# 2. Zip the exe together with the README, renaming it so it reads
#    naturally once extracted next to the exe:
cp downloads/ZValues-README.txt README.txt
zip ZValues.zip ZValues.exe README.txt
rm README.txt

# 3. Put it where the site serves from, and push:
mv ZValues.zip site/public/ZValues.zip
git add site/public/ZValues.zip && git commit -m "Release ZValues" && git push
```

The deploy workflow publishes `site/public/`, so the file goes live with the
next site deploy. Replacing it is the same three steps again.

## The one real constraint

Cloudflare caps an **individual static asset at 25 MiB**. A PyInstaller
`--onefile` build bundling Python, tkinter, requests and bs4 usually lands
well under that once zipped, but check before pushing:

```bash
ls -lh site/public/ZValues.zip
```

If it ever exceeds 25 MiB, that is the point at which moving just this file to
R2 becomes genuinely necessary rather than imagined - and this file's git
history has the old setup steps.

## What is NOT in this repo

The `.exe` and the built `.zip`. Both are build output; they get added to
`site/public/` at release time per the steps above.
