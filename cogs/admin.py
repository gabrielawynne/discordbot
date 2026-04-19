import os
import sys
from datetime import datetime, timedelta, timezone
import discord
from discord.ext import commands

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["restart"])
    async def r(self, ctx):
        if ctx.author.id != 992695156161658910:
            return
        await ctx.send("Restarting.")
        os.execv(sys.executable, [sys.executable] + sys.argv)

    @commands.group(invoke_without_command=True)
    @commands.has_permissions(manage_messages=True)
    async def mop(self, ctx, amount: int = None):
        if amount is None:
            await ctx.send("Usage: `!mop <amount>` or `!mop recent [minutes]`")
            return
        if amount <= 0:
            await ctx.send("Amount must be greater than 0.")
            return
        deleted = await ctx.channel.purge(limit=min(amount, 100) + 1)
        msg = await ctx.send(f"Deleted {len(deleted)-1} messages.")
        await msg.delete(delay=3)

    @mop.command(name="recent")
    @commands.has_permissions(manage_messages=True)
    async def mop_recent(self, ctx, minutes: int = 5):
        after = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        deleted = await ctx.channel.purge(after=after)
        msg = await ctx.send(f"Deleted {len(deleted)} messages from the last {minutes} minutes.")
        await msg.delete(delay=3)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def cost(self, ctx):
        usage = self.bot.config.get("usage", {"prompt_tokens": 0, "completion_tokens": 0})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)

        # gpt-4o-mini pricing: $0.15 / 1M input, $0.60 / 1M output
        input_cost = (prompt_tokens / 1_000_000) * 0.15
        output_cost = (completion_tokens / 1_000_000) * 0.60
        total = input_cost + output_cost

        embed = discord.Embed(title="API Usage & Cost", color=0x5865f2)
        embed.add_field(name="Input tokens", value=f"{prompt_tokens:,}", inline=True)
        embed.add_field(name="Output tokens", value=f"{completion_tokens:,}", inline=True)
        embed.add_field(name="Total tokens", value=f"{prompt_tokens + completion_tokens:,}", inline=True)
        embed.add_field(name="Input cost", value=f"${input_cost:.4f}", inline=True)
        embed.add_field(name="Output cost", value=f"${output_cost:.4f}", inline=True)
        embed.add_field(name="Total cost", value=f"${total:.4f}", inline=True)
        embed.set_footer(text="Based on gpt-4o-mini pricing")
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setfoodchannel(self, ctx, channel_id: int):
        channel = ctx.guild.get_channel(channel_id)
        if channel is None:
            await ctx.send("Invalid channel ID.")
            return
        self.bot.config["food_channel"] = channel.id
        self.bot.save_config()
        await ctx.send(f"Food review channel set to {channel.mention}")

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

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setlogcolor(self, ctx, event: str, hex_color: str):
        valid_events = [
            "member_join", "member_leave",
            "voice_join", "voice_leave", "voice_move",
            "message_delete", "message_edit", "bulk_delete",
            "role_add", "role_remove", "nickname_change",
            "reaction_add", "reaction_remove"
        ]

        if event not in valid_events:
            await ctx.send(f"Invalid event. Choose from: `{'`, `'.join(valid_events)}`")
            return

        hex_color = hex_color.lstrip("#")
        try:
            color_int = int(hex_color, 16)
        except ValueError:
            await ctx.send("Invalid hex color. Example: `!setlogcolor message_delete ff0000`")
            return

        self.bot.config.setdefault("log_colors", {})[event] = color_int
        self.bot.save_config()

        await ctx.send(f"Color for `{event}` set to `#{hex_color.upper()}`.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def logcolors(self, ctx):
        colors = self.bot.config.get("log_colors", {})
        embed = discord.Embed(title="Log Colors", color=discord.Color.blurple())
        for event, hex_int in colors.items():
            embed.add_field(
                name=event,
                value=f"`#{hex_int:06X}`",
                inline=True
            )
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Admin(bot))
