import discord
from discord.ext import commands

class PFP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def pfp(self, ctx, user: discord.User | None = None):
        user = user or ctx.author

        embed = discord.Embed(
            title=f"{user.name}'s Profile Picture",
            color=discord.Color.blurple()
        )
        embed.set_image(url=user.display_avatar.url)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(PFP(bot))
