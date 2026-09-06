# lojjkli.site

Two independent Cloudflare Workers in one repo, deployed by GitHub Actions on push.

| Path     | Worker           | Hostname                             |
|----------|------------------|--------------------------------------|
| `site/`  | `lojjkli-site`   | `lojjkli.site`, `www.lojjkli.site`   |
| `relay/` | `klisteam-relay` | `relay.lojjkli.site`                 |

They share a domain but nothing else. Editing the website never touches the
relay, which matters because deploying a Worker drops its open WebSockets.

## One-time setup

1. **Point the domain at Cloudflare.** In the Cloudflare dashboard, add
   `lojjkli.site` as a zone and set the nameservers at your registrar to the two
   Cloudflare gives you. Wait for the zone to go active.

2. **Create an API token.** Dashboard → My Profile → API Tokens → Create Token →
   *Edit Cloudflare Workers* template. Restrict it to the `lojjkli.site` zone.
   Copy the token — it is shown only once.

3. **Add repo secrets.** GitHub repo → Settings → Secrets and variables →
   Actions → New repository secret:
   - `CLOUDFLARE_API_TOKEN` — the token from step 2
   - `CLOUDFLARE_ACCOUNT_ID` — dashboard sidebar, or `wrangler whoami`

4. **Push to `main`.** Both Workers deploy. The `custom_domain` routes create
   their own DNS records, so there is nothing to add by hand.

## Adding the 3D models

`site/public/index.html` loads four models at runtime:

```
models/emerald.glb
models/crystal.glb
models/sword.glb
models/utrm.glb
```

Put them in `site/public/models/`. They are not in the HTML — unlike the images,
which are inlined as base64 — so without them the viewer stays empty.

If any file is over 25 MB, Workers assets will reject it and you will need R2
instead. Check with `ls -lh site/public/models/`.

## Deploying by hand

```bash
cd site  && wrangler deploy
cd relay && wrangler deploy
```

## The team dashboard

`lojjkli.site/team` (from `site/public/team/index.html`) shows live positions from your
relay room. Enter the same team key you use in the mod: the page derives the room id and
AES key in your browser and decrypts locally, so the relay still only ever sees
ciphertext. It listens only — it never appears as a player, and it can only show frames
sent while it is open.

This is also the fastest end-to-end test, and it needs no teammate: open it with your key
while you are in game and your own position should appear within a second or two. If it
does, sending, encryption, the room, the relay and decryption all work.

## Checking the relay

`https://relay.lojjkli.site` in a browser should print `KlisTeam relay online`.
That is only a health check — the relay speaks WebSocket, not HTTP.

In the mod: `relayUrl` = `wss://relay.lojjkli.site`, `teamKey` = a long random
string shared with your team, `relayEnabled` = true.
