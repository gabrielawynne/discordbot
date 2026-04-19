from discord.ext import commands

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.send("pong")

    @commands.command()
    async def smiley(self, ctx):
        await ctx.send(":)")

async def setup(bot):
    await bot.add_cog(Ping(bot))
