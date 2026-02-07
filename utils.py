import discord

MEDIA_EXTS = (
    ".png",".jpg",".jpeg",".gif",".webp",".svg",".tiff",".bmp",".heic",
    ".raw",".cr2",".nef",".orf",".sr2",".dng",
    ".mp4",".mov",".avi",".mkv",".flv",".wmv",".webm"
)

def is_media_message(msg: discord.Message) -> bool:
    return any(
        (a.filename or "").lower().endswith(MEDIA_EXTS)
        for a in msg.attachments
    )

async def send_log(bot, message: str, *, voice: bool = False, member=None):
    channel_id = (
        bot.config.get("vc_log_channel")
        if voice
        else bot.config.get("tc_log_channel")
    )

    if not channel_id:
        return

    channel = bot.get_channel(channel_id)
    if not channel:
        return

    # Choose color based on log type
    color = discord.Color.blue() if voice else discord.Color.green()

    embed = discord.Embed(
        description=message,
        color=color,
        timestamp=discord.utils.utcnow()
    )

    # Optional: attach user info
    if member:
        embed.set_author(
            name=str(member),
            icon_url=member.display_avatar.url
        )

    try:
        await channel.send(embed=embed)
    except Exception as e:
        print(f"[LOG ERROR] {e}")
