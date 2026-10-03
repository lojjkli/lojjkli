// Only TAGGY's HTTP API is proxied. The relay and existing admin API are independent.
const PUBLIC_ORIGIN = 'https://lojjkli.site';
const headers = {
  'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff',
  'Referrer-Policy': 'no-referrer', 'X-Frame-Options': 'DENY'
};
const failure = (status, message) => Response.json({ error: message }, { status, headers });

export async function handleRequest(request, env, fetchImpl = fetch) {
  const url = new URL(request.url);
  if (!/^\/taggy\/(api|auth)(\/|$)/.test(url.pathname)) return env.ASSETS.fetch(request);
  // Canonical host keeps host-only login cookies on one origin.
  if (url.origin !== PUBLIC_ORIGIN) return failure(403, 'Use https://lojjkli.site/taggy/');
  if (!['GET', 'POST'].includes(request.method)) return failure(405, 'Method not allowed');
  if (request.method === 'POST' && request.headers.get('Origin') !== PUBLIC_ORIGIN) return failure(403, 'Invalid request origin');
  const bodyLimit = /^\/taggy\/api\/(?:owner\/dms|guilds\/\d{1,20}\/chat)$/.test(url.pathname) ? 12*1024*1024 : 65536;
  if (Number(request.headers.get('Content-Length') || 0) > bodyLimit) return failure(413, 'Request too large');
  if (!env.TAGGY_BACKEND_URL || !env.TAGGY_PROXY_SECRET || env.TAGGY_PROXY_SECRET.length < 32) return failure(503, 'TAGGY dashboard is not configured yet.');
  let target;
  try {
    target = new URL(env.TAGGY_BACKEND_URL);
    if (target.protocol !== 'https:' || target.username || target.password || target.pathname !== '/' || target.search || target.hash) throw new Error();
  } catch (_) { return failure(503, 'TAGGY backend configuration is invalid.'); }
  target.pathname = url.pathname;
  target.search = url.search;
  const forwardHeaders = new Headers();
  // Use a small explicit header list. Client-supplied proxy keys are discarded.
  for (const key of ['cookie', 'content-type', 'origin', 'x-csrf-token']) {
    const value = request.headers.get(key);
    if (value) forwardHeaders.set(key, value);
  }
  forwardHeaders.set('x-taggy-proxy-secret', env.TAGGY_PROXY_SECRET);
  forwardHeaders.set('x-taggy-client-ip', request.headers.get('CF-Connecting-IP') || 'unknown');
  try {
    // Bound the body even when the browser supplies no Content-Length.
    let body;
    if (request.method === 'POST') {
      const reader = request.body?.getReader();
      const chunks = [];
      let size = 0;
      if (reader) {
        while (true) {
          const { value, done } = await reader.read();
          if (done) break;
          size += value.byteLength;
          if (size > bodyLimit) { await reader.cancel(); return failure(413, 'Request too large'); }
          chunks.push(value);
        }
      }
      body = new Uint8Array(size);
      let offset = 0;
      for (const chunk of chunks) { body.set(chunk, offset); offset += chunk.byteLength; }
    }
    const upstream = await fetchImpl(target.href, {
      method: request.method, headers: forwardHeaders, body,
      redirect: 'manual', signal: AbortSignal.timeout(20000)
    });
    const resultHeaders = new Headers(headers);
    for (const key of ['content-type', 'location', 'set-cookie']) {
      // Workers uses getAll('Set-Cookie'); Node uses getSetCookie(). Never fold cookies.
      if (key === 'set-cookie') {
        const cookies = typeof upstream.headers.getAll === 'function' ? upstream.headers.getAll('Set-Cookie')
          : typeof upstream.headers.getSetCookie === 'function' ? upstream.headers.getSetCookie() : [];
        for (const value of cookies) resultHeaders.append(key, value);
      } else if (upstream.headers.has(key)) resultHeaders.set(key, upstream.headers.get(key));
    }
    return new Response(upstream.body, { status: upstream.status, headers: resultHeaders });
  } catch (_) { return failure(502, 'TAGGY is offline or the backend could not be reached.'); }
}
export default { fetch(request, env) { return handleRequest(request, env); } };
