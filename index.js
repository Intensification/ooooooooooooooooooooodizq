require('dotenv').config();
const { Client, WebSocketShard } = require('discord.js-selfbot-v13');

const activeClients = [];

// ── DEVICE PROFILES (Web, Mobile, VR, etc.) ──────────────────────
const PROFILES = [
  { os: 'iOS', browser: 'Discord iOS', device: 'iPhone', release_channel: 'stable', client_build_number: 364899 },
  { os: 'Android', browser: 'Discord Android', device: 'Phone', release_channel: 'stable', client_build_number: 364899 },
  { os: 'Windows VR', browser: 'Discord VR', device: 'Quest', release_channel: 'stable', client_build_number: 364899 },
  { os: 'Windows', browser: 'Chrome', device: '', release_channel: 'stable', client_build_number: 364899 },
  { os: 'Linux', browser: 'Discord Console', device: 'Custom Device', release_channel: 'stable', client_build_number: 364899 }
];

// Available statuses (No offline)
const STATUSES = ['online', 'idle', 'dnd'];

const pick = (arr) => arr[Math.floor(Math.random() * arr.length)];

// ── PROPERTIES ENGINE ─────────────────────────────────────────────
function generateRandomProperties() {
  const baseProfile = pick(PROFILES);
  return {
    browser_user_agent: '', browser_version: '', os_version: '',
    referrer: '', referring_domain: '', referrer_current: '', referring_domain_current: '',
    client_event_source: null, design_id: 0, accessibility_support_enabled: false,
    ...baseProfile
  };
}

// ── GATEWAY INJECTION INTERCEPT ───────────────────────────────────
const _identify = WebSocketShard.prototype.identify;
WebSocketShard.prototype.identify = function () {
  const _send = this.send.bind(this);
  
  if (!this._customProps) {
    this._customProps = generateRandomProperties();
  }

  this.send = function (data) {
    if (data && data.op === 2) {
      data.d.properties = { ...this._customProps };
      data.d.capabilities = 16381;
      data.d.client_state = {
        guild_versions: {}, highest_last_message_id: '0', read_state_version: 0,
        user_guild_settings_version: -1, user_settings_version: -1,
        private_channels_version: '0', api_code_version: 0,
      };
    }
    return _send(data);
  };
  return _identify.call(this);
};

// ── INITIALIZATION LOOPER ─────────────────────────────────────────
const rawTokens = process.env.DISCORD_TOKENS;
if (!rawTokens) {
  console.error("[-] No tokens found in DISCORD_TOKENS environment variable.");
  process.exit(1);
}

const tokens = rawTokens.split(',').map(t => t.trim()).filter(t => t.length > 0);
console.log(`[+] Found ${tokens.length} tokens. Loading execution queue...`);
console.log(`[!] PRESS 'c' AT ANY TIME TO FORCE ALL TOKENS OFFLINE AND EXIT.\n`);

tokens.forEach((token, index) => {
  const client = new Client({ checkUpdate: false });
  activeClients.push(client);

  client.on('ready', async () => {
    const shardProps = client.ws.shards.first()?._customProps || {};
    const currentOS = shardProps.os || 'Unknown';
    const currentBrowser = shardProps.browser || 'Unknown';
    
    // Pick a completely random status for this token
    const randomStatus = pick(STATUSES);

    try {
      // Set status only, with no activities/RPC payloads attached
      await client.user.setPresence({ status: randomStatus, activities: [] });
      console.log(`[+] Account [${index + 1}/${tokens.length}] Online: ${client.user.tag}`);
      console.log(`   └─ Device: ${currentOS} (${currentBrowser}) | Status: ${randomStatus.toUpperCase()}`);
    } catch (err) {
      console.error(`   └─ Error setting presence: ${err.message}`);
    }
  });

  client.on('error', (err) => console.error(`[-] Error [Account ${index + 1}]:`, err.message));
  client.login(token).catch(err => console.error(`[-] Login Failed [Account ${index + 1}]:`, err.message));
});

// ── TERMINAL INTERACTION ENGINE (KEYPRESS CAPTURE) ────────────────
process.stdin.setRawMode(true);
process.stdin.resume();
process.stdin.setEncoding('utf8');

process.stdin.on('data', (key) => {
  if (key === 'c' || key === 'C') {
    console.log('\n[!] "c" detected. Forcing all tokens offline...');
    
    activeClients.forEach((client, index) => {
      try {
        if (client.readyAt) {
          client.destroy();
          console.log(`    [-] Disconnected: ${client.user?.tag || `Account ${index + 1}`}`);
        }
      } catch (e) {}
    });

    console.log('[+] Shutdown complete. Exiting process.');
    process.exit(0);
  }

  if (key === '\u0003') { 
    console.log('\n[!] Ctrl+C detected. Exiting.');
    process.exit(0);
  }
});

process.on('unhandledRejection', () => {});
