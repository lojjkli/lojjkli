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
const initialRoute = new URL(location.href).searchParams;
let currentTab = initialRoute.get('tab') || 'home';
let currentSection = initialRoute.get('section') || '';
if(currentTab==='rolepanels'){currentTab='roles';currentSection='panels';}
const PROFILE_GUILD_ID='1553040593494609920';
const profileAllowed=()=>isSpecialOwner&&selected===PROFILE_GUILD_ID;
let logRows = [];
let supportedSettings = new Set();
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
    active = false; csrf = ''; selected = ''; isSpecialOwner = false; resources = null; dmUser = ''; currentTab='home';syncMobileTools();
    fishingData=null;fishingFor='';fishingPlayer=null;fishingPlayerFor='';$('fishing-player-form').hidden=true;$('fishing-player-profile').replaceChildren();giveawayData=null;giveawayFor='';$('giveaway-active').replaceChildren();$('giveaway-results').replaceChildren();$('tool-search-results').replaceChildren();if($('tool-search-dialog').open)$('tool-search-dialog').close();
    dmRows=[];dmThreads=[];dmBefore=null;$('dm-profile').replaceChildren();$('dm-chat-header').replaceChildren();$('dm-messages').replaceChildren(); $('dm-threads').replaceChildren(); $('channel-messages').replaceChildren(); $('incidents').replaceChildren();
    $('header-login').hidden = false; document.body.classList.remove('signed-in'); $('account-name').hidden = true;
    $('dashboard').hidden = true; $('logout').hidden = true; $('login').hidden = false;
    throw new Error('Sign in with Discord to continue.');
  }
  if (!response.ok) { const error = new Error(data.error || `Request failed (${response.status})`); error.status = response.status; throw error; }
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
  supportedSettings = new Set(Object.keys(data.config));
  $('detail').hidden = false;
  renderActivity(data);
  for(const field of document.querySelectorAll('[data-new-setting]'))field.hidden=!supportedSettings.has(field.dataset.newSetting);
  $('security-update-note').hidden=supportedSettings.has('antiLinks');
  const picked=$('timeout-member').value;options($('timeout-member'),data.timeouts||[],'Choose a member');$('timeout-member').value=picked;
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
  $('automatic-copy').textContent = fullyAutomatic ? 'TAGGY checks new joins, spam and destructive changes automatically. It restricts suspicious activity and alerts the bot owner, even when this page is closed.' : 'Turn on automatic protection to let TAGGY handle join raids, spam and destructive changes. Choose the checks below and save your settings.';
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
  syncRanges(); logRows = data.incidents; renderLogs();
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
  if(selected&&$('status').textContent==='Pick a server to get started.'&&$('status').classList.contains('success'))showStatus('Your server is ready.','success');
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
  for (const input of $('settings-form').elements) if (input.name && supportedSettings.has(input.name)) body[input.name] = input.type === 'checkbox' ? input.checked : Number(input.value);
  await action(`guilds/${selected}/settings`, body, 'Protection settings saved.');
  if ($('status').classList.contains('success')) { clearDraft('settings-form'); await loadDetail(true); }
});
$('shield-on').addEventListener('click', () => {
  if (!confirm('Activate join shield for this server? Incoming non-staff members will receive a timeout.')) return;
  void action(`guilds/${selected}/shield`, { active: true }, 'Join shield activated.');
});
$('shield-off').addEventListener('click', () => { void action(`guilds/${selected}/shield`, { active: false }, 'Join shield ended. Existing timeouts are unchanged.'); });
$('release-form').addEventListener('submit', event => {
  event.preventDefault(); const memberId = $('timeout-member').value || $('member-id').value.trim();
  if(!memberId){showStatus('Choose a member first.','error');return;}
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
    $('header-login').hidden = true; document.body.classList.add('signed-in'); $('account-name').hidden = false; $('account-name').textContent = session.username || session.userId; $('dm-tab').hidden = !isSpecialOwner; $('bot-profile-tab').hidden = !profileAllowed(); profileSupported=session.features?.profile===true;
    $('login').hidden = true; $('dashboard').hidden = false; $('logout').hidden = false;syncMobileTools();
    await loadList();readDashboardRoute(false);await refreshCurrentTab(); showStatus(isSpecialOwner ? 'Your servers are ready.' : selected ? 'Your server is ready.' : 'Pick a server to get started.', 'success');
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
    resources = data; resourcesFor = guildId; communityChannels();
    if(!dirtyForms.has('roles-form'))for (const key of roleKeys) { options($(`binding-${key}`), data.roles, ['member','unverified'].includes(key)?'Choose a role':'Not set'); $(`binding-${key}`).value = data.bindings[key] || ''; }
    updateMemberRoleNotices();
    options($('chat-channel'), data.channels.filter(channel => channel.canRead || channel.canSend), 'Choose channel');
    for (const name of ['embed-channel', 'control-channel', 'welcome-channel', 'log-channel']) options($(name), data.channels, name.includes('welcome') || name === 'log-channel' ? 'Disabled' : 'Choose channel');
    options($('verification-channel'), data.channels, 'Create or reuse verification channel');
    options($('assign-role'), data.roles, 'Choose role'); options($('auto-role'), data.roles.filter(role => role.editable), 'Disabled');
    if(!dirtyForms.has('welcome-form')){ $('welcome-channel').value = data.welcome.channelId || ''; $('log-channel').value = data.welcome.logChannelId || '';
    $('auto-role').value = data.welcome.autoRoleId || ''; $('welcome-message').value = data.welcome.message || ''; } applyCapabilities();void loadPresets().catch(error=>showStatus(error.message,'error'));
  })();
  resourceRequest = { guildId, promise };
  try { await promise; } finally { if (resourceRequest?.promise === promise) resourceRequest = null; }
}
const giveawayTab=textElement('button','');giveawayTab.type='button';giveawayTab.dataset.tab='giveaways';giveawayTab.setAttribute('aria-pressed','false');giveawayTab.append(textElement('i','🎉','giveaway-nav-icon'),textElement('span','Giveaways'));giveawayTab.firstElementChild.setAttribute('aria-hidden','true');document.querySelector('.console-tabs [data-tab="fishing"]').before(giveawayTab);
const toolSearchButton=textElement('button','');toolSearchButton.type='button';toolSearchButton.className='tool-search-open desktop-tool-search';toolSearchButton.append(textElement('span','⌕','giveaway-nav-icon'),textElement('span','Find a tool'),textElement('kbd','/'));toolSearchButton.setAttribute('aria-label','Search dashboard tools');document.querySelector('.console-tabs').prepend(toolSearchButton);
const workspacePages = {
  home:['Home','A quick look at your server today.'],
  security:['Security','Choose what TAGGY watches and how it responds.'],
  verification:['Verification','Choose how members get in and make the panel yours.'],
  tickets:['Tickets','Set up support, applications and your own conversations.'],
  fishing:['Fishing','A collection to build. A rare catch to chase.'],
  giveaways:['Giveaways','Put something up for grabs. Let TAGGY pick the lucky ones.'],
  roles:['Roles','Give the right people the right tools.'],
  tools:['Tools','Polls, trigger words and a command when you need one.'],
  profile:['Bot profile','TAGGY’s name and status, across all servers.'],
  embeds:['Announcements','Write a message, post it now or choose a time.'],
  channels:['Welcome & channels','Set the welcome and keep conversations flowing.'],
  chat:['Messages','Read a channel and send a message as TAGGY.'],
  logs:['Logs','See what happened in your server.'],
  dms:['Direct messages','Your private view of TAGGY’s conversations.']
};
const workspaceSections={
 home:[['overview','Overview'],['setup','Setup']],
 giveaways:[['create','Create'],['active','Active'],['results','Results']],
 roles:[['permissions','Server roles'],['members','Member roles'],['panels','Role panels']],
 tools:[['polls','Polls'],['triggers','Trigger words'],['commands','Commands'],['server','Server info'],['members','Member profiles'],['nickname','Nickname']],
 tickets:[['panel','Ticket panel'],['topics','Topics & questions'],['reminders','Reminders'],['closed','Closed tickets']],
 security:[['protection','Protection'],['limits','Limits'],['shield','Shield & timeouts']],
 embeds:[['editor','Editor'],['scheduled','Scheduled posts'],['history','History']],
 channels:[['welcome','Welcome'],['dms','Welcome DMs'],['controls','Channels']],
 fishing:[['settings','Settings'],['collection','Collection'],['boosts','Boosts'],['players','Players'],['guide','How to play']]
};
const rememberedSections={};
function dashboardURL(tab=currentTab,section=currentSection){const url=new URL(location.href);url.hash='';if(selected)url.searchParams.set('server',selected);else url.searchParams.delete('server');url.searchParams.set('tab',tab);if(section)url.searchParams.set('section',section);else url.searchParams.delete('section');return url;}
function allowedTool(tab){return Object.hasOwn(workspacePages,tab)&&(tab!=='dms'||isSpecialOwner)&&(tab!=='profile'||profileAllowed());}
function normalizeWorkspace(){if(currentTab==='fishing'&&selected===PROFILE_GUILD_ID&&['boosts','players'].includes(currentSection)&&fishingFor!==selected)return;if(!allowedTool(currentTab)){currentTab='home';currentSection='';}const sections=workspaceSections[currentTab]?availableSections(currentTab):null;if(sections&&!sections.some(([id])=>id===currentSection))currentSection=sections.some(([id])=>id===rememberedSections[currentTab])?rememberedSections[currentTab]:sections[0][0];if(!sections)currentSection='';if(currentSection)rememberedSections[currentTab]=currentSection;}
function renderSections(){
 const nav=$('workspace-sections'),sections=availableSections(currentTab),focusedSection=nav.contains(document.activeElement)?document.activeElement.dataset.sectionLink:'';nav.hidden=!sections.length;nav.replaceChildren();
 for(const [id,label]of sections){const link=textElement('a',label);link.dataset.sectionLink=id;link.href=dashboardURL(currentTab,id).href;if(id===currentSection)link.setAttribute('aria-current','page');link.addEventListener('click',event=>{if(event.button||event.metaKey||event.ctrlKey||event.shiftKey||event.altKey)return;event.preventDefault();chooseTool(currentTab,id);});nav.append(link);if(id===focusedSection)link.focus({preventScroll:true});}
 for(const panel of document.querySelectorAll('[data-panel]'))for(const part of panel.querySelectorAll('[data-section]'))if(part.closest('[data-panel]')===panel)part.hidden=panel.dataset.panel!==currentTab||!part.dataset.section.split(' ').includes(currentSection)||(panel.dataset.panel==='fishing'&&['boosts','players'].includes(part.dataset.section)&&!fishingAdminAllowed());
 // A shared form keeps drafts from all its sections and saves them together.
 const securitySettings=$('settings-form').closest('.card');securitySettings.hidden=currentTab!=='security'||!['protection','limits'].includes(currentSection);
 const ticketsCard=$('tickets-form').closest('.tickets-card');ticketsCard.hidden=currentTab!=='tickets'||currentSection==='closed';
 document.body.dataset.section=currentSection;
 const sectionsLabel=sections.find(([id])=>id===currentSection)?.[1];document.title=(sectionsLabel?sectionsLabel+' · ':'')+workspacePages[currentTab][0]+' · TAGGY';
 $('copy-dashboard-link').dataset.url=dashboardURL().href;
 if(typeof presetSection!=='undefined')presetSection.hidden=currentTab==='home'||!presetForms[presetTab()]||(currentTab==='roles'&&currentSection!=='permissions')||(currentTab==='channels'&&currentSection!=='welcome')||(currentTab==='embeds'&&currentSection!=='editor')||(currentTab==='fishing'&&currentSection!=='settings');
}
function applyTabState(){
 normalizeWorkspace();document.body.dataset.tool=currentTab;
 const page=workspacePages[currentTab]||workspacePages.home;
 $('bot-profile-tab').hidden=!profileAllowed();
 for(const button of document.querySelectorAll('[data-tab]'))button.setAttribute('aria-pressed',String(button.dataset.tab===currentTab));
 for(const panel of document.querySelectorAll('[data-panel]'))panel.hidden=panel.dataset.panel!==currentTab;
 $('workspace-title').textContent=page[0];$('workspace-description').textContent=page[1];
 syncMobileTools();renderSections();
}
function syncMobileTools(){
 const picker=$('mobile-tool');
 const allowed=[...document.querySelectorAll('.console-tabs [data-tab]')].filter(button=>allowedTool(button.dataset.tab));
 const signature=allowed.map(button=>button.dataset.tab).join(',');
 if(picker.dataset.tools!==signature){picker.replaceChildren();for(const button of allowed){const option=textElement('option',button.querySelector('span').textContent);option.value=button.dataset.tab;picker.append(option);}picker.dataset.tools=signature;}
 picker.value=currentTab;
}
function chooseTool(tab,section='',historyMode='push'){
 if(tab==='rolepanels'){tab='roles';section='panels';}
 if(busy||!allowedTool(tab)){syncMobileTools();return;}
 const previous=currentTab;currentTab=tab;currentSection=section||(previous===tab?currentSection:rememberedSections[tab]||'');applyTabState();
 const url=dashboardURL();if(url.href!==location.href)history[historyMode==='replace'?'replaceState':'pushState']({},'',url.href);
 void refreshCurrentTab().catch(error=>showStatus(error.message,'error'));
}
function readDashboardRoute(refresh=true){
 const url=new URL(location.href),server=url.searchParams.get('server');
 if(server&&server!==selected&&guilds.some(guild=>guild.id===server)){location.assign(url.href);return;}
 let tab=url.searchParams.get('tab')||'home',section=url.searchParams.get('section')||'';
 let hash='';try{hash=decodeURIComponent(url.hash.slice(1));}catch(_){}if(hash.includes('/'))[tab,section]=hash.split('/');
 const oldAnchors={'security-messages':['security','protection'],'security-joins':['security','protection'],'security-changes':['security','protection'],'poll-card':['tools','polls'],'reply-card':['tools','triggers'],'info-card':['tools','server'],'nickname-card':['tools','nickname']};
 if(oldAnchors[hash])[tab,section]=oldAnchors[hash];
 if(tab==='rolepanels'){tab='roles';section='panels';}currentTab=tab;currentSection=section;applyTabState();
 history.replaceState({},'',dashboardURL().href);if(refresh)void refreshCurrentTab().catch(error=>showStatus(error.message,'error'));
}
for(const button of document.querySelectorAll('.console-tabs [data-tab]'))button.addEventListener('click',()=>chooseTool(button.dataset.tab));
$('mobile-tool').addEventListener('change',event=>chooseTool(event.target.value));
window.addEventListener('popstate',()=>{if(active)readDashboardRoute();});window.addEventListener('hashchange',()=>{if(active)readDashboardRoute();});
$('copy-dashboard-link').addEventListener('click',async()=>{const url=dashboardURL().href;try{await navigator.clipboard.writeText(url);showStatus('Link copied to this section.','success');}catch(_){showStatus('Your section link: '+url);}});
function updateMemberRoleNotices(){
 for(const panel of document.querySelectorAll('[data-panel="tickets"],[data-panel="verification"]')){
  let notice=panel.querySelector('.member-role-notice');if(!notice){notice=textElement('p','','notice member-role-notice');const link=textElement('a','Choose a Member role ↗');link.href=dashboardURL('roles','permissions').href;link.addEventListener('click',event=>{event.preventDefault();chooseTool('roles','permissions');});notice.append(document.createTextNode('Set a Member role before setting up this feature. '),link);panel.prepend(notice);}notice.hidden=Boolean(resources?.bindings?.member);notice.querySelector('a').href=dashboardURL('roles','permissions').href;
 }
}
function initializeDashboardSections(){
 const roles=document.querySelector('[data-panel="roles"]'),roleCards=roles.querySelectorAll(':scope > .card');roleCards[0].dataset.section='permissions';roleCards[1].dataset.section='members';
 const panels=document.querySelector('[data-panel="rolepanels"]');panels.removeAttribute('data-panel');panels.dataset.section='panels';panels.hidden=false;roles.append(panels);
 for(const [id,section]of [['poll-card','polls'],['reply-card','triggers'],['nickname-card','nickname']])$(id).dataset.section=section;
 $('tools-note').dataset.section='polls triggers server members nickname';
 const info=$('info-card');info.dataset.section='server';info.querySelector('h3').textContent='Server info';
 const memberCard=textElement('section','','card');memberCard.dataset.section='members';memberCard.append(textElement('p','YOUR COMMUNITY','eyebrow'),textElement('h3','Member profiles'),$('member-profile-form'),$('tools-member-info'),info.querySelector('.caption'));info.after(memberCard);
 const security=document.querySelector('[data-panel="security"]');security.querySelector('.automatic-card').dataset.section='protection';security.querySelector('.overview').dataset.section='shield';security.querySelector('.security-levels').dataset.section='protection';security.querySelector('.section-heading h3').textContent='Protection settings';
 const settings=$('settings-form');for(const part of [...settings.children]){if(part.classList.contains('switches')||part.classList.contains('security-group'))part.dataset.section='protection';if(part.matches('details')){part.dataset.section='limits';part.open=true;part.querySelector('summary').textContent='Protection limits';}if(part.matches('nav'))part.remove();}
 const ticketForm=$('tickets-form'),topics=textElement('div','','ticket-topic-settings'),topicHeading=$('ticket-types').previousElementSibling;topics.dataset.section='topics';topicHeading.before(topics);topics.append(topicHeading,$('ticket-types'));
 for(const part of [...ticketForm.children]){if(part===topics||part.classList.contains('form-footer'))continue;if(part.matches('details')){part.dataset.section='reminders';part.open=true;}else part.dataset.section='panel';}
 document.querySelector('.ticket-panel-preview').dataset.section='panel topics';$('closed-tickets').closest('.card').dataset.section='closed';
 for(const part of document.querySelectorAll('[data-panel="channels"] > .card'))part.dataset.section=part.contains($('channel-form'))?'controls':part.contains($('welcome-dm-form'))?'dms':'welcome';
 for(const part of document.querySelectorAll('[data-panel="fishing"] > *')){part.dataset.section ||= part.classList.contains('fishing-guide')?'guide':'settings';if(part.matches('details'))part.open=true;}
 // Reveal the section containing a missing required value before browser validation focuses it.
 let validationPending=false;
 $('detail').addEventListener('invalid',event=>{
  if(validationPending){event.preventDefault();return;}validationPending=true;setTimeout(()=>{validationPending=false;},0);
  const part=event.target.closest('[data-section]'),panel=event.target.closest('[data-panel]');
  if(part&&panel&&panel.dataset.panel===currentTab&&part.hidden){currentSection=part.dataset.section.split(' ')[0];applyTabState();history.replaceState({},'',dashboardURL().href);}
  for(let ancestor=event.target.parentElement;ancestor&&ancestor!==panel;ancestor=ancestor.parentElement)if(ancestor.matches('details'))ancestor.open=true;
 },{capture:true});
 applyTabState();updateMemberRoleNotices();
}

$('roles-form').addEventListener('submit', async event => {
  event.preventDefault(); const body = Object.fromEntries(roleKeys.map(key => [key, $(`binding-${key}`).value]));
  if (body.owner !== (resources?.bindings.owner || '') && !confirm('Change the Owner role? Members with this role will gain owner bot commands in this server.')) return;
  const result = await action(`guilds/${selected}/roles`, body, 'Server roles saved.');
  if (result) { resources.bindings = body; clearDraft('roles-form');updateMemberRoleNotices(); }
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
  for(const message of messages){const row=textElement('article','',`chat-message ${message.direction==='outgoing'?'outgoing':''}`);if(element.id==='dm-messages')row.append(avatar(message));row.append(textElement('strong',`${message.author}${message.bot?' · bot':''}`),textElement('time',new Date(message.at).toLocaleString()),textElement('p',message.content||(message.embeds?.length?'': '(attachment)'))); for(const embed of message.embeds||[]){const card=textElement('article','','conversation-embed');if(embed.title)card.append(textElement('strong',embed.title));if(embed.description)card.append(textElement('p',embed.description));if(embed.footer)card.append(textElement('small',embed.footer));row.append(card);} for(const attachment of message.attachments||[]){try{const url=new URL(attachment.url);if(url.protocol!=='https:'||!['cdn.discordapp.com','media.discordapp.net'].includes(url.hostname))continue;const link=textElement('a',attachment.name||'Attachment');link.href=url.href;link.target='_blank';link.rel='noopener noreferrer';row.append(link);const name=(attachment.name||'').toLowerCase();let media;if(/\.(?:png|jpe?g|gif|webp|avif)$/.test(name)){media=document.createElement('img');media.alt=attachment.name||'Picture';media.loading='lazy';}else if(/\.(?:mp4|webm|mov)$/.test(name)){media=document.createElement('video');media.controls=true;media.preload='metadata';}else if(/\.(?:mp3|wav|ogg|m4a)$/.test(name)){media=document.createElement('audio');media.controls=true;media.preload='none';}if(media){media.className='message-media';media.src=url.href;row.append(media);}}catch(_){}} element.append(row);}
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
 $('dm-current-name').textContent=user.name;
 $('dm-discord').href='https://discord.com/users/'+encodeURIComponent(user.id);
 $('dm-chat-header').replaceChildren(avatar(user),textElement('strong',user.name));
 const panel=$('dm-profile');panel.replaceChildren(avatar(user,'dm-profile-avatar'),textElement('h3',user.name),textElement('p','@'+(user.username||user.name),'muted'));
 panel.append(textElement('small','DISCORD USER ID'),textElement('p',user.id,'dm-profile-id'));
 const link=textElement('a','Open Discord profile ↗');link.href='https://discord.com/users/'+encodeURIComponent(user.id);link.target='_blank';link.rel='noopener noreferrer';panel.append(link,textElement('p','Messages are sent from TAGGY.','caption'));
}
const mobileInbox=matchMedia('(max-width:850px)');
mobileInbox.addEventListener('change',()=>{if(!mobileInbox.matches)$('dm-inbox').open=true;});
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
async function refreshCurrentTab(){if(currentTab==='giveaways')return loadGiveaways();if(currentTab==='home'&&currentSection==='setup')return loadSetup();if(currentTab==='tools'&&currentSection==='commands')return loadCommands();if(currentTab==='embeds'&&['scheduled','history'].includes(currentSection))return loadSchedules();if(currentTab==='channels'&&currentSection==='dms')return loadWelcomeDM();if(['tools','profile'].includes(currentTab)||(currentTab==='roles'&&currentSection==='panels'))return loadCommunityTab();void loadPresets().catch(error=>showStatus(error.message,'error'));if(currentTab==='dms')return loadDMs();if(!selected)return;if(currentTab==='tickets')return loadTickets();if(currentTab==='fishing')return loadFishing();if(currentTab==='verification')return loadVerification();if(currentTab==='logs')return loadLogs();if(currentTab==='chat')return loadChat();return loadDetail(!dirtyForms.has('settings-form'));}
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

function selectDM(userId){if(dmUser!==userId&&($('dm-content').value.trim()||selectedFiles('dm').length)&&!confirm('Discard this draft and switch conversations?')){$('dm-user-id').value=dmUser;return;}if(dmUser!==userId){$('dm-content').value='';clearUploads('dm');clearDraft('dm-form');}if(dmUser!==userId){dmRows=[];dmBefore=null;$('dm-messages').replaceChildren();$('dm-older').hidden=true;$('dm-chat-header').textContent='Loading conversation…';$('dm-profile').replaceChildren();}dmUser=userId;$('dm-user-id').value=userId;if(mobileInbox.matches)$('dm-inbox').open=false;void loadDMHistory().catch(error=>showStatus(error.message,'error'));}
function applyCapabilities(){if(busy)return;applyCommunityCapabilities();applyExtraCapabilities();if(!resources)return;applyNewCapabilities();$('chat-files').disabled=true;$('dm-files').disabled=true;const cap=resources.capabilities||{};for(const [selector,key]of [['#roles-form button,#roles-form select','changeRoles'],['#member-role-form button,#assign-role','assignRoles'],['#channel-form button,#control-channel,#slowmode','channels'],['#release-form button,#member-id,#timeout-member','timeout'],['#auto-role','autoRole'],['#settings-form input,#settings-form button,#shield-on,#shield-off,#automatic-on,[data-security-level]','security']]){for(const control of document.querySelectorAll(selector))control.disabled=cap[key]===false;} }

async function loadVerification(){const id=selected;if(!id||dirtyForms.has('verification-form'))return;const data=await api('guilds/'+id+'/verification');if(id!==selected||dirtyForms.has('verification-form'))return;const config=data.settings;$('verification-mode').value=config.mode;$('verification-group-required').checked=config.groupRequired;$('verification-group').value=config.groupId;$('verification-channel').value=config.channelId||'';$('verification-title').value=config.title||'';$('verification-description').value=config.description||'';verificationVisibility();verificationLoaded=id;const can=resources?.capabilities?.changeRoles!==false;for(const input of $('verification-form').querySelectorAll('input,select,textarea,button'))input.disabled=!can;$('verification-note').textContent=can?'Settings apply to '+$('server-name').textContent+'.':'Only the server owner or a Discord administrator can change verification.';}
$('verification-mode').addEventListener('change',verificationVisibility);$('verification-group-required').addEventListener('change',verificationVisibility);
$('verification-form').addEventListener('submit',async event=>{event.preventDefault();const body={mode:$('verification-mode').value,groupRequired:$('verification-group-required').checked,groupId:$('verification-group').value.trim(),channelId:$('verification-channel').value,title:$('verification-title').value,description:$('verification-description').value};const result=await action('guilds/'+selected+'/verification',body,'Verification settings saved.');if(result){clearDraft('verification-form');await loadResources();if(result.warning)showStatus(result.warning,'error');await loadVerification();}});

// Server presets are suggestions: applying one fills a draft, saving applies the change.
let presetGuild='',serverPresets={};
const presetSection=textElement('details','','preset-bar');presetSection.id='preset-bar';presetSection.hidden=true;
const presetSummary=textElement('summary','Presets');presetSummary.append(textElement('small','Start with a preset or save your own.'));
const presetControls=textElement('div','','preset-controls');
const presetCopy=textElement('div','','preset-copy');presetCopy.append(textElement('strong','Make it yours'),textElement('small','Start with a preset, tweak it, then save.'));
const presetSelect=document.createElement('select');presetSelect.id='preset-select';presetSelect.setAttribute('aria-label','Server presets');
const presetUse=textElement('button','Use preset'),presetSave=textElement('button','Save as preset'),presetDelete=textElement('button','Delete preset');for(const button of [presetUse,presetSave,presetDelete])button.type='button';
presetControls.append(presetCopy,presetSelect,presetUse,presetSave,presetDelete);presetSection.append(presetSummary,presetControls);$('workspace-heading').after(presetSection);
const presetTab=()=>({security:'home',channels:'welcome'}[currentTab]||currentTab);
const presetForms={home:'settings-form',verification:'verification-form',roles:'roles-form',embeds:'embed-form',welcome:'welcome-form',fishing:'fishing-form'};
function renderPresetBar(){const tab=presetTab(),items=serverPresets[tab]||[];const previous=presetSection.dataset.tab===tab?presetSelect.value:'';presetSection.dataset.tab=tab;presetSection.hidden=currentTab==='home'||!presetForms[tab]||(currentTab==='roles'&&currentSection!=='permissions')||(currentTab==='channels'&&currentSection!=='welcome')||(currentTab==='embeds'&&currentSection!=='editor')||(currentTab==='fishing'&&currentSection!=='settings');options(presetSelect,items.map(item=>({id:item.id,name:item.name})),'Choose a preset');if(items.length)presetSelect.value=items.some(item=>item.id===previous)?previous:items[0].id;const can=resources?.capabilities?.changeRoles!==false;presetSave.disabled=!can;presetDelete.disabled=!can||!items.length;presetUse.disabled=!items.length;}
async function loadPresets(){if(!selected){presetSection.hidden=true;return;}const id=selected;if(presetGuild!==id){const data=await api('guilds/'+id+'/presets');if(id!==selected)return;serverPresets=data.presets;presetGuild=id;}renderPresetBar();}
function presetControl(form,key){const element=$(key)||form.elements.namedItem(key);return element&&form.contains(element)?element:null;}
presetUse.addEventListener('click',()=>{const tab=presetTab(),form=$(presetForms[tab]),preset=(serverPresets[tab]||[]).find(p=>p.id===presetSelect.value);if(!form||!preset)return;for(const [key,value]of Object.entries(preset.values)){const field=presetControl(form,key);if(!field)continue;if(field.type==='checkbox')field.checked=Boolean(value);else field.value=String(value);}dirtyForms.add(form.id);dirty=true;if(tab==='verification')verificationVisibility();if(tab==='embeds')previewEmbed();syncRanges();showStatus('Preset added to your draft. Adjust it, then save when ready.','success');});
presetDelete.addEventListener('click',async()=>{const tab=presetTab(),items=(serverPresets[tab]||[]).filter(p=>p.id!==presetSelect.value);const result=await action('guilds/'+selected+'/presets',{tab,presets:items},'Preset removed.');if(result){serverPresets=result.presets;renderPresetBar();}});
presetSave.addEventListener('click',async()=>{const tab=presetTab(),form=$(presetForms[tab]);if(!form)return;const items=serverPresets[tab]||[];if(items.length>=6){showStatus('You can keep six presets per tab. Remove one first.','error');return;}const name=prompt('Name this preset');if(!name?.trim())return;const values={};for(const field of form.querySelectorAll('input,select,textarea')){if(field.type==='file'||field.multiple)continue;const key=field.id||field.name;if(key)values[key]=field.type==='checkbox'?field.checked:['number','range'].includes(field.type)?Number(field.value):field.value;}const result=await action('guilds/'+selected+'/presets',{tab,presets:[...items,{id:'custom-'+crypto.randomUUID().slice(0,8),name:name.trim(),values}]},'Preset saved for this server.');if(result){serverPresets=result.presets;renderPresetBar();}});

let ticketDraft=[],ticketPresets=[],ticketPreviewSelection='';
function chosen(select){return [...select.selectedOptions].map(option=>option.value).filter(Boolean);}
function fillMulti(element,roles,selected){options(element,roles,'');element.firstChild.remove();for(const option of element.options)option.selected=selected.includes(option.value);}
const markTicketDraft=()=>{dirtyForms.add('tickets-form');dirty=true;};
function ticketEmoji(value){
 const custom=/^<(a?):([A-Za-z0-9_]{2,32}):(\d{17,20})>$/.exec(value||'');
 const id=custom?.[3]||(/^\d{17,20}$/.test(value||'')?value:null);
 if(id){const img=document.createElement('img');img.src='https://cdn.discordapp.com/emojis/'+id+(custom?.[1]==='a'?'.gif':'.png')+'?size=48';img.alt=custom?.[2]||'Custom emoji';img.className='ticket-topic-emoji';img.loading='lazy';return img;}
 return textElement('span',value||'','ticket-topic-emoji');
}
function ticketPreviewOpen(open,focusIndex){
 const list=$('ticket-preview-options');list.hidden=!open;
 $('ticket-preview-trigger').setAttribute('aria-expanded',String(open));
 if(open&&Number.isInteger(focusIndex)){const options=[...list.querySelectorAll('[role=option]')];if(options.length){const active=(focusIndex+options.length)%options.length;options.forEach((option,index)=>option.tabIndex=index===active?0:-1);options[active].focus();}}
}
function renderTicketPreview(){
 $('ticket-preview-title').textContent=$('tickets-title').value||'Talk to the team';
 $('ticket-preview-description').textContent=$('tickets-description').value;
 const list=$('ticket-preview-options');list.replaceChildren();
 if(!ticketDraft.some(type=>type.id===ticketPreviewSelection))ticketPreviewSelection='';
 $('ticket-preview-selection').replaceChildren();
 const selectedType=ticketDraft.find(type=>type.id===ticketPreviewSelection);
 if(selectedType){if(selectedType.emoji)$('ticket-preview-selection').append(ticketEmoji(selectedType.emoji));$('ticket-preview-selection').append(textElement('span',selectedType.name||'Untitled topic'));}
 else $('ticket-preview-selection').textContent=$('tickets-placeholder').value||'Select a topic';
 const showDescriptions=$('tickets-show-descriptions').checked;
 for(const [index,type]of ticketDraft.entries()){
  const option=textElement('button','','ticket-topic-option');option.type='button';option.id='ticket-preview-option-'+index;option.setAttribute('role','option');option.setAttribute('aria-selected',String(type.id===ticketPreviewSelection));option.dataset.topic=type.id;
  option.tabIndex=type.id===ticketPreviewSelection||(!ticketPreviewSelection&&index===0)?0:-1;
  if(type.emoji)option.append(ticketEmoji(type.emoji));
  const copy=textElement('span','','ticket-topic-copy');copy.append(textElement('strong',type.name||'Untitled topic'));
  if(showDescriptions&&type.description?.trim())copy.append(textElement('small',type.description.slice(0,100)));
  option.append(copy);
  option.addEventListener('click',()=>{ticketPreviewSelection=type.id;renderTicketPreview();ticketPreviewOpen(false);$('ticket-preview-trigger').focus();$('ticket-preview-note').textContent='Preview: choosing '+(type.name||'this topic')+' would open a ticket and start '+(type.questions.length?type.questions.length+' questions':'a conversation')+' in TAGGY DMs.';});
  option.addEventListener('keydown',event=>{if(['ArrowDown','ArrowUp','Home','End','Escape'].includes(event.key)){event.preventDefault();if(event.key==='Escape'){ticketPreviewOpen(false);$('ticket-preview-trigger').focus();return;}ticketPreviewOpen(true,event.key==='Home'?0:event.key==='End'?ticketDraft.length-1:index+(event.key==='ArrowDown'?1:-1));}});
  list.append(option);
 }
 $('ticket-preview-trigger').disabled=!ticketDraft.length;
 $('ticket-preview-note').textContent=ticketDraft.length?'Try the menu here. Your preview does not open a ticket.':'Add a topic to show the menu on your panel.';
 const topic=ticketDraft.find(item=>item.id===ticketPreviewSelection)||ticketDraft.find(item=>item.questions.length);
 $('ticket-question-preview').hidden=!topic?.questions.length;
 if(topic?.questions.length){$('ticket-question-title').textContent='Question 1/'+topic.questions.length+' · '+topic.name;$('ticket-question-copy').textContent=topic.questions[0]+'\n\nSend your answer here in this DM. You can include pictures and files.\n\n0 of '+topic.questions.length+' answered · .question repeats this question · .close ends the ticket';}
 if(!ticketDraft.length)ticketPreviewOpen(false);
}
function renderTicketTypes(){
 const list=$('ticket-types');list.replaceChildren();
 for(const type of ticketDraft){
  type.emoji??='';
  const card=textElement('details','','ticket-type');card.dataset.type=type.id;card.open=type.id==='staff-application'||type.id.startsWith('custom-');
  const summary=textElement('summary',''),name=textElement('strong',type.name||'New topic'),count=textElement('small',type.questions.length?type.questions.length+' questions':'A conversation');
  summary.append(name,count);card.append(summary);
  const heading=textElement('div','','section-heading'),remove=textElement('button','Remove');remove.type='button';remove.addEventListener('click',()=>{ticketDraft=ticketDraft.filter(item=>item!==type);markTicketDraft();renderTicketTypes();});heading.append(remove);card.append(heading);
  for(const [key,label,max,rows]of [['name','Topic name',80,0],['emoji','Emoji',100,0],['description','Topic description',200,0]]){
   const wrapper=textElement('label',label),input=document.createElement(rows?'textarea':'input');if(rows)input.rows=rows;input.maxLength=max;input.value=key==='questions'?type.questions.join('\n'):type[key]||'';input.setAttribute('aria-label',label+' for '+type.name);input.dataset.ticketField=key;
   if(key==='name')input.required=true;
   if(key==='emoji'){input.placeholder='💬 or <:name:id>';wrapper.append(textElement('small','Paste an emoji or a Discord custom emoji. Leave empty to remove it.','caption'));}
   if(key==='description')wrapper.append(textElement('small','The menu shows up to 100 characters when descriptions are enabled.','caption'));
   input.addEventListener('input',()=>{type[key]=key==='questions'?input.value.split('\n').map(line=>line.trim()).filter(Boolean):key==='emoji'?input.value.trim():input.value;name.textContent=type.name||'New topic';count.textContent=type.questions.length?type.questions.length+' questions':'A conversation';markTicketDraft();renderTicketPreview();});wrapper.append(input);card.append(wrapper);
  }
  const questions=textElement('div','','ticket-question-editor');const drawQuestions=()=>{questions.replaceChildren();type.questions.forEach((question,index)=>{const row=textElement('div','','question-editor-row'),label=textElement('label','Question '+(index+1)),input=document.createElement('textarea');input.value=question;input.rows=3;input.maxLength=350;input.required=true;input.dataset.ticketQuestion='';input.setAttribute('aria-label','Question '+(index+1)+' for '+type.name);input.addEventListener('input',()=>{type.questions[index]=input.value;markTicketDraft();renderTicketPreview();});label.append(input);const remove=textElement('button','Remove question '+(index+1));remove.type='button';remove.addEventListener('click',()=>{type.questions.splice(index,1);markTicketDraft();count.textContent=type.questions.length?type.questions.length+' questions':'A conversation';drawQuestions();renderTicketPreview();});row.append(label,remove);questions.append(row);});};drawQuestions();card.append(questions);const addQuestion=textElement('button','Add a question');addQuestion.type='button';addQuestion.addEventListener('click',()=>{if(type.questions.length>=12){showStatus('Use up to 12 questions per topic.','error');return;}type.questions.push('');markTicketDraft();count.textContent=type.questions.length+' questions';drawQuestions();renderTicketPreview();});card.append(addQuestion,textElement('p','Leave questions empty for a conversation. Up to 12 questions, 350 characters each.','caption'));list.append(card);
 }
 if(!ticketDraft.length)list.append(textElement('p','Add a topic or restore the presets to show the menu.','muted'));
 renderTicketPreview();applyNewCapabilities();
}
$('ticket-preview-trigger').addEventListener('click',()=>ticketPreviewOpen($('ticket-preview-options').hidden));
$('ticket-preview-trigger').addEventListener('keydown',event=>{if(event.key==='ArrowDown'||event.key==='ArrowUp'){event.preventDefault();ticketPreviewOpen(true,event.key==='ArrowDown'?0:ticketDraft.length-1);}if(event.key==='Escape'){event.preventDefault();ticketPreviewOpen(false);}});
$('ticket-preview-reset').addEventListener('click',()=>{ticketPreviewSelection='';renderTicketPreview();ticketPreviewOpen(true);});
for(const id of ['tickets-title','tickets-description','tickets-placeholder','tickets-show-descriptions'])$(id).addEventListener('input',renderTicketPreview);
$('tickets-form').addEventListener('input',markTicketDraft);
async function loadTickets(){
 if(!selected||dirtyForms.has('tickets-form'))return;
 const id=selected,data=await api('guilds/'+id+'/tickets');if(id!==selected||dirtyForms.has('tickets-form'))return;
 const config=data.settings;ticketDraft=structuredClone(config.types);ticketPresets=data.presets;ticketPreviewSelection='';
 $('tickets-title').value=config.title;$('tickets-description').value=config.description;
 $('tickets-placeholder').value=config.placeholder||'Select a topic';$('tickets-show-descriptions').checked=Boolean(config.showDescriptions);
 $('tickets-reminders').checked=config.remindersEnabled;$('tickets-days').value=config.reminderDays;
 const roles=(resources?.roles||[]).filter(role=>role.id!==selected);fillMulti($('tickets-staff'),roles,data.staffRoleIds);fillMulti($('tickets-ping'),roles,config.reminderRoleIds);
 renderTicketTypes();ticketPreviewOpen(true);
 const closed=$('closed-tickets');closed.replaceChildren();
 for(const item of data.closed){
  const row=textElement('article','','closed-ticket-row'),copy=textElement('div','');copy.append(textElement('strong',item.name),textElement('small',item.type+(item.closedAt?' · '+new Date(item.closedAt).toLocaleDateString():'')));
  const open=textElement('a','View in Discord ↗');open.href='https://discord.com/channels/'+id+'/'+item.id;open.target='_blank';open.rel='noopener noreferrer';row.append(copy,open);
  if(resources?.capabilities?.changeRoles!==false){const button=textElement('button','Delete channel');button.type='button';button.className='danger';button.addEventListener('click',async()=>{if(!confirm('Permanently delete '+item.name+'? This cannot be undone. Saved transcripts keep their normal retention period.'))return;const result=await action('guilds/'+id+'/ticket-delete',{channelId:item.id,confirmed:true},'Closed ticket channel deleted.');if(result)await loadTickets();});row.append(button);}
  closed.append(row);
 }
 if(!data.closed.length)closed.append(textElement('p','No closed tickets you can view. Closed tickets will appear here.','muted'));applyNewCapabilities();
}
$('ticket-add').addEventListener('click',()=>{if(ticketDraft.length>=10){showStatus('Up to ten topics are supported.','error');return;}ticketDraft.push({id:'custom-'+crypto.randomUUID().slice(0,8),name:'New topic',emoji:'💬',description:'',questions:[]});markTicketDraft();renderTicketTypes();});
$('ticket-defaults').addEventListener('click',()=>{ticketDraft=structuredClone(ticketPresets);markTicketDraft();renderTicketTypes();});
$('tickets-refresh').addEventListener('click',()=>void loadTickets().catch(error=>showStatus(error.message,'error')));
$('tickets-form').addEventListener('submit',async event=>{
 event.preventDefault();
 const result=await action('guilds/'+selected+'/tickets',{settings:{
  title:$('tickets-title').value,description:$('tickets-description').value,placeholder:$('tickets-placeholder').value,
  showDescriptions:$('tickets-show-descriptions').checked,types:ticketDraft,remindersEnabled:$('tickets-reminders').checked,
  reminderDays:Number($('tickets-days').value),reminderRoleIds:chosen($('tickets-ping'))
 },staffRoleIds:chosen($('tickets-staff'))},'Ticket settings saved.');
 if(result){clearDraft('tickets-form');await loadTickets();if(result.warning)showStatus(result.warning,'error');}
});
let fishingData=null,fishingFor='',fishingPlayer=null,fishingPlayerFor='';
function fishingAdminAllowed(){return selected===PROFILE_GUILD_ID&&fishingFor===selected&&fishingData?.canAdmin===true;}
function availableSections(tab){return (workspaceSections[tab]||[]).filter(([id])=>tab!=='fishing'||!['boosts','players'].includes(id)||fishingAdminAllowed());}
function fishingArt(item){const img=document.createElement('img');try{const url=new URL(item.image);if(url.hostname!=='cdn.discordapp.com'||url.protocol!=='https:'||!/^\/emojis\/\d+\.png$/.test(url.pathname))return null;img.src=url.href;}catch{return null;}img.width=64;img.height=64;img.alt='';img.loading='lazy';return img;}
function renderFishingCatalog(){
 const catalog=fishingData?.catalog;if(!catalog)return;
 for(const [key,id]of [['fish','fishing-fish-catalog'],['rods','fishing-rod-catalog']]){const list=$(id);list.replaceChildren();for(const item of catalog[key]||[]){const card=textElement('article','','fishing-item'),art=fishingArt(item);if(art)card.append(art);card.append(textElement('strong',item.name),textElement('span',key==='fish'?item.rarity:item.price?item.price.toLocaleString()+' coins':'Your first rod','caption'));if(key==='fish')card.append(textElement('small',item.value.toLocaleString()+' sale coins'));list.append(card);}}
 $('fishing-upgrade-catalog').replaceChildren();for(const upgrade of catalog.upgrades||[]){const card=textElement('article','','fishing-upgrade');card.append(textElement('h4',upgrade.emoji+' '+upgrade.name),textElement('p',upgrade.description),textElement('small','Five levels · /fishupgrades','caption'));$('fishing-upgrade-catalog').append(card);}
}
function renderFishingBoost(){const boost=fishingData?.boost;$('fishing-boost-status').textContent=boost?.until>Date.now()?boost.xp+'× catch XP · '+boost.coins+'× sale coins · '+boost.luck+'× rare pool weight. Ends '+new Date(boost.until).toLocaleString()+'.':'No active boost.';}
async function loadFishing(){
 if(!selected)return;const id=selected,data=await api('guilds/'+id+'/fishing');if(id!==selected)return;
 fishingData=data;fishingFor=id;if(!dirtyForms.has('fishing-form')){$('fishing-enabled').checked=data.settings.enabled;$('fishing-cooldown').value=data.settings.cooldownSeconds;}
 renderFishingCatalog();renderFishingBoost();normalizeWorkspace();renderSections();applyNewCapabilities();applyFishingCapabilities();
}
function applyFishingCapabilities(){
 const can=fishingFor===selected&&fishingData?.canAdmin===true&&fishingAdminAllowed()&&!busy;
 for(const form of ['fishing-boost-form','fishing-player-lookup','fishing-player-form'])for(const element of $(form).querySelectorAll('input,select,button'))element.disabled=!can||(form==='fishing-player-form'&&fishingPlayerFor!==selected);
 $('fishing-stop-boost').disabled=!can||!(fishingData?.boost?.until>Date.now());
}
async function saveFishingBoost(enabled){if(!fishingAdminAllowed())return;const id=selected,body=enabled?{enabled:true,xp:Number($('fishing-boost-xp').value),coins:Number($('fishing-boost-coins').value),luck:Number($('fishing-boost-luck').value),minutes:Number($('fishing-boost-minutes').value)}:{enabled:false};const result=await action('guilds/'+id+'/fishing-boost',body,enabled?'Fishing boost started.':'Fishing boost stopped.');if(result&&selected===id){clearDraft('fishing-boost-form');await loadFishing();}}
async function loadFishingPlayer(){
 const id=selected,memberId=$('fishing-player-id').value.trim();if(!fishingAdminAllowed()||!/^\d{1,20}$/.test(memberId))return;
 try{const data=await api('guilds/'+id+'/fishing-player?memberId='+encodeURIComponent(memberId));if(selected!==id||$('fishing-player-id').value.trim()!==memberId)return;
 fishingPlayer=data.player;fishingPlayerFor=id;clearDraft('fishing-player-form');clearDraft('fishing-player-lookup');$('fishing-player-profile').replaceChildren(avatar(data.member),textElement('strong',data.member.name),textElement('span','Level '+data.player.level+' · '+memberId,'caption'));
 for(const key of ['coins','xp','bait','casts','catches','biggest'])$('fishing-player-'+key).value=data.player[key];
 for(const key of ['reel','tackle','charm'])$('fishing-player-'+key).value=data.player.upgrades[key];
 const select=$('fishing-player-rod');select.replaceChildren();for(const rod of fishingData.catalog.rods){const option=textElement('option',rod.name);option.value=rod.id;select.append(option);}select.value=data.player.rod;
 const species=$('fishing-player-fish');species.replaceChildren();for(const fish of fishingData.catalog.fish){const option=textElement('option',fish.name);option.value=fish.id;species.append(option);}$('fishing-player-quantity').value=data.player.fish[species.value]||0;$('fishing-player-change-fish').checked=false;
 $('fishing-player-form').hidden=false;applyFishingCapabilities();
 }catch(error){showStatus(error.message,'error');}
}
$('fishing-boost-form').addEventListener('submit',event=>{event.preventDefault();void saveFishingBoost(true);});
$('fishing-stop-boost').addEventListener('click',()=>void saveFishingBoost(false));
$('fishing-player-lookup').addEventListener('submit',event=>{event.preventDefault();if(dirtyForms.has('fishing-player-form')&&!confirm('Reload player and discard your unsaved changes?'))return;void loadFishingPlayer();});
$('fishing-player-reload').addEventListener('click',()=>{if(dirtyForms.has('fishing-player-form')&&!confirm('Reload player and discard your unsaved changes?'))return;void loadFishingPlayer();});
$('fishing-player-fish').addEventListener('change',()=>{$('fishing-player-quantity').value=fishingPlayer?.fish[$('fishing-player-fish').value]||0;});
$('fishing-player-id').addEventListener('input',()=>{fishingPlayer=null;fishingPlayerFor='';$('fishing-player-form').hidden=true;$('fishing-player-profile').replaceChildren();applyFishingCapabilities();});
$('fishing-player-form').addEventListener('submit',async event=>{
 event.preventDefault();if(!fishingAdminAllowed()||fishingPlayerFor!==selected||!fishingPlayer)return;
 const id=selected,body={memberId:fishingPlayer.id,revision:fishingPlayer.revision,rod:$('fishing-player-rod').value,upgrades:{}};
 for(const key of ['coins','xp','bait','casts','catches','biggest'])body[key]=Number($('fishing-player-'+key).value);
 for(const key of ['reel','tackle','charm'])body.upgrades[key]=Number($('fishing-player-'+key).value);
 if($('fishing-player-change-fish').checked)body.fish={[$('fishing-player-fish').value]:Number($('fishing-player-quantity').value)};
 const result=await action('guilds/'+id+'/fishing-player',body,'Player progress saved.');if(result&&selected===id){clearDraft('fishing-player-form');await loadFishingPlayer();}
});

$('fishing-form').addEventListener('submit',async event=>{event.preventDefault();const result=await action('guilds/'+selected+'/fishing',{enabled:$('fishing-enabled').checked,cooldownSeconds:Number($('fishing-cooldown').value)},'Fishing settings saved.');if(result){clearDraft('fishing-form');await loadFishing();}});
function applyNewCapabilities(){applyFishingCapabilities();const can=resources?.capabilities?.changeRoles!==false&&!busy;for(const element of document.querySelectorAll('#tickets-form input,#tickets-form textarea,#tickets-form select,#tickets-form button,#fishing-form input,#fishing-form button'))element.disabled=!can;$('tickets-note').textContent=can?'Save to publish the panel. Open tickets keep their original questions.':'Only the server owner or a Discord administrator can change tickets.';}

// Pause media out of view. Reduced-motion users get manual controls and static examples.
const reducedMotion=matchMedia('(prefers-reduced-motion: reduce)');
const ambientVideo=$('ambient-video'),ambientToggle=$('ambient-toggle'),ambientMobile=matchMedia('(max-width:700px)');
const dataConnection=navigator.connection;
let ambientVisible=false,ambientPaused=false;
try{ambientPaused=sessionStorage.getItem('taggy-background-paused')==='true';}catch(_){}
function syncAmbient(){
 const allowed=!reducedMotion.matches&&!dataConnection?.saveData;
 ambientToggle.hidden=!allowed;
 ambientToggle.textContent=ambientPaused?'Play motion':'Pause motion';
 ambientToggle.setAttribute('aria-pressed',String(ambientPaused));
 const shouldPlay=allowed&&ambientVisible&&!ambientPaused&&!document.hidden&&!document.body.classList.contains('signed-in');
 if(shouldPlay){
  const source='/taggy/assets/taggy-ambient'+(ambientMobile.matches?'-mobile':'')+'.mp4';
  if(ambientVideo.getAttribute('src')!==source)ambientVideo.src=source;
  void ambientVideo.play().catch(()=>ambientVideo.classList.remove('is-playing'));
 }else{ambientVideo.pause();ambientVideo.classList.remove('is-playing');}
}
ambientVideo.addEventListener('playing',()=>{
 if(!ambientVisible||ambientPaused||document.hidden||reducedMotion.matches||dataConnection?.saveData||document.body.classList.contains('signed-in')){ambientVideo.pause();ambientVideo.classList.remove('is-playing');}
 else ambientVideo.classList.add('is-playing');
});
ambientVideo.addEventListener('error',()=>{ambientVideo.classList.remove('is-playing');ambientToggle.hidden=true;});
ambientToggle.addEventListener('click',()=>{ambientPaused=!ambientPaused;try{sessionStorage.setItem('taggy-background-paused',String(ambientPaused));}catch(_){}syncAmbient();});
ambientMobile.addEventListener('change',syncAmbient);
dataConnection?.addEventListener('change',syncAmbient);
new IntersectionObserver(entries=>{ambientVisible=entries[0].isIntersecting;syncAmbient();},{threshold:0.05}).observe(document.querySelector('.centered-intro'));
document.addEventListener('visibilitychange',syncAmbient);
reducedMotion.addEventListener('change',syncAmbient);
syncAmbient();
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

function syncRanges(){for(const field of document.querySelectorAll('#settings-form input[type=range]'))field.previousElementSibling.querySelector('output').textContent=field.value;}
$('settings-form').addEventListener('input',syncRanges);
for(const button of document.querySelectorAll('[data-open-tool]'))button.addEventListener('click',()=>chooseTool(button.dataset.openTool));
const securityLevels={
 relaxed:{joinLimit:15,messageLimit:12,duplicateLimit:8,mentionLimit:10,timeoutMinutes:5,destructiveLimit:5,linkLimit:10,fileLimit:15,emojiLimit:50,creationLimit:15},
 standard:{joinLimit:8,messageLimit:7,duplicateLimit:5,mentionLimit:6,timeoutMinutes:10,destructiveLimit:3,linkLimit:5,fileLimit:8,emojiLimit:30,creationLimit:8},
 strict:{joinLimit:5,messageLimit:5,duplicateLimit:3,mentionLimit:4,timeoutMinutes:15,destructiveLimit:2,linkLimit:3,fileLimit:5,emojiLimit:20,creationLimit:5}
};
for(const button of document.querySelectorAll('[data-security-level]'))button.addEventListener('click',()=>{
 const values={...securityLevels[button.dataset.securityLevel],joinWindowSeconds:10,messageWindowSeconds:5,shieldMinutes:10,destructiveWindowSeconds:10};
 for(const [key,value]of Object.entries(values)){const field=$('settings-form').elements.namedItem(key);if(field&&supportedSettings.has(key))field.value=value;}
 dirtyForms.add('settings-form');dirty=true;syncRanges();showStatus(button.textContent+' limits added to your draft. Save protection to apply them.','success');
});
function renderActivity(data){
 const activity=data.activity,events=(data.incidents||[]).filter(item=>item.at>Date.now()-86400000);
 const protection=events.filter(item=>['Spam','Webhook flood','New account','Join raid','Join restriction','Destructive activity','Mass creation'].includes(item.type)).length;
 $('activity-stats').replaceChildren();
 for(const [label,value,note]of [['Members',data.memberCount,'In your server now'],['Messages',activity?.messages,'Last 24 hours'],['Joined',activity?.joins,'Last 24 hours'],['Left',activity?.leaves,'Last 24 hours'],['Protection events',protection,'Last 24 hours']]){
  const card=textElement('article','','activity-stat');card.append(textElement('span',label),textElement('strong',value===undefined?'Pending':value.toLocaleString()),textElement('small',note));$('activity-stats').append(card);
 }
 $('activity-total').textContent=activity?activity.messages.toLocaleString()+' messages':'Bot update needed';
 $('activity-chart').replaceChildren();const max=Math.max(1,...(activity?.hourly||[]).map(item=>item.messages));
 for(const item of activity?.hourly||[]){const bar=textElement('div','','activity-hour');bar.setAttribute('role','listitem');const time=new Date(item.at).toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'});bar.setAttribute('aria-label',time+': '+item.messages+' messages');bar.title=time+': '+item.messages+' messages';const fill=textElement('span','','activity-bar');const h=Math.max(2,Math.round(item.messages/max*100));fill.setAttribute('data-height',String(h));bar.append(fill,textElement('small',time.slice(0,2)));$('activity-chart').append(bar);}
 $('activity-note').textContent=activity?'Human messages, joins and leaves. Counts start when this bot update is installed. Updates every 15 seconds.':'Install the bot update to start recording activity.';
 $('activity-tickets').replaceChildren();
 if(data.tickets){for(const [key,label]of [['open','Open'],['waitingAnswers','Answering questions'],['claimed','Picked up by staff'],['closedToday','Closed in 24 hours']]){const row=textElement('div');row.append(textElement('span',label),textElement('strong',String(data.tickets[key])));$('activity-tickets').append(row);}}
 else $('activity-tickets').append(textElement('p','Ticket counts appear after the bot update.','muted'));
 $('activity-events').replaceChildren();
 for(const event of events.slice(0,6)){const row=textElement('article','','activity-event');const body=textElement('div');body.append(textElement('strong',event.type),textElement('small',event.detail));row.append(body,textElement('time',new Date(event.at).toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'})));$('activity-events').append(row);}
 if(!events.length)$('activity-events').append(textElement('p','Quiet so far. New server events will appear here.','muted'));
}


let scheduleData=null,scheduleId='',scheduleLoading='',scheduleDateOriginal=null,welcomeDMData=null,welcomeDMLoading='',commandData=null,commandsLoading='';
let setupData=null,setupFor='',setupLoading='';
let giveawayData=null,giveawayFor='',giveawayLoading='',giveawayUncertain=new Set(),giveawayChecked=false;
const featureReady=key=>resources?.features?.[key]===true;
const setupStatus={ready:'Ready',needs_setup:'Needs setup',blocked:'Check permissions',off:'Off',unknown:'Check again'};
function renderSetup(data){
 const items=Array.isArray(data.items)?data.items:[];
 $('setup-items').replaceChildren();
 for(const item of items){
  const status=Object.hasOwn(setupStatus,item.status)?item.status:'unknown',row=textElement('article','','card setup-item');row.dataset.setupItem=String(item.id||'');row.dataset.setupStatus=status;
  const heading=textElement('div','','section-heading');heading.append(textElement('h4',item.name||'Setup check'),textElement('span',setupStatus[status],'setup-state '+status));
  row.append(heading,textElement('p',item.description||'Check this feature’s settings.','muted'));
  const action=item.action,sections=workspaceSections[action?.tab];
  if(item.canFix===true&&action&&allowedTool(action.tab)&&(!sections||sections.some(([id])=>id===action.section))){
   const link=textElement('a',(action.label||'Open settings')+' ↗','button quiet setup-link');link.href=dashboardURL(action.tab,action.section||'').href;link.setAttribute('aria-label',(action.label||'Open settings')+' for '+(item.name||'this check'));
   link.addEventListener('click',event=>{if(event.button||event.metaKey||event.ctrlKey||event.shiftKey||event.altKey)return;event.preventDefault();chooseTool(action.tab,action.section||'');});row.append(link);
  }
  $('setup-items').append(row);
 }
 if(!items.length)$('setup-items').append(textElement('p','No setup checks are available yet. Try Check again.','muted'));
 const ready=items.filter(item=>item.status==='ready').length,off=items.filter(item=>item.status==='off').length,toCheck=items.length-ready-off;
 $('setup-progress').hidden=!items.length;$('setup-progress-label').textContent=ready+' ready · '+toCheck+' to check'+(off?' · '+off+' off':'');
 $('setup-progress-bar').max=Math.max(1,items.length-off);$('setup-progress-bar').value=ready;
 const checkedAt=new Date(data.checkedAt);$('setup-checked').textContent=Number.isFinite(checkedAt.getTime())?'Last checked '+checkedAt.toLocaleString():'';
 for(const [key,id]of [['bot','setup-bot-permissions'],['account','setup-account-permissions']]){
  const list=$(id);list.replaceChildren();
  for(const permission of Array.isArray(data.permissions?.[key])?data.permissions[key]:[]){const row=textElement('li'),granted=permission.granted===true?'Allowed':permission.granted===false?'Missing':'Unknown';row.append(textElement('span',permission.name||'Permission'),textElement('strong',granted,'setup-permission-'+granted.toLowerCase()));list.append(row);}
  if(!list.children.length)list.append(textElement('li','Permissions could not be checked.','muted'));
 }
 $('setup-permissions').hidden=!data.permissions;
 $('setup-note').textContent=!items.length?'Try Check again to refresh this server.':toCheck?toCheck+' '+(toCheck===1?'item needs':'items need')+' a look. Choose one below.':'You’re all caught up.';$('setup-note').className='notice';
}
async function loadSetup(){
 const id=selected;if(!id)return;if(resourcesFor!==id)await loadResources();if(selected!==id)return;
 if(!featureReady('setup')){setupData=null;setupFor='';$('setup-items').replaceChildren();$('setup-progress').hidden=true;$('setup-permissions').hidden=true;$('setup-note').textContent='Upload the bot update to enable setup checks.';$('setup-note').className='notice';applyExtraCapabilities();return;}
 if(setupLoading===id)return;setupLoading=id;$('setup-items').setAttribute('aria-busy','true');applyExtraCapabilities();
 if(setupFor!==id){setupData=null;$('setup-items').replaceChildren();$('setup-progress').hidden=true;$('setup-permissions').hidden=true;$('setup-note').textContent='Checking your server…';$('setup-note').className='notice';}
 try{const data=await api('guilds/'+id+'/setup');if(selected!==id)return;setupData=data;setupFor=id;renderSetup(data);}
 catch(error){if(selected!==id)return;$('setup-note').textContent='Could not refresh setup. '+error.message;$('setup-note').className='notice error';throw error;}
 finally{if(setupLoading===id)setupLoading='';if(selected===id)$('setup-items').setAttribute('aria-busy','false');applyExtraCapabilities();}
}
$('refresh-setup').addEventListener('click',()=>{if(!busy)void loadSetup().catch(error=>showStatus(error.message,'error'));});
function applyExtraCapabilities(){
 applyGiveawayCapabilities();
 const schedules=featureReady('schedules'),canSchedule=schedules&&scheduleData?.canManage===true;
 disableForm('schedule-form',!canSchedule);$('new-schedule').disabled=!canSchedule||((scheduleData?.schedules||[]).length>=20);$('schedule-picker').disabled=!schedules||!scheduleData;
 $('delete-schedule').disabled=!canSchedule||!scheduleId;
 disableForm('welcome-dm-form',!featureReady('welcomeDM')||welcomeDMData?.canManage!==true);
 for(const control of [$('command-search'),$('command-category')])control.disabled=!featureReady('commands');
 for(const button of document.querySelectorAll('[data-edit-schedule]'))button.disabled=!canSchedule;
 for(const button of document.querySelectorAll('[data-toggle-schedule]'))button.disabled=!canSchedule||!featureReady('scheduleToggle')||button.dataset.sending==='true';
 $('refresh-setup').disabled=!featureReady('setup')||Boolean(setupLoading);
}
function localDateInput(timestamp){const date=new Date(timestamp);if(!Number.isFinite(date.getTime()))return '';const pad=value=>String(value).padStart(2,'0');return date.getFullYear()+'-'+pad(date.getMonth()+1)+'-'+pad(date.getDate())+'T'+pad(date.getHours())+':'+pad(date.getMinutes());}
function scheduleChannels(){
 const picked=$('schedule-channel').value;options($('schedule-channel'),scheduleData?.channels||[],'Choose channel');
 for(const option of [...$('schedule-channel').options].slice(1)){const channel=scheduleData.channels.find(item=>item.id===option.value);if(!channel.canSend){option.disabled=true;option.textContent=channel.name+' · '+(channel.reason||'Sending unavailable');}}
 $('schedule-channel').value=picked;
}
function fillSchedule(schedule){
 scheduleId=schedule?.id||'';$('schedule-picker').value=scheduleId;$('schedule-name').value=schedule?.name||'';$('schedule-channel').value=schedule?.channelId||'';
 const repeat=String(schedule?.repeatMinutes||0);for(const option of [...$('schedule-repeat').querySelectorAll('[data-custom-repeat]')])option.remove();
 if(![...$('schedule-repeat').options].some(option=>option.value===repeat)){const option=textElement('option','Every '+repeat+' minutes');option.value=repeat;option.dataset.customRepeat='true';$('schedule-repeat').append(option);}
 $('schedule-repeat').value=repeat;const nextRunAt=schedule?.nextRunAt||Date.now()+3600000;$('schedule-time').value=localDateInput(nextRunAt);scheduleDateOriginal={value:$('schedule-time').value,nextRunAt};
 $('schedule-content').value=schedule?.content||'';$('schedule-enabled').checked=schedule?.enabled===true;applyExtraCapabilities();
}
function selectSchedule(id,forceNew=false){
 if(busy)return;if(id===scheduleId&&!forceNew&&dirtyForms.has('schedule-form'))return;
 if((id!==scheduleId||forceNew)&&dirtyForms.has('schedule-form')&&!confirm('Discard this post’s unsaved changes?')){$('schedule-picker').value=scheduleId;return;}
 clearDraft('schedule-form');fillSchedule(scheduleData?.schedules.find(schedule=>schedule.id===id));
}
const scheduleStatus=status=>({sent:'Posted',success:'Posted',failed:'Could not post',error:'Could not post',skipped:'Skipped during downtime',missed:'Skipped during downtime',uncertain:'Check delivery',paused:'Paused',pending:'Waiting',scheduled:'Waiting',sending:'Posting'}[status]||String(status||'Not posted yet'));
function scheduleMessageLink(schedule){
 try{const url=new URL(schedule.messageUrl);if(url.protocol!=='https:'||url.hostname!=='discord.com'||!new RegExp('^/channels/'+selected+'/[0-9]+/[0-9]+$').test(url.pathname))return null;const link=textElement('a','View in Discord ↗');link.href=url.href;link.target='_blank';link.rel='noopener noreferrer';return link;}catch(_){return null;}
}
function renderSchedules(){
 const schedules=scheduleData?.schedules||[];$('schedule-count').textContent=schedules.length+' / 20 posts';$('schedule-list').replaceChildren();$('schedule-history').replaceChildren();
 for(const schedule of [...schedules].sort((a,b)=>a.nextRunAt-b.nextRunAt)){
  const row=textElement('article','','schedule-row'),body=textElement('div'),channel=scheduleData.channels.find(item=>item.id===schedule.channelId)?.name||'Unavailable channel';
  const repeat=schedule.repeatMinutes?({60:'Hourly',1440:'Daily',10080:'Weekly'}[schedule.repeatMinutes]||'Every '+schedule.repeatMinutes+' minutes'):'One time';
  body.append(textElement('h4',schedule.name),textElement('p','#'+channel+' · '+repeat,'caption'),textElement('p',(schedule.enabled?'Next: ':'Paused · ')+new Date(schedule.nextRunAt).toLocaleString(),'caption'));
  if(schedule.lastStatus==='sending')body.append(textElement('p','Posting now. Pause becomes available when it finishes.','caption'));
  const actions=textElement('div','','schedule-actions'),edit=textElement('button','Edit');edit.type='button';edit.dataset.editSchedule=schedule.id;edit.setAttribute('aria-label','Edit '+schedule.name);edit.addEventListener('click',()=>selectSchedule(schedule.id));actions.append(edit);
  if(featureReady('scheduleToggle')){const toggle=textElement('button',schedule.enabled?'Pause':'Resume');toggle.type='button';toggle.dataset.toggleSchedule=schedule.id;toggle.dataset.sending=String(schedule.lastStatus==='sending');toggle.setAttribute('aria-label',(schedule.enabled?'Pause ':'Resume ')+schedule.name);toggle.addEventListener('click',()=>{void toggleSchedule(schedule.id,!schedule.enabled);});actions.append(toggle);}
  row.append(body,actions);$('schedule-list').append(row);
 }
 if(!schedules.length)$('schedule-list').append(textElement('p','Your first scheduled post goes here. Start with New post.','muted'));
 for(const schedule of [...schedules].filter(item=>item.lastRunAt>0).sort((a,b)=>(b.lastRunAt||0)-(a.lastRunAt||0))){
  const row=textElement('article','','schedule-history-row'),heading=textElement('div','','section-heading');heading.append(textElement('h4',schedule.name),textElement('span',scheduleStatus(schedule.lastStatus),'schedule-result'));
  row.append(heading,textElement('p',schedule.lastRunAt?new Date(schedule.lastRunAt).toLocaleString():'Time unavailable','caption'));
  if(schedule.lastError)row.append(textElement('p',schedule.lastError,'notice error'));const link=scheduleMessageLink(schedule);if(link)row.append(link);$('schedule-history').append(row);
 }
 if(!$('schedule-history').children.length)$('schedule-history').append(textElement('p','Results appear here after TAGGY tries a scheduled post.','muted'));applyExtraCapabilities();
}
async function toggleSchedule(id,enabled){
 if(busy||!featureReady('scheduleToggle')||scheduleData?.canManage!==true)return;
 const guildId=selected,schedule=scheduleData.schedules.find(item=>item.id===id);if(!schedule||schedule.lastStatus==='sending')return;
 const result=await action('guilds/'+guildId+'/schedules',{action:'toggle',id,enabled},enabled?'Scheduled post resumed.':'Scheduled post paused.');
 if(!result||selected!==guildId)return;
 // Apply the server response before refreshing. A failed read must never invite a second mutation.
 if(Array.isArray(result.schedules))scheduleData.schedules=result.schedules;
 else if(result.schedule)scheduleData.schedules=scheduleData.schedules.map(item=>item.id===id?result.schedule:item);
 renderSchedules();
 if(!dirtyForms.has('schedule-form')&&scheduleId===id)fillSchedule(scheduleData.schedules.find(item=>item.id===id));
 try{await loadSchedules();}catch(error){showStatus((enabled?'Post resumed. ':'Post paused. ')+'Refresh failed: '+error.message,'error');}
}
async function loadSchedules(){
 if(!selected)return;if(resourcesFor!==selected)await loadResources();
 if(!featureReady('schedules')){for(const id of ['schedule-note','schedule-history-note'])$(id).textContent='Upload the bot update to enable scheduled posts.';applyExtraCapabilities();return;}
 const id=selected;if(scheduleLoading===id)return;scheduleLoading=id;
 try{const data=await api('guilds/'+id+'/schedules');if(id!==selected)return;scheduleData=data;
  const picked=$('schedule-picker').value;options($('schedule-picker'),data.schedules,'New post');$('schedule-picker').value=picked;scheduleChannels();renderSchedules();
  if(!dirtyForms.has('schedule-form')){const existing=data.schedules.find(schedule=>schedule.id===scheduleId);fillSchedule(existing);}
  $('schedule-note').textContent=data.canManage?'Choose a post to edit or create a new one. New posts start paused.':'You can view posts. Manage Server and channel access are required to edit them.';
  $('schedule-history-note').textContent='Latest results refresh every 15 seconds. Deleted posts leave this list.';
 }catch(error){$('schedule-note').textContent=error.message;$('schedule-history-note').textContent=error.message;throw error;}finally{if(scheduleLoading===id)scheduleLoading='';applyExtraCapabilities();}
}
$('new-schedule').addEventListener('click',()=>selectSchedule('',true));$('schedule-picker').addEventListener('change',event=>selectSchedule(event.target.value));
$('schedule-form').addEventListener('submit',async event=>{
 event.preventDefault();if(!featureReady('schedules')||scheduleData?.canManage!==true)return;
 const timeValue=$('schedule-time').value,nextRunAt=timeValue===scheduleDateOriginal?.value?scheduleDateOriginal.nextRunAt:new Date(timeValue).getTime();
 const retainedPausedDate=scheduleId&&!$('schedule-enabled').checked&&nextRunAt===scheduleData?.schedules.find(schedule=>schedule.id===scheduleId)?.nextRunAt;
 if(!Number.isFinite(nextRunAt)||(!retainedPausedDate&&(nextRunAt<Date.now()+30000||nextRunAt>Date.now()+365*86400000))){showStatus('Choose a time at least 30 seconds from now and within the next year.','error');$('schedule-time').focus();return;}
 const schedule={name:$('schedule-name').value.trim(),channelId:$('schedule-channel').value,content:$('schedule-content').value,nextRunAt,repeatMinutes:Number($('schedule-repeat').value),enabled:$('schedule-enabled').checked};if(scheduleId)schedule.id=scheduleId;
 const result=await action('guilds/'+selected+'/schedules',{action:'save',schedule},'Scheduled post saved.');if(result){scheduleId=result.schedule?.id||scheduleId;clearDraft('schedule-form');await loadSchedules();}
});
$('delete-schedule').addEventListener('click',async()=>{if(!scheduleId||!featureReady('schedules')||scheduleData?.canManage!==true||!confirm('Delete this scheduled post? Messages already posted in Discord stay there.'))return;const result=await action('guilds/'+selected+'/schedules',{action:'delete',id:scheduleId,confirmed:true},'Scheduled post deleted.');if(result){scheduleId='';clearDraft('schedule-form');await loadSchedules();}});
async function loadWelcomeDM(){
 if(!selected)return;if(resourcesFor!==selected)await loadResources();if(!featureReady('welcomeDM')){$('welcome-dm-note').textContent='Upload the bot update to enable welcome DMs.';applyExtraCapabilities();return;}
 const id=selected;if(welcomeDMLoading===id)return;welcomeDMLoading=id;
 try{const data=await api('guilds/'+id+'/welcome-dm');if(id!==selected)return;welcomeDMData=data;if(!dirtyForms.has('welcome-dm-form')){$('welcome-dm-enabled').checked=data.settings.enabled===true;$('welcome-dm-message').value=data.settings.message||'';}
  $('welcome-dm-note').textContent=data.canManage?'Off by default. Save your message and turn it on when you’re ready.':'Manage Server is required to change welcome DMs.';
 }catch(error){$('welcome-dm-note').textContent=error.message;throw error;}finally{if(welcomeDMLoading===id)welcomeDMLoading='';applyExtraCapabilities();}
}
$('welcome-dm-form').addEventListener('submit',async event=>{event.preventDefault();if(!featureReady('welcomeDM')||welcomeDMData?.canManage!==true)return;const body={enabled:$('welcome-dm-enabled').checked,message:$('welcome-dm-message').value};if(body.enabled&&!body.message.trim()){showStatus('Write a welcome message before turning on DMs.','error');$('welcome-dm-message').focus();return;}const result=await action('guilds/'+selected+'/welcome-dm',body,'Welcome DM saved.');if(result){clearDraft('welcome-dm-form');await loadWelcomeDM();}});
function renderCommands(){
 const query=$('command-search').value.trim().toLocaleLowerCase(),category=$('command-category').value;
 const commands=(commandData?.commands||[]).filter(command=>(!category||command.category===category)&&[command.name,command.usage,command.description,command.category,command.access].join(' ').toLocaleLowerCase().includes(query));
 $('command-count').textContent=commands.length+' '+(commands.length===1?'command':'commands');$('command-list').replaceChildren();
 for(const command of commands){
  const row=textElement('article','','command-row'),heading=textElement('div','','section-heading');heading.append(textElement('h4',command.name),textElement('span',command.category,'caption'));row.append(heading,textElement('code',command.usage,'command-usage'),textElement('p',command.description),textElement('p',command.access,'caption'));
  const contexts=(command.contexts||[]).map(context=>({server:'Server channels',dm:'DMs',app:'Apps'}[context])).filter(Boolean);if(contexts.length)row.append(textElement('p',contexts.join(' · '),'caption'));
  const actions=textElement('div','','actions'),copy=textElement('button','Copy command');copy.type='button';copy.setAttribute('aria-label','Copy '+command.name+' command');copy.addEventListener('click',async()=>{try{await navigator.clipboard.writeText(command.usage);showStatus('Command copied. Paste it in Discord.','success');}catch(_){showStatus('Command to copy: '+command.usage);}});actions.append(copy);
  const target=command.link;if(target&&allowedTool(target.tab)&&(!target.section||(workspaceSections[target.tab]||[]).some(([id])=>id===target.section))){const link=textElement('a','Open settings ↗','button');link.href=dashboardURL(target.tab,target.section||'').href;link.addEventListener('click',event=>{if(event.button||event.ctrlKey||event.metaKey||event.shiftKey||event.altKey)return;event.preventDefault();chooseTool(target.tab,target.section||'');});actions.append(link);}
  row.append(actions);$('command-list').append(row);
 }
 if(!commands.length)$('command-list').append(textElement('p',query||category?'No commands match. Try another word or category.':'Commands appear here when the bot update is connected.','muted'));
}
async function loadCommands(){
 if(!selected)return;if(resourcesFor!==selected)await loadResources();if(!featureReady('commands')){$('commands-note').textContent='Upload the bot update to see the command guide.';applyExtraCapabilities();return;}
 const id=selected;if(commandsLoading===id)return;commandsLoading=id;
 try{const data=await api('guilds/'+id+'/commands');if(id!==selected)return;commandData=data;const picked=$('command-category').value,categories=[...new Set(data.commands.map(command=>command.category).filter(Boolean))];options($('command-category'),categories.map(category=>({id:category,name:category})),'All categories');$('command-category').value=picked;renderCommands();$('commands-note').textContent='Use these in Discord. Your server roles and channel permissions still apply.';
 }catch(error){$('commands-note').textContent=error.message;throw error;}finally{if(commandsLoading===id)commandsLoading='';applyExtraCapabilities();}
}
$('command-search').addEventListener('input',renderCommands);$('command-category').addEventListener('change',renderCommands);
applyExtraCapabilities();

let profileSupported=false, rolePanelData=null, toolData=null, rolePanelId='', panelDraft=[], replyDraft=[];
const communityDirty=id=>{dirtyForms.add(id);dirty=true;};
function communityChannels(){
 for(const id of ['role-panel-channel','poll-channel','send-reply-channel']){
  const picked=$(id).value;options($(id),(resources?.channels||[]).filter(c=>c.canSend),'Choose channel');$(id).value=picked;
 }
}
function disableForm(id,disabled){for(const control of $(id).querySelectorAll('input,select,textarea,button'))control.disabled=disabled;}
function applyCommunityCapabilities(){
 const panels=resources?.features?.rolePanels===true,tools=resources?.features?.tools===true;
 disableForm('role-panel-form',!panels||!rolePanelData?.canManage);$('new-role-panel').disabled=!panels||!rolePanelData?.canManage;
 $('role-panel-picker').disabled=!panels;$('close-role-panel').disabled=!panels||!rolePanelData?.canManage||!rolePanelId;
 for(const id of ['poll-form','replies-form'])disableForm(id,!tools||!toolData?.capabilities?.manage);
 if(tools&&Array.isArray(toolData?.pollChannels)&&!toolData.pollChannels.some(channel=>channel.canPoll))disableForm('poll-form',true);
 disableForm('send-reply-form',!tools||!toolData?.replies?.length);
 disableForm('nickname-form',!tools||!toolData?.capabilities?.nickname);disableForm('member-profile-form',!tools);
 disableForm('bot-profile-form',!profileAllowed()||!profileSupported);
}
async function loadCommunityTab(){
 if(currentTab==='profile'){
  $('bot-profile-note').textContent=profileSupported?'Your name and status settings.':'Upload the bot update to enable profile controls.';applyCommunityCapabilities();
  if(!profileAllowed()||!profileSupported||dirtyForms.has('bot-profile-form'))return;
  const profileGuild=selected;const data=await api('owner/profile?guildId='+encodeURIComponent(profileGuild));if(!profileAllowed()||selected!==profileGuild||dirtyForms.has('bot-profile-form'))return;
  const config=data.profile||data;$('bot-username').value=config.username;$('bot-status').value=config.status;$('bot-activity').value=config.activityType;return;
 }
 if(!selected)return;if(resourcesFor!==selected)await loadResources();const id=selected;
 if(currentTab==='roles'&&currentSection==='panels'){
  if(resources?.features?.rolePanels!==true){$('role-panel-note').textContent='Upload the bot update to enable role panels.';applyCommunityCapabilities();return;}
  if(dirtyForms.has('role-panel-form'))return;
  const data=await api('guilds/'+id+'/role-panels');if(id!==selected||dirtyForms.has('role-panel-form'))return;
  rolePanelData=data;options($('role-panel-picker'),data.panels.map(p=>({id:p.id,name:p.title})),'New panel');
  if(!data.panels.some(p=>p.id===rolePanelId))rolePanelId=data.panels[0]?.id||'';
  $('role-panel-picker').value=rolePanelId;fillRolePanel(data.panels.find(p=>p.id===rolePanelId));
  $('role-panel-note').textContent=data.canManage?'Publish up to 10 panels. Members choose their roles in Discord.':'You can view panels. Manage Server and Manage Roles are required to edit them.';
 }else if(currentTab==='tools'){
  if(resources?.features?.tools!==true){$('tools-note').textContent='Upload the bot update to enable these tools.';applyCommunityCapabilities();return;}
  const data=await api('guilds/'+id+'/tools');if(id!==selected)return;toolData=data;
  if(Array.isArray(data.pollChannels)){const picked=$('poll-channel').value;options($('poll-channel'),data.pollChannels.filter(channel=>channel.canPoll),'Choose a poll channel');$('poll-channel').value=picked;let note=$('poll-permission-note');if(!note){note=textElement('p','','caption');note.id='poll-permission-note';$('poll-channel').closest('label').after(note);}note.textContent=data.pollChannels.some(channel=>channel.canPoll)?'TAGGY needs Send Polls permission in the channel you choose.':data.pollChannels[0]?.reason||'Give TAGGY View Channel, Send Messages and Send Polls in a text channel to post polls.';}
  if(!dirtyForms.has('replies-form')){replyDraft=data.replies.map(reply=>({name:reply.name,trigger:reply.trigger??reply.name,match:reply.match??'contains',content:reply.content,enabled:reply.enabled??true,cooldownSeconds:reply.cooldownSeconds??15}));renderReplies();}
  if(!dirtyForms.has('nickname-form'))$('bot-nickname').value=data.nickname||'';
  const picked=$('tools-member').value;options($('tools-member'),data.members,'Choose a member');$('tools-member').value=picked;
  const reply=$('send-reply-name').value;options($('send-reply-name'),data.replies.map(r=>({id:r.name,name:r.name})),'Choose reply');$('send-reply-name').value=reply;
  $('tools-server-info').replaceChildren();for(const [label,value]of [['Members',data.server.members],['Roles',data.server.roles],['Channels',data.server.channels]]){
   const p=textElement('p','');p.append(textElement('strong',Number(value||0).toLocaleString()),textElement('span',label));$('tools-server-info').append(p);
  }
  $('tools-note').textContent=data.capabilities.manage?'Make a poll, add a trigger or choose another tool.':'You can view information and send saved replies in channels you can access. Manage Server is required to edit triggers and post polls.';
 }
 applyCommunityCapabilities();
}
function fillRolePanel(panel){
 rolePanelId=panel?.id||'';$('role-panel-title').value=panel?.title||'Pick your roles';$('role-panel-description').value=panel?.description||'Choose what you want to see and talk about.';
 $('role-panel-channel').value=panel?.channelId||'';$('role-panel-style').value=panel?.style||'buttons';$('role-panel-mode').value=panel?.mode||'normal';
 panelDraft=structuredClone(panel?.options||[{roleId:'',label:'Gaming',emoji:'🎮'}]);renderPanelRows();
 $('role-panel-link').hidden=!panel?.messageId;if(panel?.messageId)$('role-panel-link').href='https://discord.com/channels/'+selected+'/'+panel.channelId+'/'+panel.messageId;
 applyCommunityCapabilities();
}
function renderPanelRows(){
 $('role-panel-options').replaceChildren();panelDraft.forEach((choice,index)=>{
  const row=textElement('div','','community-row'),grid=textElement('div','','tool-grid');
  const label=textElement('label','Role'),select=document.createElement('select');select.required=true;options(select,rolePanelData?.roles||[],'Choose role');
  if(choice.roleId&&![...select.options].some(o=>o.value===choice.roleId)){const old=textElement('option','Unavailable role: '+choice.roleId);old.value=choice.roleId;select.append(old);}
  select.value=choice.roleId;select.setAttribute('aria-label','Role for choice '+(index+1));select.addEventListener('change',()=>{choice.roleId=select.value;communityDirty('role-panel-form');renderPanelPreview();});label.append(select);grid.append(label);
  for(const [key,name,max]of [['label','Label',80],['emoji','Emoji',100]]){const wrapper=textElement('label',name),input=document.createElement('input');input.value=choice[key];input.maxLength=max;input.required=key==='label';input.setAttribute('aria-label',name+' for choice '+(index+1));if(key==='emoji')input.placeholder='🎮 or <:name:id>';input.addEventListener('input',()=>{choice[key]=input.value;communityDirty('role-panel-form');renderPanelPreview();});wrapper.append(input);grid.append(wrapper);}
  const remove=textElement('button','Remove choice '+(index+1));remove.type='button';remove.addEventListener('click',()=>{panelDraft.splice(index,1);communityDirty('role-panel-form');renderPanelRows();applyCommunityCapabilities();});row.append(grid,remove);$('role-panel-options').append(row);
 });renderPanelPreview();
}
function renderPanelPreview(){
 const preview=$('role-panel-preview');preview.dataset.style=$('role-panel-style').value;preview.replaceChildren(textElement('h4',$('role-panel-title').value||'Pick your roles'),textElement('p',$('role-panel-description').value));
 if($('role-panel-style').value==='menu')preview.append(textElement('p','Choose your roles ▾','caption'));
 const choices=textElement('div','','role-preview-choices');for(const choice of panelDraft){const option=textElement('span','');const custom=choice.emoji?.match(/^<a?:[A-Za-z0-9_]+:(\d{1,20})>$/);if(custom){const img=document.createElement('img');img.src='https://cdn.discordapp.com/emojis/'+custom[1]+'.png';img.alt='';img.width=20;img.height=20;option.append(img);}else option.append(document.createTextNode((choice.emoji||'')+' '));option.append(document.createTextNode(choice.label||'New role'));choices.append(option);}preview.append(choices);
}
$('role-panel-picker').addEventListener('change',()=>{if(dirtyForms.has('role-panel-form')&&!confirm('Discard changes to this panel?')){$('role-panel-picker').value=rolePanelId;return;}clearDraft('role-panel-form');fillRolePanel(rolePanelData?.panels.find(p=>p.id===$('role-panel-picker').value));});
$('new-role-panel').addEventListener('click',()=>{if(dirtyForms.has('role-panel-form')&&!confirm('Discard changes to this panel?'))return;clearDraft('role-panel-form');$('role-panel-picker').value='';fillRolePanel();communityDirty('role-panel-form');});
$('add-panel-role').addEventListener('click',()=>{if(panelDraft.length>=20){showStatus('Use up to 20 roles per panel.','error');return;}panelDraft.push({roleId:'',label:'',emoji:''});communityDirty('role-panel-form');renderPanelRows();applyCommunityCapabilities();});
$('role-panel-form').addEventListener('input',renderPanelPreview);
$('role-panel-form').addEventListener('submit',async event=>{
 event.preventDefault();const body={channelId:$('role-panel-channel').value,title:$('role-panel-title').value,description:$('role-panel-description').value,style:$('role-panel-style').value,mode:$('role-panel-mode').value,options:panelDraft};if(rolePanelId)body.id=rolePanelId;
 const result=await action('guilds/'+selected+'/role-panels',body,'Role panel published.');if(result){rolePanelId=result.panel.id;clearDraft('role-panel-form');await loadCommunityTab();}
});
$('close-role-panel').addEventListener('click',async()=>{if(!rolePanelId||!confirm('Close this role panel? Members keep roles they already picked.'))return;const result=await action('guilds/'+selected+'/role-panel-close',{id:rolePanelId,confirmed:true},'Role panel closed.');if(result){rolePanelId='';clearDraft('role-panel-form');await loadCommunityTab();}});
function renderReplies(){
 $('reply-rows').replaceChildren();replyDraft.forEach((reply,index)=>{
  const row=textElement('div','','community-row trigger-row'),heading=textElement('div','','section-heading');heading.append(textElement('h4','Trigger '+(index+1)));
  const enabledLabel=textElement('label','Enabled','verification-toggle'),enabled=document.createElement('input');enabled.type='checkbox';enabled.checked=reply.enabled;enabled.setAttribute('aria-label','Enable trigger '+(index+1));enabled.addEventListener('change',()=>{reply.enabled=enabled.checked;communityDirty('replies-form');});enabledLabel.prepend(enabled);heading.append(enabledLabel);row.append(heading);
  const grid=textElement('div','','tool-grid');
  for(const [key,label,max]of [['name','Saved name',32],['trigger','When someone types',120]]){
   const wrapper=textElement('label',label),input=document.createElement('input');input.value=reply[key];input.maxLength=max;input.required=true;input.setAttribute('aria-label',label+' '+(index+1));
   if(key==='name'){input.pattern='[a-z0-9](?:[a-z0-9]|-){0,31}';input.placeholder='rules';}else input.placeholder='where are the rules';
   input.addEventListener('input',()=>{reply[key]=input.value;communityDirty('replies-form');});wrapper.append(input);grid.append(wrapper);
  }
  const matchLabel=textElement('label','Match'),match=document.createElement('select');match.setAttribute('aria-label','Match for trigger '+(index+1));for(const [value,label]of [['contains','Words appear in a message'],['exact','The whole message matches']]){const option=textElement('option',label);option.value=value;match.append(option);}match.value=reply.match;match.addEventListener('change',()=>{reply.match=match.value;communityDirty('replies-form');});matchLabel.append(match);grid.append(matchLabel);
  const cooldownLabel=textElement('label','Wait between replies · seconds'),cooldown=document.createElement('input');cooldown.type='number';cooldown.min=0;cooldown.max=3600;cooldown.required=true;cooldown.value=reply.cooldownSeconds;cooldown.setAttribute('aria-label','Cooldown for trigger '+(index+1));cooldown.addEventListener('input',()=>{reply.cooldownSeconds=Number(cooldown.value);communityDirty('replies-form');});cooldownLabel.append(cooldown);grid.append(cooldownLabel);row.append(grid);
  const contentLabel=textElement('label','TAGGY replies'),content=document.createElement('textarea');content.rows=3;content.maxLength=1800;content.required=true;content.value=reply.content;content.setAttribute('aria-label','Reply '+(index+1));content.addEventListener('input',()=>{reply.content=content.value;communityDirty('replies-form');});contentLabel.append(content);row.append(contentLabel);
  const remove=textElement('button','Remove trigger '+(index+1));remove.type='button';remove.addEventListener('click',()=>{replyDraft.splice(index,1);communityDirty('replies-form');renderReplies();applyCommunityCapabilities();});row.append(remove);$('reply-rows').append(row);
 });
}
$('add-reply').addEventListener('click',()=>{if(replyDraft.length>=30){showStatus('Use up to 30 triggers.','error');return;}replyDraft.push({name:'',trigger:'',match:'contains',content:'',enabled:true,cooldownSeconds:15});communityDirty('replies-form');renderReplies();applyCommunityCapabilities();});
$('replies-form').addEventListener('submit',async event=>{event.preventDefault();const result=await action('guilds/'+selected+'/custom-replies',{replies:replyDraft},'Trigger words saved.');if(result){clearDraft('replies-form');await loadCommunityTab();}});

$('send-reply-form').addEventListener('submit',async event=>{event.preventDefault();const result=await action('guilds/'+selected+'/custom-reply',{name:$('send-reply-name').value,channelId:$('send-reply-channel').value},'Reply sent.');if(result)clearDraft('send-reply-form');});
$('poll-form').addEventListener('submit',async event=>{event.preventDefault();const answers=$('poll-answers').value.split('\n').map(s=>s.trim()).filter(Boolean);if(answers.length<2||answers.length>10||answers.some(s=>s.length>55)){showStatus('Use 2 to 10 answers, up to 55 characters each.','error');return;}const result=await action('guilds/'+selected+'/poll',{channelId:$('poll-channel').value,question:$('poll-question').value,answers,hours:Number($('poll-hours').value),multiple:$('poll-multiple').checked},'Poll posted in Discord.');if(result){$('poll-form').reset();clearDraft('poll-form');}});
$('nickname-form').addEventListener('submit',async event=>{event.preventDefault();const result=await action('guilds/'+selected+'/bot-nickname',{nickname:$('bot-nickname').value},'Server nickname saved.');if(result){clearDraft('nickname-form');await loadCommunityTab();}});
$('member-profile-form').addEventListener('submit',async event=>{event.preventDefault();const id=selected,memberId=$('tools-member').value||$('tools-member-id').value.trim();try{const info=await api('guilds/'+id+'/member-profile?memberId='+encodeURIComponent(memberId));if(id!==selected)return;const details=textElement('div','');details.append(textElement('h4',info.name||info.username),textElement('p',info.username+' · '+info.id),textElement('p','Joined: '+(info.joinedAt?new Date(info.joinedAt).toLocaleDateString():'Unavailable')),textElement('p','Roles: '+(info.roles.join(', ')||'Member')));$('tools-member-info').replaceChildren(avatar(info),details);clearDraft('member-profile-form');}catch(error){showStatus(error.message,'error');}});
$('bot-profile-form').addEventListener('submit',async event=>{event.preventDefault();if(!profileAllowed()){showStatus('Profile controls are only available in the TAGGY owner server.','error');return;}const result=await action('owner/profile',{guildId:selected,username:$('bot-username').value,status:$('bot-status').value,activityType:$('bot-activity').value},'Bot profile saved.');if(result){clearDraft('bot-profile-form');await loadCommunityTab();}});
applyCommunityCapabilities();

initializeDashboardSections();

function applyGiveawayCapabilities(){
 const available=featureReady('giveaways'),can=available&&giveawayFor===selected&&giveawayData?.canManage===true&&!busy;
 disableForm('giveaway-form',!can||giveawayUncertain.has('start'));
 $('giveaway-preset').disabled=!can||giveawayUncertain.has('start');
 for(const control of document.querySelectorAll('[data-giveaway-duration]'))control.disabled=!can||giveawayUncertain.has('start');
 for(const control of document.querySelectorAll('[data-giveaway-action]'))control.disabled=!can||giveawayUncertain.has(control.dataset.giveawayId);
 for(const control of document.querySelectorAll('.refresh-giveaways'))control.disabled=!available||Boolean(giveawayLoading)||busy;
 $('giveaway-uncertain').hidden=!giveawayUncertain.size;$('giveaway-unlock').disabled=!giveawayChecked||busy;
}
function giveawayNotice(message,error=false){
 for(const node of [$('giveaway-note'),...document.querySelectorAll('.giveaway-list-note')]){node.textContent=message;node.className='notice'+(node.classList.contains('giveaway-list-note')?' giveaway-list-note':'')+(error?' error':'');}
}
function giveawayChoices(){
 const channel=$('giveaway-channel'),pickedChannel=channel.value,role=$('giveaway-role'),pickedRole=role.value;
 options(channel,giveawayData?.channels||[],'Choose channel');
 for(const option of [...channel.options].slice(1)){const item=giveawayData.channels.find(item=>item.id===option.value);option.disabled=item.canSend!==true;if(option.disabled)option.textContent=item.name+' · '+(item.reason||'Sending unavailable');}
 channel.value=pickedChannel;
 options(role,giveawayData?.roles||[],'Anyone in the server');role.value=pickedRole;
 if(pickedChannel&&!channel.value){const option=textElement('option','Previous channel unavailable');option.value=pickedChannel;option.disabled=true;channel.append(option);channel.value=pickedChannel;}
 if(pickedRole&&!role.value){const option=textElement('option','Previous role unavailable');option.value=pickedRole;option.disabled=true;role.append(option);role.value=pickedRole;}
}
function giveawayEmoji(value){
 const holder=textElement('span','','giveaway-emoji'),match=/^<(a?):[A-Za-z0-9_]{2,32}:([0-9]{17,20})>$/.exec(value);
 if(match){const image=document.createElement('img');image.src='https://cdn.discordapp.com/emojis/'+match[2]+(match[1]?'.gif':'.png');image.alt='Custom emoji';image.width=20;image.height=20;image.addEventListener('error',()=>{holder.textContent='🎉';});holder.append(image);}else holder.textContent=String(value||'').slice(0,100);
 return holder;
}
function relativeGiveawayTime(timestamp){
 if(!Number.isFinite(timestamp))return 'Choose a time';const minutes=Math.ceil((timestamp-Date.now())/60000);
 if(minutes<=0)return 'Time is up';if(minutes<60)return 'In '+minutes+' '+(minutes===1?'minute':'minutes');const hours=Math.ceil(minutes/60);if(hours<48)return 'In '+hours+' '+(hours===1?'hour':'hours');const days=Math.ceil(hours/24);return 'In '+days+' days';
}
function previewGiveaway(){
 $('giveaway-preview-title').textContent=$('giveaway-title').value||'Your giveaway';$('giveaway-preview-prize').textContent=$('giveaway-prize').value||'Your prize goes here';
 if($('giveaway-description').value)window.TaggyFormatting.render($('giveaway-description').value,$('giveaway-preview-description'),{headings:false});else $('giveaway-preview-description').replaceChildren();
 $('giveaway-preview').style.borderLeftColor=$('giveaway-color').value;
 $('giveaway-preview-winners').textContent=$('giveaway-winners').value;
 const timestamp=new Date($('giveaway-ends').value).getTime();$('giveaway-preview-ends').textContent=relativeGiveawayTime(timestamp);$('giveaway-preview-ends').title=Number.isFinite(timestamp)?new Date(timestamp).toLocaleString():'';
 const role=$('giveaway-role').selectedOptions[0];$('giveaway-preview-role').textContent=$('giveaway-role').value?'Requires @'+(role?.textContent||'selected role'):'Anyone in the server can enter.';
 $('giveaway-preview-button').replaceChildren(giveawayEmoji($('giveaway-emoji').value.trim()),document.createTextNode($('giveaway-button').value||'Enter giveaway'));
}
function resetGiveaway(){
 $('giveaway-form').reset();$('giveaway-ends').value=localDateInput(Date.now()+86400000);previewGiveaway();
}
const giveawayStatusLabel=status=>({creating:'Posting in Discord',active:'Open for entries',ending:'Picking winners',ended:'Finished',cancelled:'Cancelled',needs_review:'Check Discord',failed:'Could not finish'}[status]||'Check status');
function renderGiveaways(){
 const items=Array.isArray(giveawayData?.giveaways)?giveawayData.giveaways:[];$('giveaway-active').replaceChildren();$('giveaway-results').replaceChildren();
 const activeStates=new Set(['creating','active','ending','needs_review']);
 for(const item of [...items].sort((a,b)=>(b.createdAt||0)-(a.createdAt||0))){
  const row=textElement('article','','giveaway-row');row.dataset.giveaway=item.id;const heading=textElement('div','','section-heading');heading.append(textElement('h4',item.title||item.prize||'Giveaway'),textElement('span',giveawayStatusLabel(item.status),'giveaway-state '+(activeStates.has(item.status)?'live':'done')));
  const channel=giveawayData.channels?.find(channel=>channel.id===item.channelId)?.name||'Unavailable channel';row.append(heading,textElement('p',item.prize||'Prize','giveaway-prize'),textElement('p','#'+channel+' · '+Number(item.entryCount||0).toLocaleString()+' entries · '+Number(item.winnerCount||1)+' '+(Number(item.winnerCount)===1?'winner':'winners'),'caption'));
  const end=new Date(item.endsAt);row.append(textElement('p',(item.status==='active'?relativeGiveawayTime(end.getTime())+' · Ends ':'End time: ')+(Number.isFinite(end.getTime())?end.toLocaleString():'Unavailable'),'caption'));
  if(item.lastError)row.append(textElement('p',item.lastError,'notice error'));
  if(['creating','ending'].includes(item.status))row.append(textElement('p','TAGGY is working on this. Refresh to see the result.','caption'));
  if(item.status==='needs_review')row.append(textElement('p','Check the original Discord message before taking another action.','caption'));
  const winners=Array.isArray(item.winners)?item.winners:[];
  if(item.status==='ended'){const list=textElement('ul','','giveaway-winners');for(const winner of winners)list.append(textElement('li',String(winner.name||'Discord member')+(/^[0-9]{1,20}$/.test(String(winner.id))?' · '+winner.id:'')));row.append(textElement('p',winners.length?'Winners':'No eligible entries remained.','caption'));if(winners.length)row.append(list);}
  const actions=textElement('div','','actions');
  const link=scheduleMessageLink(item);if(link)actions.append(link);
  if(item.status==='active')for(const [action,label]of [['end','End now'],['cancel','Cancel']])actions.append(giveawayActionButton(item,action,label));
  if(item.status==='needs_review'){if(item.messageId)actions.append(giveawayActionButton(item,'end','Retry saved result'));actions.append(giveawayActionButton(item,'cancel','Cancel'));}
  if(item.status==='ended')actions.append(giveawayActionButton(item,'reroll','Reroll winners'));
  if(['ended','cancelled'].includes(item.status))actions.append(giveawayActionButton(item,'forget','Clear saved record'));
  if(actions.children.length)row.append(actions);(activeStates.has(item.status)?$('giveaway-active'):$('giveaway-results')).append(row);
 }
 if(!$('giveaway-active').children.length)$('giveaway-active').append(textElement('p','Nothing up for grabs yet. Create a giveaway to get everyone involved.','muted'));
 if(!$('giveaway-results').children.length)$('giveaway-results').append(textElement('p','Winners will appear here when a giveaway ends.','muted'));
 applyGiveawayCapabilities();
}
function giveawayActionButton(item,action,label){
 const button=textElement('button',label);button.type='button';button.dataset.giveawayAction=action;button.dataset.giveawayId=item.id;button.setAttribute('aria-label',label+' for '+(item.title||item.prize||'giveaway'));
 button.addEventListener('click',()=>{if(busy||giveawayData?.canManage!==true||giveawayUncertain.has(item.id))return;const retry=action==='end'&&item.status==='needs_review',question=retry?'Retry updating the original Discord message? TAGGY keeps the saved result and does not draw new winners.':{end:'End this giveaway now and pick winners?',cancel:'Cancel this giveaway? Entries close and no new winners will be picked.',reroll:'Reroll the winners? TAGGY rechecks eligible entries and excludes everyone who has already won this giveaway.',forget:'Clear this saved giveaway, its entries and result? The closed Discord post stays. You cannot reroll or restore the saved record afterward.'}[action];if(!confirm(question))return;void mutateGiveaway({action,id:item.id,confirmed:true},item.id,retry?'Giveaway result updated.':{end:'Winners picked.',cancel:'Giveaway cancelled.',reroll:'New winners picked.',forget:'Saved giveaway cleared.'}[action]);});return button;
}
async function loadGiveaways(){
 const id=selected;if(!id)return;if(resourcesFor!==id)await loadResources();if(id!==selected)return;
 if(!featureReady('giveaways')){fishingData=null;fishingFor='';fishingPlayer=null;fishingPlayerFor='';$('fishing-player-form').hidden=true;$('fishing-player-profile').replaceChildren();giveawayData=null;giveawayFor='';$('giveaway-active').replaceChildren();$('giveaway-results').replaceChildren();giveawayNotice('Upload the bot update to enable giveaways.');applyGiveawayCapabilities();return;}
 if(giveawayLoading===id)return;giveawayLoading=id;applyGiveawayCapabilities();
 try{const data=await api('guilds/'+id+'/giveaways');if(id!==selected)return;giveawayData=data;giveawayFor=id;giveawayChoices();renderGiveaways();previewGiveaway();giveawayChecked=true;
  giveawayNotice(data.canManage?'Choose a prize and a channel. TAGGY handles entries and the draw.':'You can view giveaways. Manage Server and channel access are required to change them.');
 }catch(error){if(id===selected){giveawayChecked=false;giveawayNotice('Could not refresh giveaways. '+error.message,true);}throw error;}
 finally{if(giveawayLoading===id)giveawayLoading='';applyGiveawayCapabilities();}
}
async function mutateGiveaway(body,key,message){
 if(busy||!featureReady('giveaways')||giveawayData?.canManage!==true||giveawayFor!==selected||giveawayUncertain.has(key))return;
 const id=selected,controls=[...document.querySelectorAll('#dashboard button,#dashboard input,#dashboard select,#dashboard textarea,#logout')],disabled=controls.map(control=>control.disabled);busy=true;controls.forEach(control=>{control.disabled=true;});
 try{
  const result=await api('guilds/'+id+'/giveaways',body);if(selected!==id)return;
  if(Array.isArray(result.giveaways))giveawayData.giveaways=result.giveaways;else if(result.giveaway)giveawayData.giveaways=(giveawayData.giveaways||[]).filter(item=>item.id!==result.giveaway.id).concat(result.giveaway);
  if(body.action==='start'){clearDraft('giveaway-form');resetGiveaway();}
  renderGiveaways();showStatus(message,'success');
  if(body.action==='start'){currentSection='active';applyTabState();history.pushState({},'',dashboardURL().href);}
  try{await loadGiveaways();}catch(error){showStatus('Action completed. Refresh failed: '+error.message,'error');}
 }catch(error){
  if(!Number.isInteger(error.status)||error.status>=500){giveawayUncertain.add(key);giveawayChecked=false;showStatus('Connection lost. Check Discord and refresh the list before trying this action again.','error');}
  else showStatus(error.message,'error');
 }finally{busy=false;controls.forEach((control,index)=>{control.disabled=disabled[index];});applyCapabilities();}
}
$('giveaway-form').addEventListener('input',previewGiveaway);$('giveaway-form').addEventListener('change',previewGiveaway);
$('giveaway-form').addEventListener('submit',event=>{
 event.preventDefault();if(busy||giveawayData?.canManage!==true||giveawayUncertain.has('start'))return;
 const endsAt=new Date($('giveaway-ends').value).getTime();
 if(!Number.isFinite(endsAt)||endsAt<Date.now()+60000||endsAt>Date.now()+30*86400000){showStatus('Choose a time at least one minute from now and within the next 30 days.','error');$('giveaway-ends').focus();return;}
 if(!giveawayData.channels?.some(channel=>channel.id===$('giveaway-channel').value&&channel.canSend===true)){showStatus('Choose a channel where you and TAGGY can post.','error');$('giveaway-channel').focus();return;}
 if($('giveaway-role').value&&!giveawayData.roles?.some(role=>role.id===$('giveaway-role').value)){showStatus('Choose an available role or let everyone enter.','error');$('giveaway-role').focus();return;}
 const giveaway={prize:$('giveaway-prize').value.trim(),title:$('giveaway-title').value.trim(),description:$('giveaway-description').value,channelId:$('giveaway-channel').value,winnerCount:Number($('giveaway-winners').value),endsAt,requiredRoleId:$('giveaway-role').value,buttonLabel:$('giveaway-button').value.trim(),emoji:$('giveaway-emoji').value.trim(),color:$('giveaway-color').value};
 if(!giveaway.prize||!giveaway.title||!giveaway.buttonLabel){showStatus('Add a prize, title and button text before creating your giveaway.','error');return;}
 void mutateGiveaway({action:'start',giveaway},'start','Giveaway posted in Discord.');
});
$('giveaway-preset').addEventListener('click',()=>{if(dirtyForms.has('giveaway-form')&&!confirm('Replace this unsaved giveaway with the example?'))return;$('giveaway-prize').value='A surprise from the staff';$('giveaway-title').value='A little something for the server 🎉';$('giveaway-description').value='Thanks for being here!\nPress the button below to enter. Good luck 🍀';$('giveaway-winners').value='1';$('giveaway-role').value='';$('giveaway-button').value='Count me in!';$('giveaway-emoji').value='🎉';$('giveaway-color').value='#a329c8';$('giveaway-ends').value=localDateInput(Date.now()+86400000);communityDirty('giveaway-form');previewGiveaway();showStatus('Example added to your draft. Choose your prize and channel before creating it.','success');});
for(const button of document.querySelectorAll('[data-giveaway-duration]'))button.addEventListener('click',()=>{$('giveaway-ends').value=localDateInput(Date.now()+Number(button.dataset.giveawayDuration)*60000);communityDirty('giveaway-form');previewGiveaway();});
for(const button of document.querySelectorAll('.refresh-giveaways'))button.addEventListener('click',()=>{if(!busy)void loadGiveaways().catch(error=>showStatus(error.message,'error'));});
$('giveaway-unlock').addEventListener('click',()=>{if(!giveawayChecked||busy||!confirm('Have you checked the refreshed list and original message in Discord? A second creation or reroll cannot undo the first one.'))return;giveawayUncertain.clear();applyGiveawayCapabilities();showStatus('Actions unlocked. Check the result before deciding what to do next.','success');});
$('giveaway-timezone').textContent='Your time zone: '+(Intl.DateTimeFormat().resolvedOptions().timeZone||'local time')+'. TAGGY keeps this time while the page is closed.';resetGiveaway();applyGiveawayCapabilities();

let searchReturnFocus=null;
const searchFeatures={'home/setup':'setup','embeds/scheduled':'schedules','embeds/history':'schedules','channels/dms':'welcomeDM','tools/commands':'commands','roles/panels':'rolePanels'};
function dashboardSearchItems(){
 const result=[];
 for(const [tab,[name,description]]of Object.entries(workspacePages)){
  if(!allowedTool(tab)||tab==='profile'&&!profileSupported||tab==='giveaways'&&!featureReady('giveaways'))continue;
  const sections=workspaceSections[tab]?availableSections(tab):[['',name]];
  for(const [section,label]of sections){const feature=searchFeatures[tab+'/'+section];if(feature&&!featureReady(feature))continue;result.push({tab,section,name,label,description});}
 }
 return result;
}
function renderToolSearch(){
 const query=$('tool-search-input').value.trim().toLocaleLowerCase(),items=dashboardSearchItems().filter(item=>[item.name,item.label,item.description].join(' ').toLocaleLowerCase().includes(query)),list=$('tool-search-results');list.replaceChildren();
 for(const item of items){const link=textElement('a','');link.href=dashboardURL(item.tab,item.section).href;link.dataset.searchTool=item.tab;link.dataset.searchSection=item.section;const content=textElement('span','');content.append(textElement('strong',item.label),textElement('small',item.section?item.name:item.description));link.append(content,textElement('span','↗','search-arrow'));link.addEventListener('click',event=>{if(event.button||event.metaKey||event.ctrlKey||event.shiftKey||event.altKey)return;event.preventDefault();if(busy){$('tool-search-count').textContent='Wait for the current action to finish.';return;}$('tool-search-dialog').close();chooseTool(item.tab,item.section);$('workspace-title').setAttribute('tabindex','-1');$('workspace-title').focus();});list.append(link);}
 $('tool-search-count').textContent=items.length?items.length+' '+(items.length===1?'tool':'tools')+(query?' match your search.':' available for this server.'):'No tools match. Try roles, tickets or messages.';
}
function openToolSearch(){if(!active||!selected)return;searchReturnFocus=document.activeElement;renderToolSearch();if(!$('tool-search-dialog').open)$('tool-search-dialog').showModal();$('tool-search-input').focus();$('tool-search-input').select();}
for(const button of document.querySelectorAll('.tool-search-open'))button.addEventListener('click',openToolSearch);
$('tool-search-input').addEventListener('input',renderToolSearch);$('tool-search-close').addEventListener('click',()=>$('tool-search-dialog').close());
$('tool-search-dialog').addEventListener('close',()=>{searchReturnFocus?.focus?.({preventScroll:true});});
$('tool-search-dialog').addEventListener('keydown',event=>{
 if(event.key==='Escape'){event.preventDefault();$('tool-search-dialog').close();return;}
 if(!['ArrowDown','ArrowUp'].includes(event.key))return;const links=[...$('tool-search-results').querySelectorAll('a')];if(!links.length)return;event.preventDefault();const index=links.indexOf(document.activeElement);links[index<0?(event.key==='ArrowDown'?0:links.length-1):(index+(event.key==='ArrowDown'?1:-1)+links.length)%links.length].focus();
});
window.addEventListener('keydown',event=>{
 if(event.defaultPrevented||event.repeat||$('tool-search-dialog').open||!active)return;
 const target=event.target;if(target?.closest?.('input,textarea,select,[contenteditable="true"],[role="textbox"]'))return;
 if((event.key==='/'&&!event.ctrlKey&&!event.metaKey&&!event.altKey)||(event.key.toLowerCase()==='k'&&(event.ctrlKey||event.metaKey)&&!event.altKey)){event.preventDefault();openToolSearch();}
});
