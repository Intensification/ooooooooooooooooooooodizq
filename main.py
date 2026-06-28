import asyncio
import json
import os
from dotenv import load_dotenv
import websockets

load_dotenv()

# Ensure these are set in your .env file
TOKENS = [os.getenv("TOKEN_1"), os.getenv("TOKEN_2"), os.getenv("TOKEN_3")]

async def login_token(token, platform):
    if not token:
        print(f"❌ Missing token for {platform}")
        return

    uri = "wss://gateway.discord.gg/?v=10&encoding=json"
    
    try:
        async with websockets.connect(uri) as ws:
            # Step 1: Handle Hello standard handshake
            hello = json.loads(await ws.recv())
            interval = hello["d"]["heartbeat_interval"] / 1000
            
            # Track sequence number for heartbeats
            last_sequence = None
            
            async def heartbeat():
                while True:
                    await asyncio.sleep(interval)
                    # The gateway requires the 'd' key containing the last sequence number
                    await ws.send(json.dumps({"op": 1, "d": last_sequence}))
            
            asyncio.create_task(heartbeat())
            
            # Step 2: Identify payload
            auth = {
                "op": 2,
                "d": {
                    "token": token,
                    "properties": {
                        "os": "Windows" if platform != "mobile" else "Android",
                        "browser": "Chrome" if platform == "web" else "Discord Client",
                        "device": ""
                    },
                    "presence": {"status": "online", "activities": [], "afk": False}
                }
            }
            
            await ws.send(json.dumps(auth))
            
            # Step 3: Listen for events and update sequence
            while True:
                msg = json.loads(await ws.recv())
                
                # Update sequence number if present
                if "s" in msg and msg["s"] is not None:
                    last_sequence = msg["s"]
                    
                if msg.get("t") == "READY":
                    print(f"✅ {platform} is now online!")
                    
    except Exception as e:
        print(f"❌ {platform} connection encountered an error: {e}")

async def main():
    await asyncio.gather(
        login_token(TOKENS[0], "web"),
        login_token(TOKENS[1], "desktop"),
        login_token(TOKENS[2], "mobile")
    )

if __name__ == "__main__":
    asyncio.run(main())
