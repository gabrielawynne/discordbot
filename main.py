import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import asyncio

load_dotenv()

from scheduler import weekly_scheduler

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.guilds = True

class Bot(commands.Bot):
    async def setup_hook(self):
        await self.load_extension("cogs.admin")
        await self.load_extension("cogs.reactions")
        await self.load_extension("cogs.weekly")
        await self.load_extension("cogs.pfp")
        await self.load_extension("cogs.ping")
        await self.load_extension("cogs.logging")

        asyncio.create_task(weekly_scheduler(self))


bot = Bot(command_prefix="!", intents=intents)

from config import load_config, save_config

bot.config = load_config()
bot.save_config = lambda: save_config(bot.config)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

bot.run(os.getenv("DISCORD_TOKEN"))

