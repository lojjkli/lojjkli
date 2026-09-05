/**
 * Player lookup API.
 *
 *   GET /player/<name>           -> profile + tiers
 *   GET /player/<name>?debug=1   -> same, plus per-source status
 *
 * Every source is optional. If one 404s, rate-limits or changes its schema, that
 * source is marked unavailable and the rest still return. Endpoints for the tier
 * sites are guesses in places — use ?debug=1 to see which ones actually answer,
 * then fix the URL in SOURCES below without touching anything else.
 */

import { DurableObject } from "cloudflare:workers";

const CACHE_SECONDS = 900;   // 15 min; these values barely move

/**
 * Registry of players who have run the mod. Clients POST their name once per
 * session; nothing is broadcast, so this never touches the relay rooms and adds
 * no traffic between players.
 */
export class Registry extends DurableObject {
  constructor(ctx, env) {
    super(ctx, env);
    this.ctx.storage.sql.exec(
      `CREATE TABLE IF NOT EXISTS seen (
         name TEXT PRIMARY KEY, first INTEGER NOT NULL, last INTEGER NOT NULL, hits INTEGER NOT NULL
       )`);
  }
  async fetch(request) {
    const url = new URL(request.url);
    const name = (url.searchParams.get('name') || '').toLowerCase();
    if (!/^[a-z0-9_]{1,16}$/.test(name)) return new Response('bad name', { status: 400 });
    const now = Date.now();

    if (request.method === 'POST') {
      this.ctx.storage.sql.exec(
        `INSERT INTO seen (name, first, last, hits) VALUES (?, ?, ?, 1)
         ON CONFLICT(name) DO UPDATE SET last = ?, hits = hits + 1`, name, now, now, now);
      return new Response('ok');
    }
    const rows = [...this.ctx.storage.sql.exec(
      `SELECT first, last, hits FROM seen WHERE name = ?`, name)];
    return Response.json(rows.length
      ? { seen: true, firstSeen: rows[0].first, lastSeen: rows[0].last, sessions: rows[0].hits }
      : { seen: false });
  }
}

const registry = (env, name) =>
  env.REGISTRY.get(env.REGISTRY.idFromName('global'));

const CORS = {
  'access-control-allow-origin': '*',
  'access-control-allow-methods': 'GET,OPTIONS',
  'content-type': 'application/json; charset=utf-8',
};

const json = (obj, status = 200) =>
  new Response(JSON.stringify(obj, null, 2), { status, headers: CORS });

async function getJSON(url, opts = {}) {
  const r = await fetch(url, {
    ...opts,
    headers: { 'user-agent': 'KlisTeamMod/1.0 (+https://lojjkli.site)', ...(opts.headers || {}) },
  });
  if (!r.ok) throw new Error('HTTP ' + r.status);
  return r.json();
}

/** Tier sites. Each returns whatever it can; shape is normalised by `pick`. */
const SOURCES = [
  {
    id: 'mctiers',
    url: (uuid) => `https://mctiers.com/api/profile/${uuid}`,
    pick: (d) => ({ overall: d.overall ?? null, points: d.points ?? null, modes: d.rankings ?? d.gameModes ?? null }),
  },
  {
    id: 'mcpvp',
    url: (uuid) => `https://mcpvp.com/api/profile/${uuid}`,
    pick: (d) => ({ overall: d.overall ?? null, points: d.points ?? null, modes: d.rankings ?? d.kitRanks ?? null }),
  },
  {
    id: 'pvptiers',
    url: (uuid) => `https://pvptiers.com/api/profile/${uuid}`,
    pick: (d) => ({ modes: d.rankings ?? d.gameModes ?? null }),
  },
  {
    id: 'subtiers',
    url: (uuid) => `https://subtiers.net/api/profile/${uuid}`,
    pick: (d) => ({ modes: d.rankings ?? d.gameModes ?? null }),
  },
  {
    id: 'pvphq',
    url: (uuid) => `https://pvphq.net/api/profile/${uuid}`,
    pick: (d) => ({ modes: d.rankings ?? d.gameModes ?? null }),
  },
];

async function mojang(name) {
  const p = await getJSON(`https://api.mojang.com/users/profiles/minecraft/${encodeURIComponent(name)}`);
  return { uuid: p.id, name: p.name };
}

async function textures(uuid) {
  const p = await getJSON(`https://sessionserver.mojang.com/session/minecraft/profile/${uuid}`);
  const prop = (p.properties || []).find((x) => x.name === 'textures');
  if (!prop) return {};
  const decoded = JSON.parse(atob(prop.value));
  const skin = decoded.textures?.SKIN;
  return {
    skin: skin?.url ?? null,
    slim: skin?.metadata?.model === 'slim',
    cape: decoded.textures?.CAPE?.url ?? null,
  };
}

/** laby.net: name history, capes. Path has moved before, so v3 then v2. */
async function laby(uuid) {
  for (const v of ['v3', 'v2']) {
    try {
      const d = await getJSON(`https://laby.net/api/${v}/user/${uuid}/profile`);
      return {
        nameHistory: (d.username_history || d.name_history || []).map((h) => ({
          name: h.username ?? h.name,
          changedAt: h.changed_at ?? h.changedToAt ?? null,
          accurate: h.accurate ?? null,
        })),
        skins: d.skins ?? null,   // present on some versions, null on others
      };
    } catch (e) { /* try the next path */ }
  }
  throw new Error('no laby endpoint answered');
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    if (request.method === 'OPTIONS') return new Response(null, { headers: CORS });
    // clients announce themselves here on startup
    if (url.pathname === '/seen') {
      const name = (url.searchParams.get('name') || '').trim();
      if (!/^[A-Za-z0-9_]{1,16}$/.test(name)) return json({ error: 'bad name' }, 400);
      await registry(env).fetch(new Request(
        `https://r/?name=${encodeURIComponent(name)}`, { method: 'POST' }));
      return json({ ok: true });
    }

    if (!url.pathname.startsWith('/player/')) {
      return json({ ok: true, usage: '/player/<username> or /seen?name=<username>' });
    }

    const name = decodeURIComponent(url.pathname.slice('/player/'.length)).trim();
    if (!/^[A-Za-z0-9_]{1,16}$/.test(name)) return json({ error: 'bad username' }, 400);

    const debug = url.searchParams.get('debug') === '1';
    const cacheKey = new Request(`https://lookup/${name.toLowerCase()}`, request);
    const cached = await caches.default.match(cacheKey);
    if (cached && !debug) return cached;

    let profile;
    try {
      profile = await mojang(name);
    } catch (e) {
      return json({ error: 'no such player', name }, 404);
    }

    const status = {};
    const out = { name: profile.name, uuid: profile.uuid, tiers: {} };

    // skin + cape
    try {
      Object.assign(out, await textures(profile.uuid));
      status.mojang_textures = 'ok';
    } catch (e) { status.mojang_textures = String(e.message); }

    // name history / skin gallery
    try {
      Object.assign(out, await laby(profile.uuid));
      status.laby = 'ok';
    } catch (e) { status.laby = String(e.message); }

    // tier sites, all in parallel — a slow one shouldn't hold up the rest
    await Promise.all(SOURCES.map(async (src) => {
      try {
        const d = await getJSON(src.url(profile.uuid));
        out.tiers[src.id] = src.pick(d);
        status[src.id] = 'ok';
      } catch (e) {
        out.tiers[src.id] = null;
        status[src.id] = String(e.message);
      }
    }));

    // has this player ever run the mod?
    try {
      const r = await registry(env).fetch(`https://r/?name=${encodeURIComponent(profile.name.toLowerCase())}`);
      out.klisTeamMod = await r.json();
      status.registry = 'ok';
    } catch (e) { status.registry = String(e.message); }

    if (debug) out._status = status;

    const res = json(out);
    res.headers.set('cache-control', `public, max-age=${CACHE_SECONDS}`);
    if (!debug) ctx.waitUntil?.(caches.default.put(cacheKey, res.clone()));
    return res;
  },
};
