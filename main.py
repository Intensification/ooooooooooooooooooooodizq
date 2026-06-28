import asyncio
import json
import os
from dotenv import load_dotenv
import websockets

load_dotenv()
TOKENS = [os.getenv("TOKEN_1"), os.getenv("TOKEN_2"), os.getenv("TOKEN_3")]

async def login_token(token, platform):
    uri = "wss://gateway.discord.gg/?v=10&encoding=json"
    
    try:
        async with websockets.connect(uri) as ws:
            # Get hello and start heartbeat
            hello = json.loads(await ws.recv())
            interval = hello["d"]["heartbeat_interval"] / 1000
            
            async def heartbeat():
                while True:
                    await asyncio.sleep(interval)
                    await ws.send(json.dumps({"op": 1}))
            
            asyncio.create_task(heartbeat())
            
            # Simple auth payload
            auth = {
                "op": 2,
                "d": {
                    "token": token,
                    "properties": {
                        "os": "Windows" if platform != "mobile" else "Android",
                        "browser": "Chrome" if platform == "web" else "Discord Client" if platform == "desktop" else "Discord Android",
                        "device": ""
                    },
                    "presence": {"status": "online", "activities": []}
                }
            }
            
            await ws.send(json.dumps(auth))
            
            # Wait for ready
            while True:
                msg = json.loads(await ws.recv())
                if msg.get("t") == "READY":
                    print(f"✅ {platform} online")
                    break
            
            # Keep alive
            while True:
                await ws.recv()
                
    except Exception as e:
        print(f"❌ {platform} failed: {e}")

async def main():
    await asyncio.gather(
        login_token(TOKENS[0], "web"),
        login_token(TOKENS[1], "desktop"),
        login_token(TOKENS[2], "mobile")
    )

if __name__ == "__main__":
    asyncio.run(main())
