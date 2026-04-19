import io
from datetime import datetime, timezone
import discord
from discord.ext import commands
from utils import send_log


class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._vc_join_times: dict[int, datetime] = {}

    # ----------------------------
    # MEMBER EVENTS
    # ----------------------------

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await send_log(
            self.bot,
            f"**Member joined:** {member} ({member.id})",
            event="member_join"
        )

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await send_log(
            self.bot,
            f"**Member left:** {member} ({member.id})",
            event="member_leave"
        )

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.nick != after.nick:
            old = before.nick or before.name
            new = after.nick or after.name
            await send_log(
                self.bot,
                f"**Nickname changed**\n**Before:** {old}\n**After:** {new}",
                member=after,
                event="nickname_change"
            )

        added = [r for r in after.roles if r not in before.roles]
        removed = [r for r in before.roles if r not in after.roles]

        for role in added:
            await send_log(
                self.bot,
                f"**Role added:** {role.mention}",
                member=after,
                event="role_add"
            )

        for role in removed:
            await send_log(
                self.bot,
                f"**Role removed:** {role.mention}",
                member=after,
                event="role_remove"
            )

    # ----------------------------
    # VOICE EVENTS
    # ----------------------------

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel is None and after.channel is not None:
            self._vc_join_times[member.id] = datetime.now(timezone.utc)
            await send_log(
                self.bot,
                f"**Joined voice channel:** {after.channel}",
                voice=True,
                member=member,
                event="voice_join"
            )

        elif before.channel is not None and after.channel is None:
            joined_at = self._vc_join_times.pop(member.id, None)
            if joined_at:
                delta = datetime.now(timezone.utc) - joined_at
                total = int(delta.total_seconds())
                h, rem = divmod(total, 3600)
                m, s = divmod(rem, 60)
                parts = []
                if h: parts.append(f"{h}h")
                if m: parts.append(f"{m}m")
                parts.append(f"{s}s")
                duration = " ".join(parts)
            else:
                duration = "unknown"

            await send_log(
                self.bot,
                f"**Left voice channel:** {before.channel} — Duration: {duration}",
                voice=True,
                member=member,
                event="voice_leave"
            )

        elif before.channel != after.channel:
            await send_log(
                self.bot,
                f"**Moved voice channels:** {before.channel} → {after.channel}",
                voice=True,
                member=member,
                event="voice_move"
            )

    # ----------------------------
    # MESSAGE EVENTS
    # ----------------------------

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return

        content = message.content or "*[no text content]*"
        lines = [f"**Message deleted in {message.channel.mention}**", f"> {content}"]

        if message.attachments:
            names = ", ".join(a.filename for a in message.attachments)
            lines.append(f"**Attachments:** {names}")

        await send_log(
            self.bot,
            "\n".join(lines),
            member=message.author,
            event="message_delete"
        )

    @commands.Cog.listener()
    async def on_raw_bulk_message_delete(self, payload):
        channel = self.bot.get_channel(payload.channel_id)
        count = len(payload.message_ids)
        channel_mention = channel.mention if channel else f"<#{payload.channel_id}>"

        file = None
        cached = sorted(payload.cached_messages, key=lambda m: m.created_at)
        if cached:
            lines = []
            for msg in cached:
                ts = msg.created_at.strftime("%Y-%m-%d %H:%M:%S UTC")
                content = msg.content or "[no text content]"
                lines.append(f"[{ts}] {msg.author} ({msg.author.id}): {content}")
                for a in msg.attachments:
                    lines.append(f"  [attachment: {a.filename}]")
            txt = "\n".join(lines).encode("utf-8")
            file = discord.File(io.BytesIO(txt), filename="deleted_messages.txt")

        await send_log(
            self.bot,
            f"**{count} messages bulk deleted in {channel_mention}**" + ("" if cached else "\n*Message content not available (not cached)*"),
            event="bulk_delete",
            file=file
        )

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if after.author.bot:
            return
        if before.content == after.content:
            return

        lines = [
            f"**Message edited in {after.channel.mention}** — [Jump to message]({after.jump_url})",
            f"**Before:** {before.content or '*[no text content]*'}",
            f"**After:** {after.content or '*[no text content]*'}",
        ]

        await send_log(
            self.bot,
            "\n".join(lines),
            member=after.author,
            event="message_edit"
        )

    # ----------------------------
    # REACTION EVENTS
    # ----------------------------

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot:
            return
        await send_log(
            self.bot,
            f"**Reaction added** {reaction.emoji} in {reaction.message.channel.mention} — [Jump to message]({reaction.message.jump_url})",
            member=user,
            event="reaction_add"
        )

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        if user.bot:
            return
        await send_log(
            self.bot,
            f"**Reaction removed** {reaction.emoji} in {reaction.message.channel.mention} — [Jump to message]({reaction.message.jump_url})",
            member=user,
            event="reaction_remove"
        )


async def setup(bot):
    await bot.add_cog(Logging(bot))
