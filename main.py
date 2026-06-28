import asyncio
import json
import os
from dotenv import load_dotenv
import websockets

# Load environment variables from .env file
load_dotenv()

# Gather tokens from environment variables
TOKENS = [os.getenv("TOKEN_1"), os.getenv("TOKEN_2"), os.getenv("TOKEN_3")]

async def login_token(token, platform):
    if not token:
        print(f"❌ Missing token in .env file for: {platform}")
        return

    uri = "wss://gateway.discord.gg/?v=10&encoding=json"
    
    try:
        async with websockets.connect(uri) as ws:
            # 1. Handle Gateway Hello Handshake
            hello = json.loads(await ws.recv())
            interval = hello["d"]["heartbeat_interval"] / 1000
            
            last_sequence = None
            
            # Keep-alive heartbeat task
            async def heartbeat():
                while True:
                    await asyncio.sleep(interval)
                    # Must pass the last sequence number or None
                    await ws.send(json.dumps({"op": 1, "d": last_sequence}))
            
            asyncio.create_task(heartbeat())
            
            # 2. Assign exact properties Discord expects for each platform layout
            if platform == "desktop":
                properties = {
                    "os": "Windows",
                    "browser": "Discord Client",
                    "device": ""
                }
            elif platform == "web":
                properties = {
                    "os": "Windows",
                    "browser": "Chrome",
                    "device": ""
                }
            elif platform == "mobile":
                properties = {
                    "os": "Android",
                    "browser": "Discord Android",
                    "device": "Android Device"
                }
            else:
                properties = {
                    "os": "Windows",
                    "browser": "Chrome",
                    "device": ""
                }

            # Build Identify Payload
            auth = {
                "op": 2,
                "d": {
                    "token": token,
                    "properties": properties,
                    "presence": {
                        "status": "online",
                        "activities": [],
                        "afk": False
                    }
                }
            }
            
            # Send authentication
            await ws.send(json.dumps(auth))
            
            # 3. Process events loop
            while True:
                msg = json.loads(await ws.recv())
                
                # Update sequence tracking if provided by the gateway
                if "s" in msg and msg["s"] is not None:
                    last_sequence = msg["s"]
                
                # Check for Invalid Session response
                if msg.get("op") == 9:
                    print(f"❌ {platform} failed: Gateway flagged the session as invalid. (Check token validation)")
                    break
                    
                # Check for successful authentication
                if msg.get("t") == "READY":
                    print(f"✅ {platform} is now online!")
                    
    except Exception as e:
        print(f"❌ {platform} connection encountered an error: {e}")

async def main():
    # Staggering connection starts by 1.5 seconds avoids aggressive simultaneous API hits
    print("Starting connections...")
    
    print("Connecting Web profile...")
    task1 = asyncio.create_task(login_token(TOKENS[0], "web"))
    await asyncio.sleep(1.5)
    
    print("Connecting Desktop profile...")
    task2 = asyncio.create_task(login_token(TOKENS[1], "desktop"))
    await asyncio.sleep(1.5)
    
    print("Connecting Mobile profile...")
    task3 = asyncio.create_task(login_token(TOKENS[2], "mobile"))
    
    # Wait for all tasks to run concurrently
    await asyncio.gather(task1, task2, task3)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProcess terminated by user.")
