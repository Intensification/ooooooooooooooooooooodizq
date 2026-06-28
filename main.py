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
        print(f"❌ Token {identifier} is empty or missing in your .env file!")
        return

    # Clean up token strings in case there are accidental spaces or extra quotes
    token = token.strip().replace('"', '').replace("'", "")
    
    # Print a safe snippet of the token to confirm the script is actually reading it
    print(f"🔄 Attempting connection for Token {identifier} (Starts with: {token[:15]}...)")

    uri = "wss://gateway.discord.gg/?v=10&encoding=json"
    
    try:
        async with websockets.connect(uri) as ws:
            # 1. Handle Gateway Hello Handshake
            hello = json.loads(await ws.recv())
            interval = hello["d"]["heartbeat_interval"] / 1000
            
            last_sequence = None
            
            # Keep-alive heartbeat task
            async def heartbeat():
                try:
                    while True:
                        await asyncio.sleep(interval)
                        await ws.send(json.dumps({"op": 1, "d": last_sequence}))
                except asyncio.CancelledError:
                    pass
            
            hb_task = asyncio.create_task(heartbeat())
            
            # 2. Use Desktop Client properties for all connections
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
                try:
                    msg = json.loads(await ws.recv())
                except websockets.exceptions.ConnectionClosed as cc:
                    # Catch the exact reason Discord disconnected this token
                    print(f"❌ Token {identifier} disconnected by server. Code: {cc.code}, Reason: {cc.reason}")
                    hb_task.cancel()
                    break
                
                if "s" in msg and msg["s"] is not None:
                    last_sequence = msg["s"]
                
                # Check for Invalid Session response
                if msg.get("op") == 9:
                    print(f"❌ Token {identifier} failed: Op 9 Invalid Session (Token is dead or invalid).")
                    hb_task.cancel()
                    break
                    
                # Check for successful authentication
                if msg.get("t") == "READY":
                    user_info = msg["d"].get("user", {})
                    username = user_info.get("username", f"User_{identifier}")
                    print(f"✅ Token {identifier} ({username}) is now ONLINE!")
                    
    except Exception as e:
        print(f"❌ Token {identifier} connection error: {e}")

async def main():
    print("=== Starting Token Online Script ===")
    
    # Increased the delay to 3 seconds between connections to prevent IP rate limits
    print("\n[1/3] Starting Token 1...")
    task1 = asyncio.create_task(login_token(TOKENS[0], "1"))
    await asyncio.sleep(3.0)
    
    print("\n[2/3] Starting Token 2...")
    task2 = asyncio.create_task(login_token(TOKENS[1], "2"))
    await asyncio.sleep(3.0)
    
    print("\n[3/3] Starting Token 3...")
    task3 = asyncio.create_task(login_token(TOKENS[2], "3"))
    
    # Run all connections concurrently
    await asyncio.gather(task1, task2, task3)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProcess terminated by user.")
