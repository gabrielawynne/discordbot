from discord.ext import commands
from utils import is_media_message

class Reactions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        cfg = self.bot.config

        if message.channel.id in cfg["vote_channels"] and is_media_message(message):
            await message.add_reaction("👍")
            await message.add_reaction("👎")

        if message.channel.id in cfg["heart_channels"] and is_media_message(message):
            await message.add_reaction("❤️")

async def setup(bot):
    await bot.add_cog(Reactions(bot))
