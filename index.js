require('dotenv').config();
const { Client, WebSocketShard } = require('discord.js-selfbot-v13');

// ── AVAILABLE DEVICE PROFILES ─────────────────────────────────────
const PROFILES = [
  // 1. VR Spoof
  {
    os: 'Windows VR',
    browser: 'Discord VR',
    device: 'Quest',
    release_channel: 'stable',
    client_build_number: 364899,
  },
  // 2. Web Browser
  {
    os: 'Windows',
    browser: 'Chrome',
    device: '',
    release_channel: 'stable',
    client_build_number: 364899,
  },
  // 3. Desktop Client
  {
    os: 'Windows',
    browser: 'Discord Client',
    device: '',
    release_channel: 'stable',
    client_build_number: 364899,
  },
  // 4. PlayStation 5 Spoof
  {
    os: 'PS5',
    browser: 'Discord PlayStation',
    device: 'PlayStation 5',
    release_channel: 'stable',
    client_build_number: 364899,
  },
  // 5. Xbox Series X Spoof
  {
    os: 'Xbox',
    browser: 'Discord Xbox',
    device: 'Xbox Series X',
    release_channel: 'stable',
    client_build_number: 364899,
  }
];

// Helper to fill out missing blank fields required by the gateway
function generateRandomProperties() {
  const baseProfile = PROFILES[Math.floor(Math.random() * PROFILES.length)];
  return {
    browser_user_agent: '',
    browser_version: '',
    os_version: '',
    referrer: '',
    referring_domain: '',
    referrer_current: '',
    referring_domain_current: '',
    client_event_source: null,
    design_id: 0,
    accessibility_support_enabled: false,
    ...baseProfile
  };
}

// ── RAW GATEWAY INJECTION ─────────────────────────────────────────
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
        guild_versions: {},
        highest_last_message_id: '0',
        read_state_version: 0,
        user_guild_settings_version: -1,
        user_settings_version: -1,
        private_channels_version: '0',
        api_code_version: 0,
      };
    }
    return _send(data);
  };
  return _identify.call(this);
};

// ── TOKEN PARSING & INITIALIZATION ───────────────────────────────
const rawTokens = process.env.DISCORD_TOKENS;

if (!rawTokens) {
  console.error("[-] No tokens found in DISCORD_TOKENS environment variable.");
  process.exit(1);
}

const tokens = rawTokens.split(',').map(t => t.trim()).filter(t => t.length > 0);

console.log(`[+] Found ${tokens.length} tokens. Injecting randomized profiles...`);

tokens.forEach((token, index) => {
  const client = new Client({ checkUpdate: false });

  client.on('ready', () => {
    const currentOS = client.ws.shards.first()?._customProps?.os || 'Unknown';
    const currentBrowser = client.ws.shards.first()?._customProps?.browser || 'Unknown';
    
    console.log(`[+] Account [${index + 1}/${tokens.length}] is online: ${client.user.tag} (Logged in via: ${currentOS} / ${currentBrowser})`);
  });

  client.on('error', (err) => {
    console.error(`[-] Error on Account [${index + 1}]:`, err.message);
  });

  client.login(token).catch(err => {
    console.error(`[-] Failed to login token [${index + 1}]:`, err.message);
  });
});

process.on('unhandledRejection', () => {});
