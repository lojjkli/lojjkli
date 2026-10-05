# TAGGY 2.0 dashboards and security

The update adds `https://lojjkli.site/taggy/` to the existing website. Regular users sign in with Discord and can manage only servers they own or have **Manage Server** permission in. The configured friend also gets access to the configured friend guild while still a member; channel and role operations continue to check actual Discord permissions. Every server read and write rechecks membership and permissions on the bot backend. Changes to command role bindings require the actual server owner or Discord Administrator; role assignment, channel changes and timeout releases also enforce the actor's Discord permissions. This prevents a server manager from granting themselves stronger roles through TAGGY.

The special owner console and private DM inbox are available only to the exact `OWNER_ID` account (`799725823044354048`). `ROBLOX_FRIEND_OWNER_ID` is set locally to the supplied friend ID (`1519053064445755451`); that identity never gets global access or private DMs. Confirm both values on the bot host when updating. It can select every server TAGGY is connected to, including the friend's server. Your main `ROBLOX_GUILD_ID` is listed first, with an Open my main server shortcut and a cross-server protection overview. This does not grant global-owner Discord command access in the friend's server: the existing member access plus `.partnerupdate` exception remains. Explicitly assigning that account a configured Owner role would grant owner commands in that guild.

Before login, the landing page follows the supplied TAGS/TAGGY videos: near-black backgrounds, purple light, white/lavender headlines, outline icons, soft purple cards and subtle reveals. It uses the supplied original TAGGY and TAGS PNG artwork in `site/public/taggy/assets/`. Mobile puts the logo and headline above stacked controls. Reduced-motion preferences disable decorative animation. After login the large hero/footer disappear, leaving a compact dashboard with an icon-only server rail, sidebar tabs and account name. Server names appear as tooltips and in the active-server heading; servers without icons use initials.

## Navigation and formatting

Dashboard links can select a server, tab and subpage, for example `https://lojjkli.site/taggy/?server=SERVER_ID&tab=roles&section=panels`. Roles groups permission bindings, member assignment and community role panels. Other tools also use subpages so one task stays visible at a time. Copy the current dashboard link to direct someone to the relevant controls; the recipient still needs their own Discord dashboard permissions.

Outgoing text editors include Discord formatting buttons and a safe preview. Select text and choose Bold to insert `**text**`, or use italics, underline, strikethrough, spoilers, code, quotes and heading buttons. Headings are supported in regular Discord messages; embed descriptions keep Discord's embed formatting behavior. Ticket questions use separate multiline editors so formatting and line breaks stay in one question.

## Trigger replies and polls

Tools contains trigger-word replies instead of `.tag` commands. Replies are configured per server, with a trigger phrase, whole-phrase or exact-message matching, an enable switch and a cooldown. Matching ignores case. Saved legacy reply names become their trigger words. Bots, webhooks, DMs and prefix commands do not activate replies. Responses suppress mention notifications and have minimum channel/user gaps to avoid reply floods.

Native Discord polls require TAGGY to have View Channel, Send Messages and Send Polls. The acting server manager needs Manage Server plus access and Send Messages in the channel; their own Send Polls permission is not required because TAGGY posts the poll. The dashboard shows channel eligibility, and API rejections explain which permissions or inputs to fix.

## Logs and messaging

- **Logs tab:** latest 300 Discord audit changes, dashboard actions and security events for the selected server, with search and 15-second refresh. Ordinary audit events are recorded without sending owner alerts; security protections still alert you. Requires TAGGY to have View Audit Log for incoming Discord changes. New events are captured after the updated bot starts; existing stored incidents remain visible.
- **Messages tab:** read the latest 50 messages in a supported text/announcement channel and send plain text as TAGGY. Regular users must be allowed to view/read/send in that channel; the special owner may use any connected guild where the bot has the necessary permissions. Inaccessible channels are filtered from regular users' selectors, and checks repeat on every backend request. Mentions do not notify users. Disabled buttons reflect account permissions.
- **DMs tab:** only `OWNER_ID` can list incoming conversations, read history, start a conversation by Discord user ID and reply as TAGGY. DMs are bot DMs, not access to your personal Discord account's inbox. Discord may block delivery when a recipient disables DMs or shares no server with TAGGY.
- Incoming/outgoing DM history lives in the private `private-inbox.json`, capped at 100 conversations, 150 messages each and 30 days. Keep this file private and backed up. Attachment links can be opened; this version sends plain text from the dashboard. Do not include private inbox data in GitHub or upload packages.
- Previous automatic DM forwarding and server-channel DM replies have been removed. `.setdm` now explains that forwarding is disabled; `.dm` is global-owner-only. Existing historical forwarded messages already posted in Discord are not deleted by this update. The legacy `.send` command is also restricted to the actor's current server/channel access unless the actor is the global owner.

## New customization controls

- Member and Unverified verification roles, plus Owner, Admin, Moderator, Helper and Builder command roles per server.
- Member lookup by Discord ID and role addition/removal within Discord's hierarchy.
- Embed studio: compose and publish messages, load TAGGY's existing messages, edit title/description/color/links/images/thumbnail/footer/fields and message content. Editing replaces the existing embeds with one new embed. Preview renders text safely; Discord renders markdown/images when posted. Messages suppress mention notifications.
- Welcome messages using `{user}` and `{server}`, safe auto-roles and a configurable bot audit log channel.
- Channel slowmode and @everyone Send Messages locks, with persistent recovery snapshots for restoration. Explicitly allowed roles or administrators may still send in a locked channel.
- Purple desktop/mobile styling, regular dashboard access and the exclusive global owner console.

Role bindings change which roles TAGGY uses going forward. They do not bulk migrate existing members or update existing channel permission overwrites. Review those in Discord when changing your Member/Unverified roles. In verification servers, the verified Member role cannot be auto-granted on joining. Auto-roles cannot grant configured staff command tiers or dangerous Discord permissions; safety is rechecked for every join.

New ticket setup, panel publishing and ticket opening use the Member role selected under Roles > Server roles. Select it first; missing, deleted, elevated or inaccessible roles stop setup and give a direct dashboard link. New ticket openers must have that role, unless they are ticket staff or the actual server owner. Existing tickets keep their close, reopen and DM relay controls even if a binding is later cleared.

Verification setup also requires a selected Unverified role. Server setup reuses the selected Member, Unverified, Owner and staff roles, preserves all bound roles and does not create replacement defaults. Existing verification installations can still resolve their legacy roles until a dashboard binding is selected; a selected binding never silently falls back to a different role. These controls do not rename roles or bulk move existing users.

Management settings persist in `management-state.json`. Keep this file and `security-state.json` private and backed up. The website controls above are implemented; other existing bot features still use their Discord commands.

## Minecraft removal and branding

The active bot no longer imports the Minecraft storage, FTP, role sync, whitelist or team-channel modules. Polling, Minecraft status, account linking, whitelist interactions and associated legacy commands/help entries have been removed. Legacy source modules were preserved locally outside the bot in the chat's `work/legacy-minecraft` folder. Existing community data was retained.

The bot defaults to **Watching lojjkli.site/taggy**, online, and preserves its existing avatar. Global name/status controls require the exact `OWNER_ID` and server `1553040593494609920` to be selected; this server must also be connected to TAGGY. Backend requests enforce the same restriction. Other servers can change TAGGY's server nickname with the appropriate Discord permissions. Startup does not change the bot profile picture, banner or description. Package startup is corrected to `node index.js`; the unused FTP dependency is removed.

## Automatic security

- Automatic join-raid containment: 8 non-staff joins in 10 seconds activates a 10-minute join shield. Recent arrivals and new non-staff human members are timed out for 10 minutes. Bots are not timed out by this feature.
- Spam containment: 7 messages in 5 seconds, 5 identical text messages in 15 seconds, or 6 distinct user/role mentions in one message triggers message deletion and a 10-minute timeout. Everyone/here mentions also trigger this rule. Staff with Administrator or Manage Messages are exempt.
- Destructive activity containment: 3 channel deletions, role deletions or bans by the same audit-log actor in 10 seconds removes that actor's manageable dangerous roles. Managed roles and roles above TAGGY cannot be removed. Deletions that already occurred cannot be undone by this feature. Administrators are checked; the global owner, actual server owner, and TAGGY are trusted.
- Owner DM alerts, throttled to one alert per incident type per server per minute. If DMs fail, incidents remain in the dashboard.
- Per-server switches and thresholds, manual join shield controls, member timeout release, bot permission checks and the latest 300 incidents per server.
- Settings, shield expiry and incidents persist in `security-state.json`. Keep this file private and back it up. The dashboard reports write failures. There are no security-management Discord commands.

All three protections are enabled by default when the updated bot starts. Tune thresholds for servers with legitimate join surges or routine staff bulk changes. These rules are a first security version, not protection against every kind of raid: there is no new-bot allowlist, invite/link filter, webhook spam filter, deleted-channel restoration or cross-server ban system in this version.

## Configure Discord login

1. In the Discord Developer Portal, open TAGGY's application.
2. In OAuth2, add the exact redirect URL `https://lojjkli.site/taggy/auth/callback`.
3. Copy the application/client ID and OAuth2 client secret into the **bot host's private environment**:

   ```dotenv
   TAGGY_DISCORD_CLIENT_ID=1534927924732629254
   TAGGY_DISCORD_CLIENT_SECRET=YOUR_DISCORD_OAUTH_CLIENT_SECRET
   TAGGY_PROXY_SECRET=YOUR_RANDOM_SHARED_SECRET_AT_LEAST_32_CHARACTERS
   ```

   This is the OAuth2 client secret, **not** the bot token. Keep the existing `OWNER_ID` set to your Discord user ID. This account alone gets the special owner console; other authorized server managers get their server-scoped dashboard.

4. The local TAGGY `.env` already contains a newly generated 256-bit `TAGGY_PROXY_SECRET` and TAGGY's application ID verified through Discord's bot application endpoint. Copy those two values privately into the hosted bot environment, and use the same `TAGGY_PROXY_SECRET` in the Cloudflare website Worker. The OAuth client secret still needs to be obtained from the Developer Portal and configured on the host. Do not paste secrets into chat or commit them to GitHub. The download package deliberately excludes `.env` and all secrets.

Login uses Discord's authorization-code flow and `identify` scope, a browser-bound one-use state, an opaque Secure/HttpOnly/SameSite cookie and CSRF protection on all writes. Sessions expire after 30 minutes idle or 8 hours absolute. Bot restarts require signing in again; signing out revokes that account's sessions on every device, without signing other accounts out. The bot retains no Discord access or refresh token after identifying the user.

## Update the bot on bot-hosting.net

1. Upload all files from the current update package's `bot/` folder into `/home/container/`, replacing the source files. The package contains 19 production JavaScript modules, required assets, `package.json` and `package-lock.json`. Keep the host's existing `.env` and saved JSON files. The package needs no new bot dependency.
2. Ensure the bot uses Node.js 20 or newer and starts `index.js` using the host's startup settings. The updated package starts `index.js`; ensure the hosting panel does too.
3. The dashboard shares TAGGY's existing HTTP listener. The host must supply a valid `SERVER_PORT` matching its allocated port. If the host does not supply it, set the assigned port in the private environment. Do not choose an arbitrary port.
4. TAGGY's canonical HTTPS address is `https://1u061e9dv7.apps.bot-hosting.cloud`. Its existing `/health` endpoint returned HTTP 200 with `{"ok":true}` during preparation. This is already set as `TAGGY_BACKEND_URL` in `site/wrangler.toml`. No custom domain is required. This check confirms the existing listener, not the new dashboard; verify login after the updated bot is running. `https://bot-hosting.net` is the provider's website, not the bot API.
5. Give TAGGY View Audit Log, Manage Roles, Manage Channels, Moderate Members, Manage Messages, Send Messages, Embed Links and access to the channels it must protect. Place its role above members/roles it should manage. Preserve your test server by explicitly setting `ROBLOX_TEST_GUILD_ID`; the old Minecraft environment setting is no longer used. The local environment has already been migrated. Enable the Server Members and Message Content gateway intents in the Developer Portal as required by the existing bot. The new code also subscribes to Guild Moderation events for audit-log detection.
6. Restart the bot. Verify its `/health` URL returns `{"ok":true}`. If the HTTP listener is disabled because of an invalid port, website login cannot work.

## Configure and deploy the website

Apply the website update's files to `lojjkli/lojjkli`. It modifies only the website Worker; the relay, map-sync and lookup Workers remain independent.

The backend address is already set in `site/wrangler.toml`. In Cloudflare, open the `lojjkli-site` Worker's Settings → Variables and Secrets:

- `TAGGY_PROXY_SECRET`: the same private shared secret as the bot host; add it as an encrypted secret.

Alternatively, from `site/`, run `npx wrangler secret put TAGGY_PROXY_SECRET`, entering its value privately at the prompt. Change `TAGGY_BACKEND_URL` in `site/wrangler.toml` if the bot's canonical address changes; it must be an HTTPS base URL without a path, query or fragment.

The website Worker adds the connection secret on the server side. The browser never receives it. API responses are not cached, and forwarded credentials/headers are explicitly limited. Use the canonical `lojjkli.site` hostname for login; the `www` alias does not host private API sessions.

The existing GitHub Actions workflow deploys the website when changes reach `main`. Configure the secrets before merging/pushing there. Then open `https://lojjkli.site/taggy/` and sign in with your owner account. The existing `/admin` page and its key-based API are separate; their key grants no TAGGY dashboard authority.

## Verification

Local checks:

```text
Bot folder: node --check index.js
Bot folder: node --test owner-access.test.js security.test.js security-dashboard.test.js dashboard-management.test.js dashboard-messaging.test.js dashboard-roles.test.js taggy-2.test.js
Website site/ folder: node --check public/taggy/dashboard.js
Website site/ folder: node --test src/worker.test.mjs
Website site/ folder: npx wrangler deploy --dry-run
```

52 bot/login/access/management/messaging/branding tests and 7 website proxy tests pass. A browser fixture verified server icons, compact post-login layout, Logs/search, channel read/send, owner-only DMs/replies, account-disabled controls, regular and special owner views, server selection, role settings, member role assignment, embed publishing/loading, welcome settings, channel locking, shield activation, 320px mobile layout, safe text rendering and the unauthenticated login view. Screenshots are previews with synthetic server data, not a live connection. An earlier baseline run found 11 failures in the pre-existing ticket/Roblox verification tests; that full legacy suite was not rerun for this update. Focused tests verify custom verification-role behavior.

Before treating the system as live, verify login with the real owner and server-scoped access with another Discord account and rejection when it requests another server or the owner API, all connected servers appearing for the owner, a per-server setting saved across a bot restart, delivery of an owner DM and a controlled spam/join test in a dedicated test server. Confirm actual Discord permissions/role hierarchy there. Do not simulate destructive raids in a real community server.

## Recovery

Pause the relevant protection in the dashboard before planned bulk staff operations. End a join shield to stop new-arrival timeouts; existing timeouts expire independently or can be released by member ID. Dangerous roles removed during destructive activity are listed in the incident outcome and require manual review/restoration in Discord. Guild/server owners and roles above TAGGY cannot be contained by the bot.

Back up `security-state.json` before editing it. An unreadable/corrupt state file intentionally fails startup instead of silently overwriting security policy. During bot downtime the dashboard is unavailable and automatic protection does not run. There is no permission or downtime bypass.

## References

- [Discord OAuth2 flow and state binding](https://docs.discord.com/developers/topics/oauth2)
- [Cloudflare Worker-first asset routing](https://developers.cloudflare.com/workers/static-assets/routing/worker-script/)
- [Cloudflare multiple Set-Cookie handling](https://developers.cloudflare.com/workers/runtime-apis/headers/)

## Deployment state

The website is published through its existing GitHub deployment workflow. Updated bot code is tested and provided in the current upload package; it still needs uploading and restarting on the bot host. The browser/computer plugin could not initialize because its runtime kernel files are missing. Existing host secrets and Cloudflare configuration remain in place. Browser screenshots and interaction checks use example server data.

## Older DM history and profiles

The owner DM page now uses searchable avatar conversations, a chat pane and a profile panel. Opening a conversation fetches up to 100 messages from Discord; Load older messages pages backward independently of the bounded local fallback. Known cached DM channels also appear in the inbox. Missing recipients can be opened by user ID. A complete automatic list of every past recipient is not guaranteed; deleted/inaccessible messages cannot be recovered. Network failures are explicitly marked as saved-history fallback. Upload both updated dashboard-messaging.js and security-dashboard.js plus the three dashboard website files.

## Centered introduction, DM tickets and attachments

New tickets continue in DMs and create a private staff channel. Staff replies/files relay to the member; // notes remain internal. Members can type .close. One DM ticket per person can be open across servers; unrelated DMs are never forwarded. Existing legacy tickets remain in their channels until closed. Upload tickets.js, index.js, message-media.js, dashboard-messaging.js and security-dashboard.js, restart, then run .ticketsetup with your support role to update its panel.

Dashboard Messages and owner DMs now accept up to 10 attachments / 8 MB total, including attachment-only messages. Upload the website Worker and _headers as well as the three dashboard files. Regular users must have Attach Files permission. Discord image/GIF/video/audio attachments render inline. Ticket relay copies supported files and falls back to Discord links when copying fails or exceeds the size limit. The introduction follows the video frames with centered branding and content.
