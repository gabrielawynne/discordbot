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
