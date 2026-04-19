import discord
from discord.ext import commands


SECTIONS = [
    {
        "title": "General",
        "color": 0x5865f2,
        "commands": [
            ("!ping", "", "Check if the bot is alive"),
            ("!pfp", "[user]", "Show yours or someone else's profile picture"),
        ]
    },
    {
        "title": "Moderation",
        "color": 0xed4245,
        "commands": [
            ("!mop",         "<amount>",   "Bulk delete up to 100 messages in the current channel"),
            ("!mop recent",  "[minutes]",  "Delete messages from the last N minutes (default: 5)"),
            ("!setfoodchannel", "<channel_id>", "Set the food review channel"),
        ]
    },
    {
        "title": "Logging",
        "color": 0x57f287,
        "commands": [
            ("!setlog",      "<channel_id>",  "Set the server event log channel"),
            ("!unsetlog",    "",              "Remove the server event log channel"),
            ("!setvclog",    "<channel_id>",  "Set the voice log channel"),
            ("!unsetvclog",  "",              "Remove the voice log channel"),
            ("!setlogcolor", "<event> <hex>", "Change the embed color for a log event"),
            ("!logcolors",   "",              "Show all current log event colors"),
        ]
    },
    {
        "title": "Weekly Winner",
        "color": 0xfee75c,
        "commands": [
            ("!weeklysource", "#channel",      "Set the vote channel to pull the winner from"),
            ("!weeklypost",   "#channel",      "Set the channel where the winner gets posted"),
            ("!weeklymsg",    "<text>",        "Set the winner announcement message (use {winner} for mention)"),
            ("!weeklytime",   "<day> <HH:MM>", "Schedule the weekly post (e.g. friday 18:00)"),
            ("!weeklytest",   "[days]",        "Manually trigger the weekly winner post"),
        ]
    },
    {
        "title": "Bot",
        "color": 0x979c9f,
        "commands": [
            ("!r", "", "Restart the bot and apply any new changes (alias: !restart)"),
        ]
    },
]

LOG_EVENTS = [
    "member_join", "member_leave",
    "voice_join", "voice_leave", "voice_move",
    "message_delete", "message_edit", "bulk_delete",
    "role_add", "role_remove", "nickname_change",
    "reaction_add", "reaction_remove",
]


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help(self, ctx, section: str = None):
        if section:
            await self._send_section(ctx, section.lower())
        else:
            await self._send_overview(ctx)

    async def _send_overview(self, ctx):
        embed = discord.Embed(
            title="Bot Commands",
            description="Use `!help <section>` to see detailed usage for a category.",
            color=0x5865f2
        )

        for s in SECTIONS:
            names = " • ".join(f"`{cmd}`" for cmd, _, _ in s["commands"])
            embed.add_field(
                name=s["title"],
                value=names,
                inline=False
            )

        embed.add_field(
            name="Auto Features",
            value=(
                "**Food review** — post a food image in the food channel to get an AI review\n"
                "**Vote reactions** — thumbs up/down auto-added to media in vote channels\n"
                "**Heart reactions** — heart auto-added to media in heart channels"
            ),
            inline=False
        )

        embed.set_footer(text=f"Prefix: !  •  {len(SECTIONS)} categories")
        await ctx.send(embed=embed)

    async def _send_section(self, ctx, section: str):
        match = next((s for s in SECTIONS if s["title"].lower() == section), None)

        if not match:
            names = ", ".join(f"`{s['title'].lower()}`" for s in SECTIONS)
            await ctx.send(f"Unknown section. Try one of: {names}")
            return

        embed = discord.Embed(
            title=match["title"],
            color=match["color"]
        )

        for cmd, args, desc in match["commands"]:
            usage = f"`{cmd} {args}`".strip() if args else f"`{cmd}`"
            embed.add_field(name=usage, value=desc, inline=False)

        if match["title"] == "Logging":
            embed.add_field(
                name="Valid log events for `!setlogcolor`",
                value=" • ".join(f"`{e}`" for e in LOG_EVENTS),
                inline=False
            )

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Help(bot))
