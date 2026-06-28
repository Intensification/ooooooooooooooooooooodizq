import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio

load_dotenv()

tokens = [
    os.getenv("TOKEN_1"),
    os.getenv("TOKEN_2"),
    os.getenv("TOKEN_3")
]

# Client status strings: 'web', 'desktop', 'mobile'
client_statuses = ['web', 'desktop', 'mobile']

class SelfBot(commands.Bot):
    def __init__(self, token_index):
        intents = discord.Intents.default()
        intents.presences = True
        super().__init__(
            command_prefix=commands.when_mentioned_or('!'),
            self_bot=True,
            intents=intents
        )
        self.token_index = token_index
        self.token = tokens[token_index]
        self.client_status = client_statuses[token_index]

    async def on_ready(self):
        print(f"{self.user} is online!")
        # Force client status via ws.identify (low-level Discord call)
        await self.ws.identify(
            status='online',
            client_status={
                'desktop': None,
                'web': self.client_status == 'web',
                'mobile': self.client_status == 'mobile'
            }
        )

async def start_bot(token_index):
    try:
        bot = SelfBot(token_index)
        await bot.start(tokens[token_index])
    except Exception as e:
        print(f"Token {token_index + 1} failed: {e}")

async def main():
    for i, token in enumerate(tokens):
        if not token:
            print(f"Token {i+1} is missing!")
            continue
        asyncio.create_task(start_bot(i))

if __name__ == "__main__":
    asyncio.run(main())
