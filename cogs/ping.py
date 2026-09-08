import discord
from discord.ext import commands
from version import VERSION

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.send("pong")

    @commands.command()
    async def smiley(self, ctx):
        await ctx.send(":)")

    @commands.command()
    async def version(self, ctx):
        await ctx.send(f"version `v{VERSION}`")

async def setup(bot):
    await bot.add_cog(Ping(bot))
