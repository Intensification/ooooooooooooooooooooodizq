import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Get tokens
TOKENS = [
    os.getenv("TOKEN_1"),
    os.getenv("TOKEN_2"),
    os.getenv("TOKEN_3")
]

# Target platforms for each token
PLATFORMS = ['web', 'desktop', 'mobile']

class SelfBot(commands.Bot):
    def __init__(self, index):
        intents = discord.Intents.default()
        intents.presences = True
        super().__init__(
            command_prefix=commands.when_mentioned_or("!"),
            self_bot=True,
            intents=intents
        )
        self.index = index
        self.token = TOKENS[index]
        self.platform = PLATFORMS[index]

    async def on_ready(self):
        user = self.user
        print(f"✅ {user} is online ({self.platform} client)")
        
        # Force the client status (Platform) directly
        # This makes Discord show the browser/app icon next to your name
        await self.ws.identify(
            status='online',
            client_status={
                'desktop': self.platform == 'desktop',
                'mobile': self.platform == 'mobile',
                'web': self.platform == 'web'
            }
        )
        
        # Log success to Railway logs
        print(f"[{self.platform}] Status updated successfully.")

async def run_token(index):
    if not TOKENS[index]:
        print(f"❌ Token {index+1} missing in .env")
        return
    try:
        bot = SelfBot(index)
        await bot.start(TOKENS[index])
    except Exception as e:
        print(f"❌ Token {index+1} failed: {e}")

async def main():
    tasks = [run_token(i) for i in range(3) if TOKENS[i]]
    if not tasks:
        print("No tokens found. Check .env file.")
        return
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
