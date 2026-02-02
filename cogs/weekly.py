from discord.ext import commands
import discord
from datetime import datetime, timedelta, timezone

from config import load_config, save_config

WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6
}

class Weekly(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ---------------- CONFIG COMMANDS ----------------

    @commands.command(name="weeklysource")
    @commands.has_permissions(manage_guild=True)
    async def weeklysource(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            return await ctx.send("Usage: `!weeklysource #channel`")

        cfg = load_config()
        if channel.id not in cfg["vote_channels"]:
            return await ctx.send(
                f"{channel.mention} is not a vote channel. "
                f"Add it first with `!votechannel add {channel.mention}`"
            )

        cfg["weekly_source_channel"] = channel.id
        save_config(cfg)
        await ctx.send(f"Weekly source set to {channel.mention}")

    @commands.command(name="weeklypost")
    @commands.has_permissions(manage_guild=True)
    async def weeklypost(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            return await ctx.send("Usage: `!weeklypost #channel`")

        cfg = load_config()
        cfg["weekly_post_channel"] = channel.id
        save_config(cfg)
        await ctx.send(f"Weekly post channel set to {channel.mention}")

    @commands.command(name="weeklymsg")
    @commands.has_permissions(manage_guild=True)
    async def weeklymsg(self, ctx, *, text: str = None):
        if not text:
            return await ctx.send("Usage: `!weeklymsg <message text>`")

        cfg = load_config()
        cfg["weekly_message"] = text
        save_config(cfg)
        await ctx.send("Weekly message updated.")

    @commands.command(name="weeklytime")
    @commands.has_permissions(manage_guild=True)
    async def weeklytime(self, ctx, day: str = None, time: str = None):
        if not day or not time:
            return await ctx.send("Usage: `!weeklytime <day> <HH:MM>`")

        day = day.lower()
        if day not in WEEKDAYS:
            return await ctx.send("Invalid day.")

        try:
            hour, minute = map(int, time.split(":"))
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError
        except ValueError:
            return await ctx.send("Invalid time format.")

        cfg = load_config()
        cfg["weekly_day"] = WEEKDAYS[day]
        cfg["weekly_hour"] = hour
        cfg["weekly_minute"] = minute
        save_config(cfg)

        await ctx.send(f"Weekly post set for {day.title()} at {time} (Central)")

    # ---------------- WEEKLY TEST ----------------

    @commands.command(name="weeklytest")
    @commands.has_permissions(manage_guild=True)
    async def weeklytest(self, ctx, days: int = 7):
        cfg = load_config()

        src_id = cfg.get("weekly_source_channel")
        post_id = cfg.get("weekly_post_channel")

        if not src_id:
            return await ctx.send("Set the weekly source first: `!weeklysource #votechannel`")
        if not post_id:
            return await ctx.send("Set the post channel first: `!weeklypost #channel`")

        src = ctx.guild.get_channel(src_id)
        out = ctx.guild.get_channel(post_id)

        if not src or not out:
            return await ctx.send("Weekly source or post channel not found.")

        days = max(1, min(int(days), 30))
        after_dt = datetime.now(timezone.utc) - timedelta(days=days)

        best_msg = None
        best_upvotes = -1
        best_created_ts = -1

        async for msg in src.history(limit=None, after=after_dt):
            if msg.author.bot:
                continue

            upvotes = 0
            for r in msg.reactions:
                if str(r.emoji) == "👍":
                    upvotes = max(0, r.count - 1)
                    break

            if upvotes <= 0:
                continue

            created_ts = msg.created_at.timestamp() if msg.created_at else 0

            if (upvotes > best_upvotes) or (
                upvotes == best_upvotes and created_ts > best_created_ts
            ):
                best_msg = msg
                best_upvotes = upvotes
                best_created_ts = created_ts

        if not best_msg:
            return await out.send(
                f"No messages with 👍 found in the last {days} day(s) in {src.mention}."
            )

        custom = cfg.get("weekly_message", "🏆 Weekly winner!")
        final_message = custom.replace("{winner}", best_msg.author.mention)

        await out.send(
            final_message,
            allowed_mentions=discord.AllowedMentions(users=True)
        )
        await out.send(f"{best_msg.jump_url}  (👍 {best_upvotes})")
        await out.send(f"> {best_msg.content}" if best_msg.content else "> *(no caption)*")

        if best_msg.attachments:
            files = []
            for a in best_msg.attachments[:10]:
                try:
                    files.append(await a.to_file())
                except Exception:
                    pass
            if files:
                await out.send(files=files)

async def setup(bot):
    await bot.add_cog(Weekly(bot))
