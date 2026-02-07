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

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setvclog(self, ctx, channel_id: int):
        channel = ctx.guild.get_channel(channel_id)

        if channel is None:
            await ctx.send("Invalid channel ID.")
            return

        self.bot.config["vc_log_channel"] = channel.id
        self.bot.save_config()

        await ctx.send(f"VC log channel set to {channel.mention}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setlog(self, ctx, channel_id: int):
        channel = ctx.guild.get_channel(channel_id)

        if channel is None:
            await ctx.send("Invalid channel ID.")
            return

        self.bot.config["tc_log_channel"] = channel.id
        self.bot.save_config()

        await ctx.send(f"Server log channel set to {channel.mention}")


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unsetvclog(self, ctx):
        self.bot.config["vc_log_channel"] = None
        self.bot.save_config()

        await ctx.send("VC logging removed.")


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unsetlog(self, ctx):
        self.bot.config["tc_log_channel"] = None
        self.bot.save_config()

        await ctx.send("Server logging removed.")
"""
    @commands.command()
    async def testlog(self, ctx):
        from utils import send_log

        await send_log(self.bot, "Test server log")
        await send_log(self.bot, "Test VC log", voice=True)

        await ctx.send("Sent test logs.")
"""


async def setup(bot):
    await bot.add_cog(Admin(bot))
