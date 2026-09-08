import discord
from discord.ext import commands
from version import VERSION, CHANGELOG

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
        embed = discord.Embed(
            title=f"Bot Version v{VERSION}",
            color=0x5865f2
        )
        log = "\n".join(f"`v{ver}` — {desc}" for ver, desc in CHANGELOG)
        embed.add_field(name="Changelog", value=log, inline=False)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Ping(bot))
