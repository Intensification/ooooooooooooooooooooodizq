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
    headers = {
        "Authorization": token
    }
    
    # Different platform identifiers
    platform_ids = {
        "web": {"os": "Linux", "browser": "Chrome", "browser_version": "120.0.0.0"},
        "desktop": {"os": "Windows", "browser": "Discord Client", "browser_version": "1.0.9007"},
        "mobile": {"os": "Android", "browser": "Discord Android", "browser_version": "128.18"}
    }
    
    # WebSocket URL for Discord
    uri = "wss://gateway.discord.gg/?v=10&encoding=json"
    
    try:
        async with websockets.connect(uri) as websocket:
            # Send authentication with platform info
            auth_payload = {
                "op": 2,
                "d": {
                    "token": token,
                    "intents": 513,
                    "properties": platform_ids[platform],
                    "presence": {
                        "status": "online",
                        "since": 0,
                        "activities": [],
                        "afk": False
                    }
                }
            }
            
            await websocket.send(json.dumps(auth_payload))
            response = await websocket.recv()
            
            # Check if authentication was successful
            response_data = json.loads(response)
            if response_data.get("op") == 10:  # Ready event
                print(f"✅ Token logged in on {platform}")
                # Keep connection alive
                while True:
                    try:
                        await asyncio.sleep(30)
                        await websocket.ping()
                    except:
                        break
            else:
                print(f"❌ Failed to login on {platform}: {response_data}")
                
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
