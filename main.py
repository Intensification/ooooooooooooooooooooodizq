import asyncio
import json
import os
from dotenv import load_dotenv
import websockets

# Load tokens from environment
load_dotenv()
TOKENS = [
    os.getenv("TOKEN_1"),
    os.getenv("TOKEN_2"),
    os.getenv("TOKEN_3")
]

async def login_token(token, platform):
    # WebSocket URL for Discord
    uri = "wss://gateway.discord.gg/?v=10&encoding=json"
    
    try:
        async with websockets.connect(uri) as websocket:
            # Set platform-specific properties
            if platform == "web":
                properties = {
                    "os": "Windows",
                    "browser": "Chrome",
                    "device": "",
                    "browser_user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "browser_version": "120.0.0.0",
                    "os_version": "10",
                    "referrer": "",
                    "referring_domain": "",
                    "referrer_current": "",
                    "referring_domain_current": "",
                    "release_channel": "stable",
                    "system_locale": "en-US",
                    "client_build_number": 0,
                    "client_event_source": None
                }
            elif platform == "desktop":
                properties = {
                    "os": "Windows",
                    "browser": "Discord Client",
                    "browser_version": "1.0.9007",
                    "os_version": "10.0.19045",
                    "os_arch": "x64",
                    "device": "",
                    "browser_user_agent": "",
                    "system_locale": "en-US",
                    "client_build_number": 99999,
                    "release_channel": "stable"
                }
            else:  # mobile
                properties = {
                    "os": "Android",
                    "browser": "Discord Android",
                    "browser_version": "128.18",
                    "os_version": "11",
                    "device": "SM-G973F",
                    "browser_user_agent": "Discord-Android/128.18",
                    "client_build_number": 12818,
                    "system_locale": "en-US"
                }
            
            # Send authentication
            auth_payload = {
                "op": 2,
                "d": {
                    "token": token,
                    "capabilities": 125,
                    "properties": properties,
                    "presence": {
                        "status": "online",
                        "since": 0,
                        "activities": [],
                        "afk": False
                    },
                    "compress": True,
                    "client_state": {
                        "guild_hashes": {},
                        "highest_last_message_id": "0",
                        "read_state_version": -1,
                        "user_guild_settings_version": -1,
                        "user_settings_version": -1
                    }
                }
            }
            
            await websocket.send(json.dumps(auth_payload))
            
            # Wait for ready event
            while True:
                response = await websocket.recv()
                response_data = json.loads(response)
                
                if response_data.get("op") == 10:  # Hello event
                    heartbeat_interval = response_data["d"]["heartbeat_interval"] / 1000
                    
                    # Start heartbeat
                    async def heartbeat():
                        while True:
                            await asyncio.sleep(heartbeat_interval)
                            await websocket.send(json.dumps({"op": 1, "d": None}))
                    
                    asyncio.create_task(heartbeat())
                
                elif response_data.get("t") == "READY":
                    print(f"✅ Token logged in on {platform}")
                    break
                elif response_data.get("op") == 9:  # Invalid session
                    print(f"❌ Invalid session for {platform} token")
                    break
                
            # Keep connection alive
            while True:
                try:
                    await websocket.recv()
                except:
                    break
                
    except Exception as e:
        print(f"❌ Error with {platform} login: {e}")

async def main():
    tasks = [
        login_token(TOKENS[0], "web"),
        login_token(TOKENS[1], "desktop"),
        login_token(TOKENS[2], "mobile")
    ]
    
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
