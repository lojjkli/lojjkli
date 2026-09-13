# klisteam-mapsync

Shares Xaero World Map region files between teammates in the same relay room,
so exploring is split across the team instead of everyone walking the same
ground.

R2 holds the region blobs. KV holds a small manifest of what exists, so the
constant "anything new?" poll never touches the bucket.

## One-time setup

Both the bucket and the KV namespace have to exist before the first deploy.
Wrangler creates neither automatically.

```bash
cd mapsync

# 1. The bucket. Name must match bucket_name in wrangler.toml.
wrangler r2 bucket create klisteam-maps

# 2. The manifest namespace. This prints an id.
wrangler kv namespace create MANIFEST
```

Paste the id from step 2 into `wrangler.toml`, replacing
`REPLACE_WITH_KV_NAMESPACE_ID`. Then:

```bash
wrangler deploy
```

After the first manual deploy, `.github/workflows/deploy-mapsync.yml` handles
it on every push that touches `mapsync/`.

The route is `maps.lojjkli.site` with `custom_domain = true`, so Wrangler
creates the DNS record itself - nothing to add in the dashboard.

## Cost

R2's free tier is 10 GB of storage, 1 million writes and 10 million reads per
month. A team's map cache is nowhere near that: the sample cache this was
designed against held 61 regions totalling a few MB, and the largest single
region file was 192 KB.

R2 also has no egress fees, which is the reason it is used here rather than
anything else - several teammates pulling the same regions costs nothing extra.

## Request budget

This matters more than storage. Workers' free plan allows 100,000 requests/day
**across the whole account**, shared with the relay, lookup and site workers.
The mod's existing ban-poll and heartbeat already use roughly 54,600/day at 14
players for 15 hours.

Clients poll `GET /manifest` every few minutes and only fetch a region when a
hash they do not already have shows up. At 14 players for 15 hours that is
about 4,700 requests/day, for a combined total near 59,000 - comfortably inside
the cap.

The naive alternative - every client re-pulling every teammate's regions on a
30 second timer - works out to roughly 350,000 requests/day, which is how you
get a Cloudflare 1027 rate-limit error. Do not remove the manifest step.

## API

All three endpoints are scoped to a relay room id, which is the same
sha256-derived id the mod already uses for its relay connection. It is derived
from the room name and password, so having it already implies membership. This
service never sees either.

| Method | Path        | Purpose |
|--------|-------------|---------|
| `GET`  | `/manifest` | `{regions: {"<dim>/<region>/<player>": {hash, at}}}`. Edge-cached 30s. |
| `PUT`  | `/region`   | Upload one region file. Body is the raw `.zip`. Returns its hash. |
| `GET`  | `/region`   | Download one region file. Immutable per hash, edge-cached 1h. |

Room comes from the `x-room` header (or `?room=`), player from `x-player`.
`/region` also needs `?dim=` and `?region=`.

Every one of those values is validated against a strict pattern before it is
used to build an R2 key, so a crafted `dim` or `player` cannot escape its
prefix and reach another room's objects.
