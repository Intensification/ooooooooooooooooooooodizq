import os
import discord
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()

# Get tokens from environment
tokens = [
    os.getenv("TOKEN_1"),
    os.getenv("TOKEN_2"),
    os.getenv("TOKEN_3")
]

# Define platforms for each token
platforms = [
    discord.Platform.web,      # Token 1: Web
    discord.Platform.desktop,  # Token 2: Desktop (Discord app)
    discord.Platform.mobile    # Token 3: Mobile
]

class SelfBot(discord.Client):
    def __init__(self, token_index):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.token_index = token_index
        self.token = tokens[token_index]
        self.platform = platforms[token_index]
        
    async def on_ready(self):
        print(f"{self.user} is now online")
        
        # Set just the platform (no activity)
        await self.ws.identify(
            status=discord.Status.online,
            platform=self.platform
        )

async def start_bot(token_index):
    try:
        bot = SelfBot(token_index)
        await bot.start(tokens[token_index])
    except Exception as e:
        print(f"Error with token {token_index + 1}: {e}")

async def main():
    tasks = []
    for i in range(3):
        if tokens[i]:  # Only start if token exists
            tasks.append(start_bot(i))
    
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
