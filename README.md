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
   Copy the token - it is shown only once.

3. **Add repo secrets.** GitHub repo → Settings → Secrets and variables →
   Actions → New repository secret:
   - `CLOUDFLARE_API_TOKEN` - the token from step 2
   - `CLOUDFLARE_ACCOUNT_ID` - dashboard sidebar, or `wrangler whoami`

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

Put them in `site/public/models/`. They are not in the HTML - unlike the images,
which are inlined as base64 - so without them the viewer stays empty.

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
ciphertext. It listens only - it never appears as a player, and it can only show frames
sent while it is open.

This is also the fastest end-to-end test, and it needs no teammate: open it with your key
while you are in game and your own position should appear within a second or two. If it
does, sending, encryption, the room, the relay and decryption all work.

## Checking the relay

`https://relay.lojjkli.site` in a browser should print `KlisTeam relay online`.
That is only a health check - the relay speaks WebSocket, not HTTP.

In the mod: `relayUrl` = `wss://relay.lojjkli.site`, `teamKey` = a long random
string shared with your team, `relayEnabled` = true.

## TAGGY V3 verification

Open `/taggy/?tab=verification` and choose a server. In Roblox Verify mode, independently check Roblox OAuth, Profile Code and TAGS Hub, then select **Save & update panel**. Only selected, configured methods appear in the Discord panel and alternate method picker. Simple Verify and Off remain available. Group requirements and panel copy are still per server.

At least one available method is required in Roblox mode. Unconfigured methods are disabled in the dashboard. Existing settings keep all previously available methods until a manager saves a selection. Old buttons, submitted modals and verification attempts already in progress cannot finish through a method that the server has disabled.

The V3 video feature list is backed by existing bot modules: Roblox verification, support tickets and DM questions, raid and nuke protection, spam/link/new-account filters, honeypot channels, giveaways, role panels, polls, scheduled posts, setup checklist, dashboard and fishing. Fishing currently includes 35 fish, 6 worlds, 18 maps and 14 rods.

## Expanded TAGGY security

Security now has links for Protection, Messages, New members, Server changes, Limits and Shield & timeouts. Each server keeps its own switches and thresholds. Protection shows enabled checks and recent containment results. Missing optional Manage Webhooks or Kick Members permissions appear as actionable guidance.

Added automatic checks: copied spam across channels, cumulative ping bursts, message-edit filtering, repeated joins, rapid server edits and mass timeouts. Existing anti-nuke containment also covers prunes, thread deletions, emoji deletions and sticker deletions. Text normalization catches case, spacing and invisible-character tricks. Edited messages do not count as new posts.

Optional checks are off by default: executable file extensions, displayed-URL mismatches in Markdown links, deletion of flooded webhooks, owner-approved bot invites and owner-approved powerful permission grants. The last two allow the server owner and TAGGY owner; other actors' fresh, attributed bot additions or dangerous permission grants are contained when enabled. Ordinary staff message/join exemptions still apply. Permission rollback checks current role permissions against the audited change and reports incomplete containment when hierarchy or permissions prevent a response.

Discord deletions, timeouts and role containment require the relevant bot permissions and role position. Protection reacts to events; it does not undo deleted channels, retrieve lost messages or scan attachment contents. Link checks compare hostnames without requesting the destination. Presets adjust thresholds and preserve the selected checks. Existing saved switches retain their values, and new ordinary flood checks use their defaults.
