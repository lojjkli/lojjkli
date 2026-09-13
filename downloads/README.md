# Public downloads

Hosts files the website links to for direct download - currently
`ZValues.zip` (the built `.exe` plus a short README for whoever downloads it).

## Why a bare R2 bucket, not a Worker

Two reasons, both learned the hard way earlier in this project:

1. **Cost/quota isolation.** Traffic straight from a custom domain to R2 is
   billed under R2's own request pricing - its own separate 1M Class A + 10M
   Class B/month free tier - not the Workers 100,000/day pool. That pool is
   already close to 59,000/day between the mod's ban-poll and the map sync
   worker (see `../mapsync/README.md`). Public download traffic is exactly the
   kind of unpredictable spike - one Discord post and it's 10x - that must
   never be able to eat into the budget the mod actually depends on to enforce
   bans. Keeping it on a completely separate billing pool makes that structural
   rather than something to remember.
2. **Nothing here needs code.** No auth, no per-request logic - just "serve
   this file to anyone." A Worker in front of that adds a point of failure and
   a second thing that could hit a rate limit, for zero benefit.

## One-time setup

```bash
wrangler r2 bucket create klisteam-downloads
```

Then in the Cloudflare dashboard: **R2 → klisteam-downloads → Settings →
Custom Domains → Connect Domain**, and add `dl.lojjkli.site`. This is a
dashboard-only step - there is no CLI command for it as of this writing, and
no wrangler.toml to deploy, since there is no Worker involved at all.

Public read access on custom domains is on by default for R2; double check it
under the same Settings tab.

## Building and uploading a release

The download is a zip, not a bare `.exe` - `ZValues-README.txt` in this folder
(the SmartScreen warning, "do I need Python" - no, how to use it) rides along
in it so anyone who downloads actually sees it, not just people who happen to
find this repo.

```bash
# 1. Build the exe on Windows (build.bat in the ZValues source). PyInstaller
#    does not cross-compile, so this step can't happen anywhere but Windows.

# 2. Zip the exe with the README, renaming the README so it reads naturally
#    once extracted next to the exe:
cp downloads/ZValues-README.txt README.txt
zip ZValues.zip ZValues.exe README.txt
rm README.txt

# 3. Upload
wrangler r2 object put klisteam-downloads/ZValues.zip --file ./ZValues.zip
```

The site links directly to `https://dl.lojjkli.site/ZValues.zip`. Re-uploading
under the same name overwrites it in place - no redeploy of anything needed.

## What is NOT here

The actual `.exe`. It has to be built on Windows, per step 1 above - nothing
running in this repo's tooling (or a Linux sandbox) can produce it.
