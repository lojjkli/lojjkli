'use strict';
const $ = id => document.getElementById(id);
let csrf = '';
let isSpecialOwner = false;
let priorityGuild = '';
let selected = '';
let active = false;
let busy = false;
let dirty = false;
const dirtyForms = new Set();
function clearDraft(form) { dirtyForms.delete(form); dirty = dirtyForms.size > 0; }
function discardDrafts() { dirtyForms.clear(); dirty = false; }
let guilds = [];
let currentTab = 'security';
let logRows = [];
let dmUser = '';
let channelLoading = '';
let displayedChannel = '';
let dmLoading = false;
let resourcesFor = '';
let resources = null;
let lookedUpMember = '';
let resourceRequest = null;
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
    active = false; csrf = ''; selected = ''; isSpecialOwner = false; resources = null; dmUser = '';
    $('dm-messages').replaceChildren(); $('dm-threads').replaceChildren(); $('channel-messages').replaceChildren(); $('incidents').replaceChildren();
    document.body.classList.remove('signed-in'); $('account-name').hidden = true;
    $('dashboard').hidden = true; $('logout').hidden = true; $('login').hidden = false;
    throw new Error('Sign in with Discord to continue.');
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
    const button = textElement('button', '');
    button.title = guild.name; button.setAttribute('aria-label', guild.name);
    let iconUrl = null;
    try { const url = new URL(guild.iconUrl); if (url.protocol === 'https:' && url.hostname === 'cdn.discordapp.com' && url.pathname.startsWith(`/icons/${guild.id}/`)) iconUrl = url.href; } catch (_) {}
    if (iconUrl) { const img = document.createElement('img'); img.src = iconUrl; img.alt = ''; img.className = 'server-icon'; img.addEventListener('error', () => img.replaceWith(textElement('span', guild.name.slice(0,2).toUpperCase(), 'server-initials'))); button.append(img); }
    else button.append(textElement('span', guild.name.slice(0,2).toUpperCase(), 'server-initials'));
    button.type = 'button'; button.setAttribute('aria-current', String(guild.id === selected));

    button.addEventListener('click', async () => {
      if (busy || (dirty && !confirm('Discard unsaved settings and switch servers?'))) return;
      discardDrafts(); selected = guild.id; resourcesFor = ''; lookedUpMember = ''; $('member-result').textContent = 'Look up a member to review their roles.'; $('embed-form').reset(); previewEmbed(); renderList();
      $('channel-messages').replaceChildren(); $('chat-content').value = '';
      try { await loadDetail(true); await refreshCurrentTab(); } catch (error) { showStatus(error.message, 'error'); }
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
  }
  logRows = data.incidents; renderLogs();
}
async function loadDetail(settings = false) {
  const id = selected;
  if (!id) { $('detail').hidden = !isSpecialOwner; $('server-name').textContent = 'No servers yet'; return; }
  const data = await api(`guilds/${id}`);
  if (selected === id) { renderDetail(data, settings); if (resourcesFor !== id) await loadResources(); }
}
async function loadList() {
  const data = await api(isSpecialOwner ? 'owner/guilds' : 'guilds'); guilds = data.guilds;
  $('empty').hidden = guilds.length > 0;
  if (!guilds.some(guild => guild.id === selected)) { selected = guilds[0]?.id || ''; discardDrafts(); }
  renderList(); await loadDetail(!dirty);
  if (isSpecialOwner) { $('owner-summary').textContent = `${guilds.length} connected servers · ${guilds.filter(guild => guild.enabled).length} protected · ${guilds.filter(guild => guild.shieldUntil > Date.now()).length} active shields`; $('priority-server').disabled = !guilds.some(guild => guild.id === priorityGuild); }
}
async function action(path, body, message) {
  if (busy) return;
  busy = true;
  const controls = [...document.querySelectorAll('#dashboard button, #dashboard input, #dashboard select, #dashboard textarea, #logout')];
  const previousDisabled = controls.map(control => control.disabled);
  controls.forEach(control => { control.disabled = true; });
  try {
    const result = await api(path, body); showStatus(message, 'success');
    try { await loadList(); } catch(error) { showStatus(`Action completed. Refresh failed: ${error.message}`, 'error'); }
    return result;
  } catch (error) { showStatus(error.message, 'error'); }
  finally { busy = false; controls.forEach((control,index) => { control.disabled = previousDisabled[index]; }); applyCapabilities(); }
}
$('detail').addEventListener('input', event => { const form = event.target.closest('form'); if (form) { dirtyForms.add(form.id); dirty = true; } });
$('settings-form').addEventListener('submit', async event => {
  event.preventDefault();
  const body = {};
  for (const input of $('settings-form').elements) if (input.name) body[input.name] = input.type === 'checkbox' ? input.checked : Number(input.value);
  await action(`guilds/${selected}/settings`, body, 'Protection settings saved.');
  if ($('status').classList.contains('success')) { clearDraft('settings-form'); await loadDetail(true); }
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
    const session = await api('session'); csrf = session.csrf; active = true; isSpecialOwner = session.isOwner === true; priorityGuild = session.priorityGuildId || '';
    $('owner-console').hidden = !isSpecialOwner; $('console-label').textContent = isSpecialOwner ? 'OWNER CONSOLE' : 'SERVER DASHBOARD';
    $('scope-note').textContent = isSpecialOwner ? 'Every connected server. Your main server first.' : 'Your servers. Your controls.';
    document.body.classList.add('signed-in'); $('account-name').hidden = false; $('account-name').textContent = session.username || session.userId; $('dm-tab').hidden = !isSpecialOwner;
    $('login').hidden = true; $('dashboard').hidden = false; $('logout').hidden = false;
    await loadList(); showStatus(isSpecialOwner ? 'Your servers are ready.' : 'Pick a server to get started.', 'success');
  } catch (error) { showStatus(error.message, 'error'); }
}
setInterval(() => {
  if (active && !busy && !document.hidden) void refreshCurrentTab().catch(error => showStatus(error.message, 'error'));
}, 15000);
void start();

const roleKeys = ['member', 'unverified', 'owner', 'admin', 'moderator', 'helper', 'builder'];
for (const key of roleKeys) {
  const label = textElement('label', key[0].toUpperCase() + key.slice(1));
  const select = document.createElement('select'); select.id = `binding-${key}`; label.append(select); $('role-bindings').append(label);
}
function options(element, items, blank = 'Disabled') {
  element.replaceChildren(); const empty = textElement('option', blank); empty.value = ''; element.append(empty);
  for (const item of items) { const option = textElement('option', item.name); option.value = item.id; element.append(option); }
}
async function loadResources() {
  const guildId = selected;
  // A new server can supersede an older in-flight resource request.
  if (resourceRequest?.guildId === guildId) return resourceRequest.promise;
  const promise = (async () => {
    const data = await api(`guilds/${guildId}/resources`);
    if (selected !== guildId) return;
    resources = data; resourcesFor = guildId;
    for (const key of roleKeys) { options($(`binding-${key}`), data.roles, 'Existing default'); $(`binding-${key}`).value = data.bindings[key] || ''; }
    options($('chat-channel'), data.channels.filter(channel => channel.canRead || channel.canSend), 'Choose channel');
    for (const name of ['embed-channel', 'control-channel', 'welcome-channel', 'log-channel']) options($(name), data.channels, name.includes('welcome') || name === 'log-channel' ? 'Disabled' : 'Choose channel');
    options($('assign-role'), data.roles, 'Choose role'); options($('auto-role'), data.roles.filter(role => role.editable), 'Disabled');
    $('welcome-channel').value = data.welcome.channelId || ''; $('log-channel').value = data.welcome.logChannelId || '';
    $('auto-role').value = data.welcome.autoRoleId || ''; $('welcome-message').value = data.welcome.message || ''; applyCapabilities();
  })();
  resourceRequest = { guildId, promise };
  try { await promise; } finally { if (resourceRequest?.promise === promise) resourceRequest = null; }
}
for (const button of document.querySelectorAll('[data-tab]')) button.addEventListener('click', () => {
  if (button.dataset.tab === 'dms' && !isSpecialOwner) return;
  currentTab = button.dataset.tab;
  for (const tab of document.querySelectorAll('[data-tab]')) tab.setAttribute('aria-pressed', String(tab === button));
  for (const panel of document.querySelectorAll('[data-panel]')) panel.hidden = panel.dataset.panel !== button.dataset.tab;
  void refreshCurrentTab().catch(error => showStatus(error.message, 'error'));
});
$('roles-form').addEventListener('submit', async event => {
  event.preventDefault(); const body = Object.fromEntries(roleKeys.map(key => [key, $(`binding-${key}`).value]));
  if (body.owner !== (resources?.bindings.owner || '') && !confirm('Change the Owner role? Members with this role will gain owner bot commands in this server.')) return;
  const result = await action(`guilds/${selected}/roles`, body, 'Server roles saved.');
  if (result) { resources.bindings = body; clearDraft('roles-form'); }
});
$('lookup-form').addEventListener('submit', async event => {
  event.preventDefault(); lookedUpMember = ''; const guildId = selected;
  try {
    const data = await api(`guilds/${guildId}/member?memberId=${encodeURIComponent($('lookup-id').value.trim())}`);
    if (guildId !== selected) return;
    lookedUpMember = data.id;
    const names = data.roles.map(id => resources.roles.find(role => role.id === id)?.name || id);
    $('member-result').textContent = `${data.username} · ${names.join(', ') || 'No roles'}${data.manageable ? '' : ' · Above TAGGY’s role hierarchy'}`;
  } catch (error) { showStatus(error.message, 'error'); }
});
$('member-role-form').addEventListener('submit', async event => {
  event.preventDefault(); if (!lookedUpMember) { showStatus('Find a member first.', 'error'); return; }
  const operation = event.submitter.value;
  if (!confirm(`${operation === 'add' ? 'Add' : 'Remove'} this role for member ${lookedUpMember}?`)) return;
  const result = await action(`guilds/${selected}/member-role`, { memberId: lookedUpMember, roleId: $('assign-role').value, operation }, 'Member role updated.');
  if (result) $('lookup-form').requestSubmit();
});
function embedBody() {
  const embed = Object.fromEntries(['title', 'description', 'color', 'url', 'image', 'thumbnail', 'footer'].map(key => [key, $(`embed-${key}`).value]));
  embed.fields = JSON.parse($('embed-fields').value || '[]');
  return { channelId: $('embed-channel').value, messageId: $('embed-id').value.trim(), content: $('embed-content').value, embed };
}
function previewEmbed() {
  $('preview-title').textContent = $('embed-title').value || 'Your title'; $('preview-description').textContent = $('embed-description').value || 'Your message, styled your way.';
  $('preview-footer').textContent = $('embed-footer').value; $('embed-preview').style.borderLeftColor = $('embed-color').value;
  $('preview-fields').replaceChildren();
  try { const fields = JSON.parse($('embed-fields').value || '[]'); if (Array.isArray(fields)) for (const field of fields.slice(0, 25)) { const div = document.createElement('div'); div.append(textElement('strong', String(field.name || '')), textElement('p', String(field.value || ''))); $('preview-fields').append(div); } } catch (_) { $('preview-fields').append(textElement('small', 'Fields must be a valid JSON array.')); }
}
$('embed-form').addEventListener('input', previewEmbed);
$('load-embed').addEventListener('click', async () => {
  const guildId = selected;
  try {
    if (!$('embed-id').value || !$('embed-channel').value) throw new Error('Choose a channel and paste a message ID first.');
    const data = await api(`guilds/${guildId}/message?channelId=${encodeURIComponent($('embed-channel').value)}&messageId=${encodeURIComponent($('embed-id').value.trim())}`);
    if (guildId !== selected) return;
    const embed = data.embeds[0] || {}; $('embed-content').value = data.content || '';
    for (const key of ['title', 'description', 'url']) $(`embed-${key}`).value = embed[key] || '';
    $('embed-color').value = '#' + (embed.color ?? 0xbe8bff).toString(16).padStart(6, '0');
    $('embed-image').value = embed.image?.url || ''; $('embed-thumbnail').value = embed.thumbnail?.url || '';
    $('embed-footer').value = embed.footer?.text || ''; $('embed-fields').value = JSON.stringify(embed.fields || [], null, 2);
    dirtyForms.add('embed-form'); dirty = true; previewEmbed(); showStatus('Message loaded. Publishing will replace its embeds with your edited version.');
  } catch (error) { showStatus(error.message, 'error'); }
});
$('embed-form').addEventListener('submit', async event => {
  event.preventDefault(); let body;
  try { body = embedBody(); } catch (_) { showStatus('Fields must be valid JSON.', 'error'); return; }
  if (!confirm(body.messageId ? 'Replace the embeds on this TAGGY message?' : 'Publish this embed to the selected channel?')) return;
  const result = await action(`guilds/${selected}/embed`, body, 'Embed published.');
  if (result) { clearDraft('embed-form'); $('embed-id').value = result.messageId; const link = textElement('a', 'Open message in Discord'); const url = new URL(result.url); if (url.origin === 'https://discord.com') { link.href = url.href; link.target = '_blank'; link.rel = 'noopener noreferrer'; $('embed-result').replaceChildren(link); } }
});
$('channel-form').addEventListener('submit', event => {
  event.preventDefault(); const operation = event.submitter.value;
  if (operation !== 'slowmode' && !confirm(`${operation === 'lock' ? 'Lock' : 'Restore'} the selected channel’s @everyone Send Messages permission?`)) return;
  void action(`guilds/${selected}/channel`, { channelId: $('control-channel').value, operation, seconds: Number($('slowmode').value) }, 'Channel settings updated.');
});
$('control-channel').addEventListener('change', () => { $('slowmode').value = resources?.channels.find(item => item.id === $('control-channel').value)?.slowmode || 0; });
$('welcome-form').addEventListener('submit', async event => {
  event.preventDefault(); const body = { channelId: $('welcome-channel').value, autoRoleId: $('auto-role').value, logChannelId: $('log-channel').value, message: $('welcome-message').value };
  const result = await action(`guilds/${selected}/welcome`, body, 'Welcome and logging settings saved.'); if (result) { resources.welcome = body; clearDraft('welcome-form'); }
});
previewEmbed();

$('priority-server').addEventListener('click', async () => {
  if (busy || !priorityGuild || (dirty && !confirm('Discard unsaved drafts and open your main server?'))) return;
  selected = priorityGuild; resourcesFor = ''; discardDrafts(); lookedUpMember = ''; $('embed-form').reset(); previewEmbed(); renderList();
  try { await loadDetail(true); } catch (error) { showStatus(error.message, 'error'); }
});

function renderLogs() {
  $('incidents').replaceChildren(); const query = $('log-search').value.toLowerCase();
  const rows = logRows.filter(row => [row.type,row.actorId,row.detail,row.outcome].join(' ').toLowerCase().includes(query));
  if (!rows.length) $('incidents').append(textElement('p','No matching logs.','muted'));
  for (const row of rows) { const item = textElement('article','','incident'); const time = textElement('time',new Date(row.at).toLocaleString()); const content = document.createElement('div'); content.append(textElement('strong',row.type),textElement('p',row.detail),textElement('p',row.outcome,'outcome')); if(row.actorId) content.append(textElement('small',`Account: ${row.actorId}`)); item.append(time,content); $('incidents').append(item); }
}
async function loadLogs() { const id = selected; if(!id)return; const data=await api(`guilds/${id}/logs`); if(selected===id){logRows=data.logs;renderLogs();} }
function renderMessages(element,messages) {
  const nearBottom = element.scrollHeight-element.scrollTop-element.clientHeight<60; element.replaceChildren();
  if(!messages.length) element.append(textElement('p','No messages yet.','muted'));
  for(const message of messages){const row=textElement('article','',`chat-message ${message.direction==='outgoing'?'outgoing':''}`);row.append(textElement('strong',`${message.author}${message.bot?' · bot':''}`),textElement('time',new Date(message.at).toLocaleString()),textElement('p',message.content||'(attachment)')); for(const attachment of message.attachments||[]){try{const url=new URL(attachment.url);if(url.protocol!=='https:'||!['cdn.discordapp.com','media.discordapp.net'].includes(url.hostname))continue;const link=textElement('a',attachment.name||'Attachment');link.href=url.href;link.target='_blank';link.rel='noopener noreferrer';row.append(link);}catch(_){}} element.append(row);}
  if(nearBottom) element.scrollTop=element.scrollHeight;
}
async function loadChat() {
  const guildId=selected,channelId=$('chat-channel').value; const key=`${guildId}/${channelId}`; if(!guildId||!channelId||channelLoading===key)return; displayedChannel=channelId;
  const capability=resources?.channels.find(channel=>channel.id===channelId);$('chat-access').textContent=capability?.canSend?'Messages are sent by TAGGY.':'You can read this channel. Sending is unavailable.';
  if(!capability?.canRead){$('channel-messages').replaceChildren(textElement('p','Message history is unavailable in this channel.','muted'));return;}
  channelLoading=key;
  try{const data=await api(`guilds/${guildId}/messages?channelId=${encodeURIComponent(channelId)}`);if(selected===guildId&&$('chat-channel').value===channelId)renderMessages($('channel-messages'),data.messages);}
  finally{if(channelLoading===key)channelLoading='';}
}
async function loadDMs() {
  if(!isSpecialOwner||dmLoading)return;dmLoading=true;
  try{const data=await api('owner/dms');$('dm-threads').replaceChildren(); if(data.storageError)showStatus('The inbox could not be saved. Check bot storage.','error'); for(const thread of data.threads){const button=textElement('button',thread.name);button.type='button';button.append(textElement('small',thread.preview.slice(0,70)));button.addEventListener('click',()=>selectDM(thread.id));$('dm-threads').append(button);}if(dmUser)await loadDMHistory();}
  finally{dmLoading=false;}
}
async function loadDMHistory(){if(!isSpecialOwner||!dmUser)return;const user=dmUser;const data=await api(`owner/dms?userId=${encodeURIComponent(user)}`);if(user===dmUser)renderMessages($('dm-messages'),data.messages);}
async function refreshCurrentTab(){if(currentTab==='dms')return loadDMs();if(!selected)return;if(currentTab==='logs')return loadLogs();if(currentTab==='chat')return loadChat();return loadDetail(false);}
$('log-search').addEventListener('input',renderLogs);
$('refresh-logs').addEventListener('click',()=>void loadLogs().catch(error=>showStatus(error.message,'error')));
$('refresh-chat').addEventListener('click',()=>void loadChat().catch(error=>showStatus(error.message,'error')));
$('chat-channel').addEventListener('change',()=>{if($('chat-content').value.trim()&&!confirm('Discard this draft and switch channels?')){$('chat-channel').value=displayedChannel;return;}$('chat-content').value='';clearDraft('chat-form');$('channel-messages').replaceChildren();void loadChat().catch(error=>showStatus(error.message,'error'));});
$('chat-form').addEventListener('submit',async event=>{event.preventDefault();if(!resources?.channels.find(channel=>channel.id===$('chat-channel').value)?.canSend){showStatus('You cannot send to this channel.','error');return;}const result=await action(`guilds/${selected}/chat`,{channelId:$('chat-channel').value,content:$('chat-content').value},'Message sent.');if(result){$('chat-content').value='';clearDraft('chat-form');await loadChat().catch(error=>showStatus(`Message sent. Refresh failed: ${error.message}`,'error'));}});
$('dm-open-form').addEventListener('submit',event=>{event.preventDefault();selectDM($('dm-user-id').value.trim());});
$('refresh-dms').addEventListener('click',()=>void loadDMs().catch(error=>showStatus(error.message,'error')));
$('dm-form').addEventListener('submit',async event=>{event.preventDefault();if(!isSpecialOwner||!dmUser){showStatus('Open a conversation first.','error');return;}const result=await action('owner/dms',{userId:dmUser,content:$('dm-content').value},'DM sent.');if(result){$('dm-content').value='';clearDraft('dm-form');if(result.warning)showStatus(result.warning,'error');await loadDMs().catch(error=>showStatus(`DM sent. Refresh failed: ${error.message}`,'error'));}});

function selectDM(userId){if(dmUser!==userId&&$('dm-content').value.trim()&&!confirm('Discard this draft and switch conversations?')){$('dm-user-id').value=dmUser;return;}if(dmUser!==userId){$('dm-content').value='';clearDraft('dm-form');}dmUser=userId;$('dm-user-id').value=userId;void loadDMHistory().catch(error=>showStatus(error.message,'error'));}
function applyCapabilities(){if(!resources||busy)return;const cap=resources.capabilities||{};for(const [selector,key]of [['#roles-form button,#roles-form select','changeRoles'],['#member-role-form button,#assign-role','assignRoles'],['#channel-form button,#control-channel,#slowmode','channels'],['#release-form button,#member-id','timeout'],['#auto-role','autoRole']]){for(const control of document.querySelectorAll(selector))control.disabled=cap[key]===false;} }
