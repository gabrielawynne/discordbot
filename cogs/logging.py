from discord.ext import commands
from utils import send_log


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
            f"**Member joined:** {member} ({member.id})"
        )

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await send_log(
            self.bot,
            f"**Member left:** {member} ({member.id})"
        )

    # ----------------------------
    # VOICE EVENTS
    # ----------------------------

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # Joined a voice channel
        if before.channel is None and after.channel is not None:
            await send_log(
                self.bot,
                f"**Joined voice channel:** {after.channel}",
                voice=True,
                member=member
            )

        # Left a voice channel
        elif before.channel is not None and after.channel is None:
            await send_log(
                self.bot,
                f"**Left voice channel:** {before.channel}",
                voice=True,
                member=member
            )

        # Moved between voice channels
        elif before.channel != after.channel:
            await send_log(
                self.bot,
                "**Member joined the server**",
                member=member
            )


async def setup(bot):
    await bot.add_cog(Logging(bot))
