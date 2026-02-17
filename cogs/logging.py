from discord.ext import commands
from utils import send_log

import discord


class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ----------------------------
    # MEMBER EVENTS
    # ----------------------------

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await send_log(
            self.bot,
            f"Member joined: {member} ({member.id})"
        )

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await send_log(
            self.bot,
            f"Member left: {member} ({member.id})"
        )

    # ----------------------------
    # VOICE EVENTS
    # ----------------------------

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        
        # Both changed
        if before.self_mute != after.self_mute and before.self_deaf != after.self_deaf:

            if after.self_mute and after.self_deaf:
                action = "muted and deafened themselves"
            elif not after.self_mute and not after.self_deaf:
                action = "unmuted and undeafened themselves"
            elif after.self_mute and not after.self_deaf:
                action = "muted and undeafened themselves"
            elif not after.self_mute and after.self_deaf:
                action = "unmuted and deafened themselves"

            await send_log(
                self.bot,
                f"{member} {action}"
            )

        # Only mute changed
        elif before.self_mute != after.self_mute:
            action = "muted themselves" if after.self_mute else "unmuted themselves"

            await send_log(
                self.bot,
                f"{member} {action}"
            )

        # Only deaf changed
        elif before.self_deaf != after.self_deaf:
            action = "deafened themselves" if after.self_deaf else "undeafened themselves"

            await send_log(
                self.bot,
                f"{member} {action}"
            )
        
        # Joined a voice channel
        if before.channel is None and after.channel is not None:
            await send_log(
                self.bot,
                f"Joined voice channel: {after.channel}",
                voice=True,
                member=member
            )

        # Left a voice channel
        elif before.channel is not None and after.channel is None:
            await send_log(
                self.bot,
                f"Left voice channel: {before.channel}",
                voice=True,
                member=member
            )

        # Moved between voice channels
        elif before.channel != after.channel:
            await send_log(
                self.bot,
                f"Switched voice channels: {before.channel} -> {after.channel}",
                member=member
            )


async def setup(bot):
    await bot.add_cog(Logging(bot))
