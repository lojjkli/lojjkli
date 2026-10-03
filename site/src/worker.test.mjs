import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
const source = readFileSync(new URL('./worker.js', import.meta.url), 'utf8');
const { handleRequest, default: worker } = await import(`data:text/javascript;base64,${Buffer.from(source).toString('base64')}`);
const env = { TAGGY_BACKEND_URL: 'https://bot.example', TAGGY_PROXY_SECRET: 'a'.repeat(40),
  ASSETS: { fetch: () => new Response('public assets') } };

test('regular site requests still serve existing static assets', async () => {
  const response = await worker.fetch(new Request('https://lojjkli.site/admin/'), env, {});
  assert.equal(await response.text(), 'public assets');
});
test('proxy is fixed to configured backend and strips caller credentials', async () => {
  let captured;
  const response = await handleRequest(new Request('https://lojjkli.site/taggy/api/guilds?test=1', {
    headers: { 'x-taggy-proxy-secret': 'attacker', Authorization: 'Bearer attacker', Cookie: '__Host-taggy_session=test', 'CF-Connecting-IP': '192.0.2.1' }
  }), env, async (url, options) => {
    captured = { url, options };
    return new Response('{"guilds":[]}', { headers: { 'content-type': 'application/json', 'set-cookie': '__Host-taggy_session=test; Secure; HttpOnly; Path=/' } });
  });
  assert.equal(captured.url, 'https://bot.example/taggy/api/guilds?test=1');
  assert.equal(captured.options.headers.get('x-taggy-proxy-secret'), env.TAGGY_PROXY_SECRET);
  assert.equal(captured.options.headers.has('authorization'), false);
  assert.equal(response.headers.has('x-taggy-proxy-secret'), false);
  assert.equal(response.headers.get('cache-control'), 'no-store');
  assert.match(response.headers.get('set-cookie'), /HttpOnly/);
});
test('cross-origin writes and noncanonical hosts fail before forwarding', async () => {
  const noFetch = () => { throw new Error('Must not forward'); };
  assert.equal((await handleRequest(new Request('https://lojjkli.site/taggy/api/logout', { method: 'POST', headers: { origin: 'https://evil.example' } }), env, noFetch)).status, 403);
  assert.equal((await handleRequest(new Request('https://www.lojjkli.site/taggy/api/session'), env, noFetch)).status, 403);
});
test('oversized untrusted bodies and invalid backend configuration are denied', async () => {
  const response = await handleRequest(new Request('https://lojjkli.site/taggy/api/guilds/100/settings', {
    method: 'POST', headers: { origin: 'https://lojjkli.site' }, body: 'x'.repeat(70000)
  }), env, () => { throw new Error('Must not forward'); });
  assert.equal(response.status, 413);
  assert.equal((await handleRequest(new Request('https://lojjkli.site/taggy/api/session'), { ...env, TAGGY_BACKEND_URL: 'http://bot.example' })).status, 503);
});
test('OAuth redirect stays a redirect and both cookies survive proxying', async () => {
  const response = await handleRequest(new Request('https://lojjkli.site/taggy/auth/callback?code=one'), env, async (url, options) => {
    assert.equal(options.redirect, 'manual');
    const headers = new Headers({ location: '/taggy/' });
    headers.append('set-cookie', '__Host-taggy_oauth=; Path=/; Secure; Max-Age=0');
    headers.append('set-cookie', '__Host-taggy_session=session; Path=/; Secure; HttpOnly');
    return new Response(null, { status: 302, headers });
  });
  assert.equal(response.status, 302);
  assert.equal(response.headers.get('location'), '/taggy/');
  assert.equal(response.headers.getSetCookie().length, 2);
});
test('upstream failures do not leak secret values or provider responses', async () => {
  const response = await handleRequest(new Request('https://lojjkli.site/taggy/api/session'), env, () => { throw new Error(env.TAGGY_PROXY_SECRET); });
  assert.equal(response.status, 502);
  assert.equal((await response.text()).includes(env.TAGGY_PROXY_SECRET), false);
});
test('Workers-specific getAll preserves both login cookies', async () => {
  const response = await handleRequest(new Request('https://lojjkli.site/taggy/auth/callback'), env, async () => {
    const upstream = new Response(null, { status: 302, headers: { location: '/taggy/' } });
    upstream.headers.getAll = name => {
      assert.equal(name, 'Set-Cookie');
      return ['__Host-taggy_oauth=; Path=/; Secure; Max-Age=0', '__Host-taggy_session=s; Path=/; Secure; HttpOnly'];
    };
    return upstream;
  });
  assert.equal(response.headers.getSetCookie().length, 2);
});
