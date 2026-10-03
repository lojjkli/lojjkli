'use strict';
const $ = id => document.getElementById(id);
let csrf = '';
let selected = '';
let active = false;
let busy = false;
let dirty = false;
let guilds = [];
const showStatus = (text, type = '') => { $('status').textContent = text; $('status').className = `notice ${type}`; };

async function api(path, body) {
  const response = await fetch(`/taggy/api/${path}`, {
    method: body === undefined ? 'GET' : 'POST', credentials: 'same-origin', cache: 'no-store',
    headers: body === undefined ? {} : { 'Content-Type': 'application/json', 'X-CSRF-Token': csrf },
    body: body === undefined ? undefined : JSON.stringify(body)
  });
  let data;
  try { data = await response.json(); } catch (_) { throw new Error('The dashboard could not reach TAGGY.'); }
  if (response.status === 401) {
    active = false; csrf = ''; selected = '';
    $('dashboard').hidden = true; $('logout').hidden = true; $('login').hidden = false;
    throw new Error('Sign in with your owner Discord account to continue.');
  }
  if (!response.ok) throw new Error(data.error || `Request failed (${response.status})`);
  return data;
}
function textElement(tag, text, className) {
  const element = document.createElement(tag);
  element.textContent = text;
  if (className) element.className = className;
  return element;
}
function renderList() {
  $('servers').replaceChildren();
  for (const guild of guilds) {
    const button = textElement('button', guild.name);
    button.type = 'button'; button.setAttribute('aria-current', String(guild.id === selected));
    button.append(textElement('small', `${guild.memberCount.toLocaleString()} members · ${guild.enabled ? 'Protected' : 'Paused'}`));
    button.addEventListener('click', async () => {
      if (busy || (dirty && !confirm('Discard unsaved settings and switch servers?'))) return;
      dirty = false; selected = guild.id; renderList();
      try { await loadDetail(true); } catch (error) { showStatus(error.message, 'error'); }
    });
    $('servers').append(button);
  }
}
function renderDetail(data, settings) {
  $('detail').hidden = false;
  $('server-name').textContent = data.name;
  $('server-meta').textContent = `${data.memberCount.toLocaleString()} members · ${data.id}`;
  $('protection-status').textContent = data.config.enabled ? 'Protection active' : 'Protection paused';
  $('protection-status').className = `pill ${data.config.enabled ? '' : 'off'}`;
  const missing = Object.entries(data.permissions).filter(([, value]) => !value).map(([key]) => ({
    moderateMembers: 'Moderate Members', manageMessages: 'Manage Messages', manageRoles: 'Manage Roles', viewAuditLog: 'View Audit Log'
  })[key]);
  const warnings = [];
  if (missing.length) warnings.push(`Missing bot permissions: ${missing.join(', ')}. Some responses will fail. Keep TAGGY’s role above members it needs to manage.`);
  if (data.storageError) warnings.push('Security state could not be saved. Check the bot host storage before relying on incident history.');
  $('permissions').hidden = !warnings.length; $('permissions').textContent = warnings.join(' '); $('permissions').className = 'notice error';
  const shield = data.shieldUntil > Date.now();
  $('shield-title').textContent = shield ? 'Join shield is active' : 'Monitoring new joins';
  $('shield-copy').textContent = shield
    ? `Active until ${new Date(data.shieldUntil).toLocaleTimeString()}. New non-staff members receive a temporary timeout.`
    : `${data.config.joinLimit} joins within ${data.config.joinWindowSeconds} seconds activates a ${data.config.shieldMinutes}-minute shield.`;
  if (!data.config.enabled || !data.config.antiRaid) $('shield-copy').textContent += ' Join protection is paused; shield enforcement is currently disabled.';
  if (settings) {
    for (const [key, value] of Object.entries(data.config)) {
      const input = $('settings-form').elements.namedItem(key);
      if (!input) continue;
      if (input.type === 'checkbox') input.checked = value; else input.value = value;
    }
    dirty = false;
  }
  $('incidents').replaceChildren();
  if (!data.incidents.length) $('incidents').append(textElement('p', 'No incidents recorded for this server yet.', 'muted'));
  for (const incident of data.incidents) {
    const row = textElement('article', '', 'incident');
    const time = textElement('time', new Date(incident.at).toLocaleString());
    time.dateTime = new Date(incident.at).toISOString();
    const content = document.createElement('div');
    content.append(textElement('strong', incident.type), textElement('p', incident.detail), textElement('p', incident.outcome, 'outcome'));
    if (incident.actorId) content.append(textElement('p', `Account: ${incident.actorId}`));
    row.append(time, content); $('incidents').append(row);
  }
}
async function loadDetail(settings = false) {
  const id = selected;
  if (!id) { $('detail').hidden = true; return; }
  const data = await api(`guilds/${id}`);
  if (selected === id) renderDetail(data, settings);
}
async function loadList() {
  const data = await api('guilds'); guilds = data.guilds;
  $('empty').hidden = guilds.length > 0;
  if (!guilds.some(guild => guild.id === selected)) { selected = guilds[0]?.id || ''; dirty = false; }
  renderList(); await loadDetail(!dirty);
}
async function action(path, body, message) {
  if (busy) return;
  busy = true;
  const controls = [...document.querySelectorAll('#dashboard button, #dashboard input, #logout')];
  controls.forEach(control => { control.disabled = true; });
  try {
    await api(path, body); showStatus(message, 'success'); await loadList();
  } catch (error) { showStatus(error.message, 'error'); }
  finally { busy = false; controls.forEach(control => { control.disabled = false; }); }
}
$('settings-form').addEventListener('input', () => { dirty = true; });
$('settings-form').addEventListener('submit', async event => {
  event.preventDefault();
  const body = {};
  for (const input of $('settings-form').elements) if (input.name) body[input.name] = input.type === 'checkbox' ? input.checked : Number(input.value);
  await action(`guilds/${selected}/settings`, body, 'Protection settings saved.');
  if ($('status').classList.contains('success')) { dirty = false; await loadDetail(true); }
});
$('shield-on').addEventListener('click', () => {
  if (!confirm('Activate join shield for this server? Incoming non-staff members will receive a timeout.')) return;
  void action(`guilds/${selected}/shield`, { active: true }, 'Join shield activated.');
});
$('shield-off').addEventListener('click', () => { void action(`guilds/${selected}/shield`, { active: false }, 'Join shield ended. Existing timeouts are unchanged.'); });
$('release-form').addEventListener('submit', event => {
  event.preventDefault(); const memberId = $('member-id').value.trim();
  if (!confirm(`Release the timeout for member ${memberId} in ${$('server-name').textContent}?`)) return;
  void action(`guilds/${selected}/release-timeout`, { memberId }, 'Member timeout released.');
});
$('refresh').addEventListener('click', () => { if (!busy) void loadList().catch(error => showStatus(error.message, 'error')); });
$('logout').addEventListener('click', async () => {
  try { await api('logout', {}); location.assign('/taggy/'); }
  catch (error) { showStatus(error.message, 'error'); }
});
window.addEventListener('beforeunload', event => { if (dirty) { event.preventDefault(); event.returnValue = ''; } });
async function start() {
  try {
    const session = await api('session'); csrf = session.csrf; active = true;
    $('login').hidden = true; $('dashboard').hidden = false; $('logout').hidden = false;
    await loadList(); showStatus('Signed in as owner. Server data is live.', 'success');
  } catch (error) { showStatus(error.message, 'error'); }
}
setInterval(() => {
  if (active && !busy && !document.hidden) void loadDetail(false).catch(error => showStatus(error.message, 'error'));
}, 15000);
void start();
