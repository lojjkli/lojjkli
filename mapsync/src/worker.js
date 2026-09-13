/**
 * KlisTeamMod map sync.
 *
 * Stores Xaero World Map region files so teammates can fill in each other's
 * unexplored areas. R2 holds the blobs; KV holds a small manifest of what
 * exists.
 *
 * ## Why a manifest
 *
 * The obvious design - every client periodically re-downloads every teammate's
 * regions - does not fit the request budget. At 14 players for 15 hours a day
 * that is roughly 350,000 requests/day at a 30s interval, against a 100k/day
 * account-wide Workers limit that the mod's existing ban-poll and heartbeat
 * already use over half of. (We hit Cloudflare error 1027 once already from a
 * poll interval that was too aggressive.)
 *
 * So clients poll one cheap endpoint - GET /manifest - which returns a compact
 * {regionKey: hash} map from KV, and only ever call /region when a hash they
 * do not have appears. Terrain does not change; only newly explored area does,
 * so nearly every poll is a single small read that transfers nothing. That is
 * ~6,000 requests/day instead of ~350,000, for the same practical freshness.
 *
 * ## Room scoping
 *
 * Everything is namespaced by the relay room id the client is already using -
 * the same sha256-derived id from RelayShare - so map data is only ever shared
 * within one team. The room id is derived from the room name and password, so
 * possessing it already implies membership; this service never sees either.
 */

const CORS = {
  'access-control-allow-origin': '*',
  'access-control-allow-methods': 'GET,PUT,OPTIONS',
  'access-control-allow-headers': 'content-type, x-room, x-player',
  'access-control-max-age': '86400',
};

const json = (obj, status = 200) =>
  new Response(JSON.stringify(obj), {
    status,
    headers: { ...CORS, 'content-type': 'application/json' },
  });

// A region file for one 512x512 area. Real ones from a well-explored area run
// to a couple of MB; this is generous headroom while still refusing anything
// that is obviously not a region file.
const MAX_REGION_BYTES = 8 * 1024 * 1024;

// Room ids are the 32-hex-char value RelayShare derives; player names are
// Minecraft usernames. Validated so neither can be used to escape its prefix
// in an R2 key or KV key.
const ROOM_RE = /^[a-f0-9]{16,64}$/i;
const PLAYER_RE = /^[A-Za-z0-9_]{1,16}$/;
// dim is Xaero's dimension folder id, region is "<x>_<z>" with optional minus.
const DIM_RE = /^[A-Za-z0-9_%$.-]{1,64}$/;
const REGION_RE = /^-?\d{1,5}_-?\d{1,5}$/;

const manifestKey = (room) => `m:${room}`;
const objectKey = (room, dim, region, player) =>
  `${room}/${dim}/${region}/${player}.xaero`;

function badRequest(msg) {
  return json({ error: msg }, 400);
}

/** Validates the shared room/dim/region/player params used by both endpoints. */
function readParams(url, request, { needRegion, needPlayer }) {
  const room = (request.headers.get('x-room') || url.searchParams.get('room') || '').trim();
  if (!ROOM_RE.test(room)) return { error: 'bad room' };

  const out = { room };

  if (needRegion) {
    const dim = (url.searchParams.get('dim') || '').trim();
    const region = (url.searchParams.get('region') || '').trim();
    if (!DIM_RE.test(dim)) return { error: 'bad dim' };
    if (!REGION_RE.test(region)) return { error: 'bad region' };
    out.dim = dim;
    out.region = region;
  }
  if (needPlayer) {
    const player = (request.headers.get('x-player') || url.searchParams.get('player') || '').trim();
    if (!PLAYER_RE.test(player)) return { error: 'bad player' };
    out.player = player;
  }
  return out;
}

async function loadManifest(env, room) {
  const raw = await env.MANIFEST.get(manifestKey(room));
  if (!raw) return {};
  try {
    return JSON.parse(raw);
  } catch {
    return {};
  }
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (request.method === 'OPTIONS') return new Response(null, { headers: CORS });

    // ---- GET /manifest -------------------------------------------------
    // The hot path. One small KV read; clients call this every few minutes and
    // almost always find nothing new.
    if (url.pathname === '/manifest' && request.method === 'GET') {
      const p = readParams(url, request, {});
      if (p.error) return badRequest(p.error);

      const manifest = await loadManifest(env, p.room);
      return new Response(JSON.stringify({ regions: manifest }), {
        headers: {
          ...CORS,
          'content-type': 'application/json',
          // Short edge cache: 14 clients polling the same room collapse into
          // roughly one origin read per window instead of 14.
          'cache-control': 'public, max-age=30',
        },
      });
    }

    // ---- PUT /region ---------------------------------------------------
    if (url.pathname === '/region' && request.method === 'PUT') {
      const p = readParams(url, request, { needRegion: true, needPlayer: true });
      if (p.error) return badRequest(p.error);

      const body = await request.arrayBuffer();
      if (body.byteLength === 0) return badRequest('empty body');
      if (body.byteLength > MAX_REGION_BYTES) return json({ error: 'too large' }, 413);

      // Hash the bytes so clients can tell "this changed" from "same as what I
      // already have" without downloading it again.
      const digest = await crypto.subtle.digest('SHA-256', body);
      const hash = [...new Uint8Array(digest)]
        .map((b) => b.toString(16).padStart(2, '0')).join('').slice(0, 32);

      const key = objectKey(p.room, p.dim, p.region, p.player);
      await env.MAPS.put(key, body, {
        httpMetadata: { contentType: 'application/octet-stream' },
        customMetadata: { player: p.player, hash, uploaded: String(Date.now()) },
      });

      // Manifest is a read-modify-write. Last write wins, which is fine here:
      // an entry only ever moves forward to a newer upload, and a lost update
      // just means one client re-uploads on its next pass.
      const manifest = await loadManifest(env, p.room);
      manifest[`${p.dim}/${p.region}/${p.player}`] = { hash, at: Date.now() };
      await env.MANIFEST.put(manifestKey(p.room), JSON.stringify(manifest));

      return json({ ok: true, hash, bytes: body.byteLength });
    }

    // ---- GET /region ---------------------------------------------------
    // Only called when the manifest showed a hash the client does not have.
    if (url.pathname === '/region' && request.method === 'GET') {
      const p = readParams(url, request, { needRegion: true, needPlayer: true });
      if (p.error) return badRequest(p.error);

      const obj = await env.MAPS.get(objectKey(p.room, p.dim, p.region, p.player));
      if (!obj) return json({ error: 'not found' }, 404);

      return new Response(obj.body, {
        headers: {
          ...CORS,
          'content-type': 'application/octet-stream',
          'x-hash': obj.customMetadata?.hash || '',
          // Region bytes are immutable for a given hash, so this is safe to
          // cache hard - repeat pulls by other teammates hit the edge.
          'cache-control': 'public, max-age=3600',
        },
      });
    }

    return json({ error: 'not found' }, 404);
  },
};
