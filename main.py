import asyncio
import json
import os
from dotenv import load_dotenv
import websockets

# Load environment variables from .env file
load_dotenv()

# Gather tokens from environment variables
TOKENS = [os.getenv("TOKEN_1"), os.getenv("TOKEN_2"), os.getenv("TOKEN_3")]

async def login_token(token, identifier):
    if not token:
        print(f"❌ Missing token in .env file for: {identifier}")
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
                    await ws.send(json.dumps({"op": 1, "d": last_sequence}))
            
            asyncio.create_task(heartbeat())
            
            # 2. Emulate the working Desktop Client properties for all connections
            properties = {
                "os": "Windows",
                "browser": "Discord Client",
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
                
                if "s" in msg and msg["s"] is not None:
                    last_sequence = msg["s"]
                
                # Check for Invalid Session response
                if msg.get("op") == 9:
                    print(f"❌ Token {identifier} failed: Gateway flagged the session as invalid.")
                    break
                    
                # Check for successful authentication
                if msg.get("t") == "READY":
                    print(f"✅ Token {identifier} is now online using Desktop Client properties layout!")
                    
    except Exception as e:
        print(f"❌ Token {identifier} connection encountered an error: {e}")

async def main():
    print("Starting connections...")
    
    # Staggering connection starts to avoid spamming the gateway simultaneously
    print("Connecting Token 1...")
    task1 = asyncio.create_task(login_token(TOKENS[0], "1"))
    await asyncio.sleep(1.5)
    
    print("Connecting Token 2...")
    task2 = asyncio.create_task(login_token(TOKENS[1], "2"))
    await asyncio.sleep(1.5)
    
    print("Connecting Token 3...")
    task3 = asyncio.create_task(login_token(TOKENS[2], "3"))
    
    # Wait for all tasks to run concurrently
    await asyncio.gather(task1, task2, task3)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProcess terminated by user.")
