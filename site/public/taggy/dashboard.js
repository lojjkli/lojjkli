'use strict';
const $ = id => document.getElementById(id);
let csrf = '';
let isSpecialOwner = false;
let priorityGuild = '';
let selected = new URL(location.href).searchParams.get('server') || '';
function switchServer(id) {
  if (busy || (dirty && !confirm('Leave without saving your changes?'))) return;
  discardDrafts();
  const url = new URL(location.href); url.searchParams.set('server', id);
  location.assign(url.href);
}
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
let dmRows = []; let dmBefore = null; let dmHistoryLoading = ''; let dmThreads = [];
function avatar(user, className='dm-avatar') {
 const fallback=textElement('span',(user.name||user.author||'?').slice(0,2).toUpperCase(),className+' avatar-fallback');
 try { const url=new URL(user.avatarUrl); if(url.protocol!=='https:'||url.hostname!=='cdn.discordapp.com')return fallback;const img=document.createElement('img');img.src=url.href;img.alt='';img.className=className;img.addEventListener('error',()=>img.replaceWith(fallback));return img; } catch(_){return fallback;}
}

let resourcesFor = '';
let resources = null;
let verificationLoaded='';
function verificationVisibility(){const roblox=$('verification-mode').value==='roblox';$('verification-roblox').hidden=!roblox;$('verification-group-label').hidden=!roblox||!$('verification-group-required').checked;$('verification-group').required=roblox&&$('verification-group-required').checked;}
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
    dmRows=[];dmThreads=[];dmBefore=null;$('dm-profile').replaceChildren();$('dm-chat-header').replaceChildren();$('dm-messages').replaceChildren(); $('dm-threads').replaceChildren(); $('channel-messages').replaceChildren(); $('incidents').replaceChildren();
    $('header-login').hidden = false; document.body.classList.remove('signed-in'); $('account-name').hidden = true;
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

    button.addEventListener('click', () => switchServer(guild.id));
    $('servers').append(button);
  }
}
function renderDetail(data, settings) {
  $('detail').hidden = false;
  applyTabState();
  $('server-name').textContent = data.name;
  $('server-meta').textContent = `${data.memberCount.toLocaleString()} members`;
  $('protection-status').textContent = data.config.enabled ? 'Protection active' : 'Protection paused';
  $('protection-status').className = `pill ${data.config.enabled ? '' : 'off'}`;
  const missing = Object.entries(data.permissions).filter(([, value]) => !value).map(([key]) => ({
    moderateMembers: 'Moderate Members', manageMessages: 'Manage Messages', manageRoles: 'Manage Roles', viewAuditLog: 'View Audit Log'
  })[key]);
  const warnings = [];
  if (missing.length) warnings.push(`Missing bot permissions: ${missing.join(', ')}. Some responses will fail. Keep TAGGY’s role above members it needs to manage.`);
  if (data.storageError) warnings.push('Security state could not be saved. Check the bot host storage before relying on incident history.');
  $('permissions').hidden = !warnings.length; $('permissions').textContent = warnings.join(' '); $('permissions').className = 'notice error';
  const fullyAutomatic = data.config.enabled && data.config.antiRaid && data.config.antiSpam && data.config.antiNuke;
  $('automatic-title').textContent = fullyAutomatic ? 'Automatic protection is on' : 'Some protection is paused';
  $('automatic-copy').textContent = fullyAutomatic ? 'TAGGY checks new joins, spam and destructive changes automatically. It restricts suspicious activity and alerts the bot owner, even when this page is closed.' : 'Turn on automatic protection to let TAGGY handle join raids, spam and destructive changes. You can tune individual checks under Advanced.';
  $('automatic-on').hidden = fullyAutomatic;
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
    $('header-login').hidden = true; document.body.classList.add('signed-in'); $('account-name').hidden = false; $('account-name').textContent = session.username || session.userId; $('dm-tab').hidden = !isSpecialOwner;
    $('login').hidden = true; $('dashboard').hidden = false; $('logout').hidden = false;
    await loadList(); showStatus(isSpecialOwner ? 'Your servers are ready.' : 'Pick a server to get started.', 'success');
  } catch (error) { if (error.message === 'Sign in with Discord to continue.') { showStatus(''); } else { showStatus(error.message, 'error'); $('login').hidden = false; } }
}
setInterval(() => {
  if (active && !busy && !document.hidden) void refreshCurrentTab().catch(error => showStatus(error.message, 'error'));
}, 15000);
void start();

$('automatic-on').addEventListener('click', () => { void action(`guilds/${selected}/settings`, { enabled:true, antiRaid:true, antiSpam:true, antiNuke:true }, 'Automatic protection is on.'); });

const roleKeys = ['member', 'unverified', 'owner', 'admin', 'moderator', 'helper', 'builder'];
const extraRoles = document.createElement('details'); extraRoles.className = 'advanced';
extraRoles.append(textElement('summary', 'More command roles'));
const extraRoleFields = document.createElement('div'); extraRoleFields.className = 'thresholds'; extraRoles.append(extraRoleFields);
$('role-bindings').after(extraRoles);
for (const key of roleKeys) {
  const label = textElement('label', key[0].toUpperCase() + key.slice(1));
  const select = document.createElement('select'); select.id = `binding-${key}`; label.append(select); (['member','unverified','owner'].includes(key) ? $('role-bindings') : extraRoleFields).append(label);
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
    options($('verification-channel'), data.channels, 'Create or reuse verification channel');
    options($('assign-role'), data.roles, 'Choose role'); options($('auto-role'), data.roles.filter(role => role.editable), 'Disabled');
    $('welcome-channel').value = data.welcome.channelId || ''; $('log-channel').value = data.welcome.logChannelId || '';
    $('auto-role').value = data.welcome.autoRoleId || ''; $('welcome-message').value = data.welcome.message || ''; applyCapabilities();void loadPresets().catch(error=>showStatus(error.message,'error'));
  })();
  resourceRequest = { guildId, promise };
  try { await promise; } finally { if (resourceRequest?.promise === promise) resourceRequest = null; }
}
const workspacePages = {
  security:['Home','See how TAGGY is looking after your community.'],
  verification:['Verification','Choose how members get in and make the panel yours.'],
  tickets:['Tickets','Set up support, applications and your own conversations.'],
  fishing:['Fishing','A collection to build. A rare catch to chase.'],
  roles:['Roles','Give the right people the right tools.'],
  embeds:['Announcements','Write it, preview it and share it with your server.'],
  channels:['Welcome & channels','Set the welcome and keep conversations flowing.'],
  chat:['Messages','Read a channel and send a message as TAGGY.'],
  logs:['Logs','See what happened in your server.'],
  dms:['Direct messages','Your private view of TAGGY’s conversations.']
};
function applyTabState(){
  const page=workspacePages[currentTab]||workspacePages.security;
  for(const button of document.querySelectorAll('[data-tab]'))button.setAttribute('aria-pressed',String(button.dataset.tab===currentTab));
  for(const panel of document.querySelectorAll('[data-panel]'))panel.hidden=panel.dataset.panel!==currentTab;
  $('workspace-title').textContent=page[0];$('workspace-description').textContent=page[1];
  document.title=page[0]+' · TAGGY';
}
for (const button of document.querySelectorAll('[data-tab]')) button.addEventListener('click', () => {
  if (button.dataset.tab === 'dms' && !isSpecialOwner) return;
  currentTab = button.dataset.tab;applyTabState();
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
function readEmbedFields() { return [...$('embed-field-rows').children].map(row => ({ name:row.querySelector('[data-field=name]').value, value:row.querySelector('[data-field=value]').value, inline:row.querySelector('[data-field=inline]').checked })); }
function addEmbedField(field = {}) {
 if ($('embed-field-rows').children.length >= 25) return;
 const row = document.createElement('fieldset'); row.className = 'embed-field-row';
 row.append(textElement('legend', 'Extra field'));
 for (const [key, title, max] of [['name','Heading',256],['value','Text',1024]]) {
  const label=textElement('label',title); const input=document.createElement(key==='value'?'textarea':'input');
  input.dataset.field=key; input.maxLength=max; input.required=true; input.value=field[key]||''; label.append(input); row.append(label);
 }
 const label=textElement('label','Show side by side'); const inline=document.createElement('input'); inline.type='checkbox'; inline.dataset.field='inline'; inline.checked=field.inline===true; label.append(inline); row.append(label);
 const remove=textElement('button','Remove field'); remove.type='button'; remove.addEventListener('click',()=>{row.remove();dirtyForms.add('embed-form');dirty=true;previewEmbed();}); row.append(remove); $('embed-field-rows').append(row);
}
$('add-embed-field').addEventListener('click',()=>{addEmbedField();dirtyForms.add('embed-form');dirty=true;previewEmbed();});
function embedBody() {
  const embed = Object.fromEntries(['title', 'description', 'color', 'url', 'image', 'thumbnail', 'footer'].map(key => [key, $(`embed-${key}`).value]));
  embed.fields = readEmbedFields();
  return { channelId: $('embed-channel').value, messageId: $('embed-id').value.trim(), content: $('embed-content').value, embed };
}
function previewEmbed() {
  $('preview-title').textContent = $('embed-title').value || 'Your title'; $('preview-description').textContent = $('embed-description').value || 'Your message, styled your way.';
  $('preview-footer').textContent = $('embed-footer').value; $('embed-preview').style.borderLeftColor = $('embed-color').value;
  $('preview-fields').replaceChildren();
  for (const field of readEmbedFields()) { const div=document.createElement('div'); div.append(textElement('strong',field.name),textElement('p',field.value)); $('preview-fields').append(div); }
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
    $('embed-footer').value = embed.footer?.text || ''; $('embed-field-rows').replaceChildren(); for (const field of embed.fields || []) addEmbedField(field);
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

$('priority-server').addEventListener('click', () => { if (priorityGuild) switchServer(priorityGuild); });

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
  for(const message of messages){const row=textElement('article','',`chat-message ${message.direction==='outgoing'?'outgoing':''}`);if(element.id==='dm-messages')row.append(avatar(message));row.append(textElement('strong',`${message.author}${message.bot?' · bot':''}`),textElement('time',new Date(message.at).toLocaleString()),textElement('p',message.content||'(attachment)')); for(const attachment of message.attachments||[]){try{const url=new URL(attachment.url);if(url.protocol!=='https:'||!['cdn.discordapp.com','media.discordapp.net'].includes(url.hostname))continue;const link=textElement('a',attachment.name||'Attachment');link.href=url.href;link.target='_blank';link.rel='noopener noreferrer';row.append(link);const name=(attachment.name||'').toLowerCase();let media;if(/\.(?:png|jpe?g|gif|webp|avif)$/.test(name)){media=document.createElement('img');media.alt=attachment.name||'Picture';media.loading='lazy';}else if(/\.(?:mp4|webm|mov)$/.test(name)){media=document.createElement('video');media.controls=true;media.preload='metadata';}else if(/\.(?:mp3|wav|ogg|m4a)$/.test(name)){media=document.createElement('audio');media.controls=true;media.preload='none';}if(media){media.className='message-media';media.src=url.href;row.append(media);}}catch(_){}} element.append(row);}
  if(nearBottom) element.scrollTop=element.scrollHeight;
}
async function loadChat() {
  const guildId=selected,channelId=$('chat-channel').value; const key=`${guildId}/${channelId}`; if(!guildId||!channelId||channelLoading===key)return; displayedChannel=channelId;
  const capability=resources?.channels.find(channel=>channel.id===channelId);$('chat-access').textContent=capability?.canSend?'Messages are sent by TAGGY.':'You can read this channel. Sending is unavailable.';
  $('chat-discord').href='https://discord.com/channels/'+encodeURIComponent(guildId)+'/'+encodeURIComponent(channelId);
  if(!capability?.canRead){$('channel-messages').replaceChildren(textElement('p','Message history is unavailable in this channel.','muted'));return;}
  channelLoading=key;
  try{const data=await api(`guilds/${guildId}/messages?channelId=${encodeURIComponent(channelId)}`);if(selected===guildId&&$('chat-channel').value===channelId)renderMessages($('channel-messages'),data.messages);}
  finally{if(channelLoading===key)channelLoading='';}
}
function renderDMThreads(){
 $('dm-threads').replaceChildren();const query=$('dm-search').value.toLowerCase();
 for(const thread of dmThreads.filter(t=>(t.name+' '+(t.username||'')).toLowerCase().includes(query))){const button=textElement('button','');button.type='button';button.setAttribute('aria-current',String(thread.id===dmUser));button.setAttribute('aria-label',thread.name);button.append(avatar(thread));const copy=textElement('span','','dm-thread-copy');copy.append(textElement('strong',thread.name),textElement('small',thread.preview.slice(0,70)));button.append(copy);button.addEventListener('click',()=>selectDM(thread.id));$('dm-threads').append(button);}
 if(!$('dm-threads').children.length)$('dm-threads').append(textElement('p','No conversations here yet. Open one with a user ID.','muted'));
}
function renderDMProfile(user){
 $('dm-discord').href='https://discord.com/users/'+encodeURIComponent(user.id);
 $('dm-chat-header').replaceChildren(avatar(user),textElement('strong',user.name));
 const panel=$('dm-profile');panel.replaceChildren(avatar(user,'dm-profile-avatar'),textElement('h3',user.name),textElement('p','@'+(user.username||user.name),'muted'));
 panel.append(textElement('small','DISCORD USER ID'),textElement('p',user.id,'dm-profile-id'));
 const link=textElement('a','Open Discord profile ↗');link.href='https://discord.com/users/'+encodeURIComponent(user.id);link.target='_blank';link.rel='noopener noreferrer';panel.append(link,textElement('p','Messages are sent from TAGGY.','caption'));
}
async function loadDMs() {
 if(!isSpecialOwner||dmLoading)return;dmLoading=true;
 try{const data=await api('owner/dms');dmThreads=data.threads;renderDMThreads();if(data.storageError)showStatus('The inbox could not be saved. Check bot storage.','error');if(dmUser)await loadDMHistory();}
 finally{dmLoading=false;}
}
async function loadDMHistory(older=false){
 if(!isSpecialOwner||!dmUser||older&&!dmBefore)return;
 const user=dmUser,key=user+'/'+(older?dmBefore:'latest');if(dmHistoryLoading===key)return;dmHistoryLoading=key;
 const feed=$('dm-messages'),height=feed.scrollHeight,scroll=feed.scrollTop;
 $('dm-older').disabled=true;
 try{const data=await api('owner/dms?userId='+encodeURIComponent(user)+(older?'&before='+encodeURIComponent(dmBefore):''));if(user!==dmUser)return;
 const merged=new Map(dmRows.map(m=>[m.id,m]));for(const message of data.messages)merged.set(message.id,message);dmRows=[...merged.values()].sort((a,b)=>a.at-b.at);
 renderMessages(feed,dmRows);if(older)feed.scrollTop=scroll+feed.scrollHeight-height;
 if(older||!dmBefore){dmBefore=data.before||data.messages[0]?.id||null;$('dm-older').hidden=!data.hasMore;}
 const profile=data.profile||dmThreads.find(t=>t.id===user)||{id:user,name:user};renderDMProfile(profile);renderDMThreads();
 $('dm-history-note').textContent=data.warning|| (data.hasMore?'Older messages are available.':'Showing available conversation history.');
 }finally{if(dmHistoryLoading===key)dmHistoryLoading='';$('dm-older').disabled=false;}
}
$('dm-search').addEventListener('input',renderDMThreads);
$('dm-older').addEventListener('click',()=>void loadDMHistory(true).catch(error=>showStatus(error.message,'error')));
async function refreshCurrentTab(){void loadPresets().catch(error=>showStatus(error.message,'error'));if(currentTab==='dms')return loadDMs();if(!selected)return;if(currentTab==='tickets')return loadTickets();if(currentTab==='fishing')return loadFishing();if(currentTab==='verification')return loadVerification();if(currentTab==='logs')return loadLogs();if(currentTab==='chat')return loadChat();return loadDetail(false);}
$('log-search').addEventListener('input',renderLogs);
$('refresh-logs').addEventListener('click',()=>void loadLogs().catch(error=>showStatus(error.message,'error')));
$('refresh-chat').addEventListener('click',()=>void loadChat().catch(error=>showStatus(error.message,'error')));
$('chat-channel').addEventListener('change',()=>{if(($('chat-content').value.trim()||selectedFiles('chat').length)&&!confirm('Discard this draft and switch channels?')){$('chat-channel').value=displayedChannel;return;}$('chat-content').value='';clearUploads('chat');clearDraft('chat-form');$('channel-messages').replaceChildren();void loadChat().catch(error=>showStatus(error.message,'error'));});

function selectedFiles(kind){return [...$(kind+'-files').files];}
function updateUploads(kind){const list=$(kind+'-uploads');list.replaceChildren();const files=selectedFiles(kind);if(files.length)list.append(textElement('p',files.map(file=>file.name+' ('+(file.size/1024/1024).toFixed(1)+' MB)').join(' · ')));}
async function encodeFiles(kind){if(selectedFiles(kind).length)throw Error('Please send pictures, GIFs and files in Discord. Website messaging supports text.');return [];}
function clearUploads(kind){$(kind+'-files').value='';updateUploads(kind);}
for(const kind of ['chat','dm'])$(kind+'-files').addEventListener('change',()=>{updateUploads(kind);dirtyForms.add(kind+'-form');dirty=true;});

$('chat-form').addEventListener('submit',async event=>{event.preventDefault();if(!resources?.channels.find(channel=>channel.id===$('chat-channel').value)?.canSend){showStatus('You cannot send to this channel.','error');return;}let files;try{files=await encodeFiles('chat');}catch(error){showStatus(error.message,'error');return;}const result=await action(`guilds/${selected}/chat`,{channelId:$('chat-channel').value,content:$('chat-content').value,files},'Message sent.');if(result){$('chat-content').value='';clearUploads('chat');clearDraft('chat-form');if(result.warning)showStatus(result.warning,'error');await loadChat().catch(error=>showStatus(`Message sent. Refresh failed: ${error.message}`,'error'));}});
$('dm-open-form').addEventListener('submit',event=>{event.preventDefault();selectDM($('dm-user-id').value.trim());});
$('refresh-dms').addEventListener('click',()=>void loadDMs().catch(error=>showStatus(error.message,'error')));
$('dm-form').addEventListener('submit',async event=>{event.preventDefault();if(!isSpecialOwner||!dmUser){showStatus('Open a conversation first.','error');return;}let files;try{files=await encodeFiles('dm');}catch(error){showStatus(error.message,'error');return;}const result=await action('owner/dms',{userId:dmUser,content:$('dm-content').value,files},'DM sent.');if(result){$('dm-content').value='';clearUploads('dm');clearDraft('dm-form');if(result.warning)showStatus(result.warning,'error');await loadDMs().catch(error=>showStatus(`DM sent. Refresh failed: ${error.message}`,'error'));}});

function selectDM(userId){if(dmUser!==userId&&($('dm-content').value.trim()||selectedFiles('dm').length)&&!confirm('Discard this draft and switch conversations?')){$('dm-user-id').value=dmUser;return;}if(dmUser!==userId){$('dm-content').value='';clearUploads('dm');clearDraft('dm-form');}if(dmUser!==userId){dmRows=[];dmBefore=null;$('dm-messages').replaceChildren();$('dm-older').hidden=true;$('dm-chat-header').textContent='Loading conversation…';$('dm-profile').replaceChildren();}dmUser=userId;$('dm-user-id').value=userId;void loadDMHistory().catch(error=>showStatus(error.message,'error'));}
function applyCapabilities(){if(!resources||busy)return;applyNewCapabilities();$('chat-files').disabled=true;$('dm-files').disabled=true;const cap=resources.capabilities||{};for(const [selector,key]of [['#roles-form button,#roles-form select','changeRoles'],['#member-role-form button,#assign-role','assignRoles'],['#channel-form button,#control-channel,#slowmode','channels'],['#release-form button,#member-id','timeout'],['#auto-role','autoRole']]){for(const control of document.querySelectorAll(selector))control.disabled=cap[key]===false;} }

async function loadVerification(){const id=selected;if(!id||dirtyForms.has('verification-form'))return;const data=await api('guilds/'+id+'/verification');if(id!==selected||dirtyForms.has('verification-form'))return;const config=data.settings;$('verification-mode').value=config.mode;$('verification-group-required').checked=config.groupRequired;$('verification-group').value=config.groupId;$('verification-channel').value=config.channelId||'';$('verification-title').value=config.title||'';$('verification-description').value=config.description||'';verificationVisibility();verificationLoaded=id;const can=resources?.capabilities?.changeRoles!==false;for(const input of $('verification-form').querySelectorAll('input,select,textarea,button'))input.disabled=!can;$('verification-note').textContent=can?'Settings apply to '+$('server-name').textContent+'.':'Only the server owner or a Discord administrator can change verification.';}
$('verification-mode').addEventListener('change',verificationVisibility);$('verification-group-required').addEventListener('change',verificationVisibility);
$('verification-form').addEventListener('submit',async event=>{event.preventDefault();const body={mode:$('verification-mode').value,groupRequired:$('verification-group-required').checked,groupId:$('verification-group').value.trim(),channelId:$('verification-channel').value,title:$('verification-title').value,description:$('verification-description').value};const result=await action('guilds/'+selected+'/verification',body,'Verification settings saved.');if(result){clearDraft('verification-form');await loadResources();if(result.warning)showStatus(result.warning,'error');await loadVerification();}});

// Server presets are suggestions: applying one fills a draft, saving applies the change.
let presetGuild='',serverPresets={};
const presetSection=textElement('details','','preset-bar');presetSection.id='preset-bar';
const presetSummary=textElement('summary','Presets');presetSummary.append(textElement('small','Start with a preset or save your own.'));
const presetControls=textElement('div','','preset-controls');
const presetCopy=textElement('div','','preset-copy');presetCopy.append(textElement('strong','Make it yours'),textElement('small','Start with a preset, tweak it, then save.'));
const presetSelect=document.createElement('select');presetSelect.id='preset-select';presetSelect.setAttribute('aria-label','Server presets');
const presetUse=textElement('button','Use preset'),presetSave=textElement('button','Save as preset'),presetDelete=textElement('button','Delete preset');for(const button of [presetUse,presetSave,presetDelete])button.type='button';
presetControls.append(presetCopy,presetSelect,presetUse,presetSave,presetDelete);presetSection.append(presetSummary,presetControls);$('workspace-heading').after(presetSection);
const presetTab=()=>({security:'home',channels:'welcome'}[currentTab]||currentTab);
const presetForms={home:'settings-form',verification:'verification-form',roles:'roles-form',embeds:'embed-form',welcome:'welcome-form',fishing:'fishing-form'};
function renderPresetBar(){const tab=presetTab(),items=serverPresets[tab]||[];const previous=presetSection.dataset.tab===tab?presetSelect.value:'';presetSection.dataset.tab=tab;presetSection.hidden=!presetForms[tab];options(presetSelect,items.map(item=>({id:item.id,name:item.name})),'Choose a preset');if(items.length)presetSelect.value=items.some(item=>item.id===previous)?previous:items[0].id;const can=resources?.capabilities?.changeRoles!==false;presetSave.disabled=!can;presetDelete.disabled=!can||!items.length;presetUse.disabled=!items.length;}
async function loadPresets(){if(!selected){presetSection.hidden=true;return;}const id=selected;if(presetGuild!==id){const data=await api('guilds/'+id+'/presets');if(id!==selected)return;serverPresets=data.presets;presetGuild=id;}renderPresetBar();}
function presetControl(form,key){const element=$(key)||form.elements.namedItem(key);return element&&form.contains(element)?element:null;}
presetUse.addEventListener('click',()=>{const tab=presetTab(),form=$(presetForms[tab]),preset=(serverPresets[tab]||[]).find(p=>p.id===presetSelect.value);if(!form||!preset)return;for(const [key,value]of Object.entries(preset.values)){const field=presetControl(form,key);if(!field)continue;if(field.type==='checkbox')field.checked=Boolean(value);else field.value=String(value);}dirtyForms.add(form.id);dirty=true;if(tab==='verification')verificationVisibility();if(tab==='embeds')previewEmbed();showStatus('Preset added to your draft. Adjust it, then save when ready.','success');});
presetDelete.addEventListener('click',async()=>{const tab=presetTab(),items=(serverPresets[tab]||[]).filter(p=>p.id!==presetSelect.value);const result=await action('guilds/'+selected+'/presets',{tab,presets:items},'Preset removed.');if(result){serverPresets=result.presets;renderPresetBar();}});
presetSave.addEventListener('click',async()=>{const tab=presetTab(),form=$(presetForms[tab]);if(!form)return;const items=serverPresets[tab]||[];if(items.length>=6){showStatus('You can keep six presets per tab. Remove one first.','error');return;}const name=prompt('Name this preset');if(!name?.trim())return;const values={};for(const field of form.querySelectorAll('input,select,textarea')){if(field.type==='file'||field.multiple)continue;const key=field.id||field.name;if(key)values[key]=field.type==='checkbox'?field.checked:field.type==='number'?Number(field.value):field.value;}const result=await action('guilds/'+selected+'/presets',{tab,presets:[...items,{id:'custom-'+crypto.randomUUID().slice(0,8),name:name.trim(),values}]},'Preset saved for this server.');if(result){serverPresets=result.presets;renderPresetBar();}});

let ticketDraft=[],ticketPresets=[];
const markTicketDraft=()=>{dirtyForms.add('tickets-form');dirty=true;};
function renderTicketTypes(){const list=$('ticket-types');list.replaceChildren();for(const type of ticketDraft){const card=textElement('details','','ticket-type');card.dataset.type=type.id;card.open=type.id==='staff-application'||type.id.startsWith('custom-');const summary=textElement('summary','');summary.append(textElement('strong',type.name||'New ticket type'),textElement('small',type.questions.length?type.questions.length+' questions':'A normal conversation'));card.append(summary);const heading=textElement('div','','section-heading');heading.append(textElement('strong',type.name||'New ticket type'));const remove=textElement('button','Remove');remove.type='button';remove.addEventListener('click',()=>{ticketDraft=ticketDraft.filter(item=>item!==type);markTicketDraft();renderTicketTypes();});heading.append(remove);card.append(heading);for(const [key,label,max,rows]of [['name','Button name',80,0],['description','Short description',200,0],['questions','Questions · one per line',4200,4]]){const wrapper=textElement('label',label);const input=document.createElement(rows?'textarea':'input');if(rows)input.rows=rows;input.maxLength=max;input.value=key==='questions'?type.questions.join('\n'):type[key];input.setAttribute('aria-label',label+' for '+type.name);input.addEventListener('input',()=>{type[key]=key==='questions'?input.value.split('\n').map(line=>line.trim()).filter(Boolean):input.value;markTicketDraft();});wrapper.append(input);card.append(wrapper);}card.append(textElement('p','Leave questions empty for a normal conversation. Up to 12 questions, 350 characters each.','caption'));list.append(card);}if(!ticketDraft.length)list.append(textElement('p','No ticket types. Add one or restore the presets to publish an Open Ticket button.','muted'));applyNewCapabilities();}
function chosen(select){return [...select.selectedOptions].map(option=>option.value).filter(Boolean);}
function fillMulti(element,roles,selected){options(element,roles,'');element.firstChild.remove();for(const option of element.options)option.selected=selected.includes(option.value);}
async function loadTickets(){if(!selected||dirtyForms.has('tickets-form'))return;const id=selected,data=await api('guilds/'+id+'/tickets');if(id!==selected||dirtyForms.has('tickets-form'))return;const config=data.settings;ticketDraft=structuredClone(config.types);ticketPresets=data.presets;$('tickets-title').value=config.title;$('tickets-description').value=config.description;$('tickets-reminders').checked=config.remindersEnabled;$('tickets-days').value=config.reminderDays;const roles=(resources?.roles||[]).filter(role=>role.id!==selected);fillMulti($('tickets-staff'),roles,data.staffRoleIds);fillMulti($('tickets-ping'),roles,config.reminderRoleIds);renderTicketTypes();const closed=$('closed-tickets');closed.replaceChildren();for(const item of data.closed){const row=textElement('article','','closed-ticket-row');const copy=textElement('div','');copy.append(textElement('strong',item.name),textElement('small',item.type+(item.closedAt?' · '+new Date(item.closedAt).toLocaleDateString():'')));const open=textElement('a','View in Discord ↗');open.href='https://discord.com/channels/'+id+'/'+item.id;open.target='_blank';open.rel='noopener noreferrer';row.append(copy,open);if(resources?.capabilities?.changeRoles!==false){const button=textElement('button','Delete channel');button.type='button';button.className='danger';button.addEventListener('click',async()=>{if(!confirm('Permanently delete '+item.name+'? This cannot be undone. Saved transcripts keep their normal retention period.'))return;const result=await action('guilds/'+id+'/ticket-delete',{channelId:item.id,confirmed:true},'Closed ticket channel deleted.');if(result)await loadTickets();});row.append(button);}closed.append(row);}if(!data.closed.length)closed.append(textElement('p','No closed tickets you can view. Closed tickets will appear here.','muted'));applyNewCapabilities();}
$('ticket-add').addEventListener('click',()=>{if(ticketDraft.length>=10){showStatus('Up to ten ticket types are supported.','error');return;}ticketDraft.push({id:'custom-'+crypto.randomUUID().slice(0,8),name:'New ticket',description:'',questions:[]});markTicketDraft();renderTicketTypes();});
$('ticket-defaults').addEventListener('click',()=>{ticketDraft=structuredClone(ticketPresets);markTicketDraft();renderTicketTypes();});
$('tickets-refresh').addEventListener('click',()=>void loadTickets().catch(error=>showStatus(error.message,'error')));
$('tickets-form').addEventListener('submit',async event=>{event.preventDefault();const result=await action('guilds/'+selected+'/tickets',{settings:{title:$('tickets-title').value,description:$('tickets-description').value,types:ticketDraft,remindersEnabled:$('tickets-reminders').checked,reminderDays:Number($('tickets-days').value),reminderRoleIds:chosen($('tickets-ping'))},staffRoleIds:chosen($('tickets-staff'))},'Ticket settings saved.');if(result){clearDraft('tickets-form');await loadTickets();if(result.warning)showStatus(result.warning,'error');}});
async function loadFishing(){if(!selected||dirtyForms.has('fishing-form'))return;const id=selected,data=await api('guilds/'+id+'/fishing');if(id!==selected||dirtyForms.has('fishing-form'))return;$('fishing-enabled').checked=data.settings.enabled;$('fishing-cooldown').value=data.settings.cooldownSeconds;applyNewCapabilities();}
$('fishing-form').addEventListener('submit',async event=>{event.preventDefault();const result=await action('guilds/'+selected+'/fishing',{enabled:$('fishing-enabled').checked,cooldownSeconds:Number($('fishing-cooldown').value)},'Fishing settings saved.');if(result){clearDraft('fishing-form');await loadFishing();}});
function applyNewCapabilities(){const can=resources?.capabilities?.changeRoles!==false&&!busy;for(const element of document.querySelectorAll('#tickets-form input,#tickets-form textarea,#tickets-form select,#tickets-form button,#fishing-form input,#fishing-form button'))element.disabled=!can;$('tickets-note').textContent=can?'Save to publish the panel. Open tickets keep their original questions.':'Only the server owner or a Discord administrator can change tickets.';}

// Pause media out of view. Reduced-motion users get manual controls and static examples.
const reducedMotion=matchMedia('(prefers-reduced-motion: reduce)');
const introVideo=$('intro-video');
const introSound=$('intro-sound');
function syncSoundControl(){const audible=!introVideo.muted&&introVideo.volume>0;introSound.textContent=audible?'Mute video':'Turn sound on';introSound.setAttribute('aria-pressed',String(audible));$('intro-sound-note').textContent=audible?'Original video sound is on.':'Starts muted. Turn sound on to hear the video.';}
introSound.addEventListener('click',()=>{const audible=!introVideo.muted&&introVideo.volume>0;introVideo.muted=audible;if(!audible){if(introVideo.volume===0)introVideo.volume=1;void introVideo.play().catch(()=>{$('intro-sound-note').textContent='Use the video play button to start playback.';});}syncSoundControl();});
introVideo.addEventListener('volumechange',syncSoundControl);
syncSoundControl();
let introVisible=false;
function syncVideoPlayback(){if(introVisible&&!document.hidden&&!document.body.classList.contains('signed-in')&&!reducedMotion.matches)void introVideo.play().catch(()=>{});else introVideo.pause();}
const observer=new IntersectionObserver(entries=>{for(const entry of entries){if(entry.target===introVideo){introVisible=entry.isIntersecting&&entry.intersectionRatio>=0.35;syncVideoPlayback();}else entry.target.classList.toggle('playing',entry.isIntersecting&&!reducedMotion.matches);}},{threshold:0.35});
observer.observe(introVideo);for(const demo of document.querySelectorAll('[data-demo]'))observer.observe(demo);
document.addEventListener('visibilitychange',syncVideoPlayback);
function videoIsOnScreen(){const rect=introVideo.getBoundingClientRect();return rect.bottom>0&&rect.top<innerHeight;}
function pauseHiddenVideo(){if(!videoIsOnScreen()||document.hidden||document.body.classList.contains('signed-in'))introVideo.pause();}
window.addEventListener('scroll',pauseHiddenVideo,{passive:true});
introVideo.addEventListener('playing',pauseHiddenVideo);
reducedMotion.addEventListener('change',()=>{syncVideoPlayback();if(reducedMotion.matches)for(const demo of document.querySelectorAll('[data-demo]'))demo.classList.remove('playing');});
