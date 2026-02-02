from discord.ext import commands

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def r(self, ctx):
        await ctx.send("Penciling out... ✏️")
        await self.bot.close()

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def mop(self, ctx, amount: int):
        deleted = await ctx.channel.purge(limit=min(amount, 100) + 1)
        msg = await ctx.send(f"🧹 Deleted {len(deleted)-1} messages.")
        await msg.delete(delay=3)

async def setup(bot):
    await bot.add_cog(Admin(bot))
