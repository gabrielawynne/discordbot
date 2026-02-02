import asyncio
from datetime import datetime, timedelta, timezone
from config import load_config

CENTRAL = timezone(timedelta(hours=-6))

async def weekly_scheduler(bot):
    await bot.wait_until_ready()

    while not bot.is_closed():
        cfg = load_config()

        if None in (
            cfg["weekly_day"],
            cfg["weekly_hour"],
            cfg["weekly_minute"],
            cfg["weekly_post_channel"],
            cfg["weekly_source_channel"]
        ):
            await asyncio.sleep(60)
            continue

        now = datetime.now(CENTRAL)
        target = now.replace(
            hour=cfg["weekly_hour"],
            minute=cfg["weekly_minute"],
            second=0,
            microsecond=0
        )

        days_ahead = (cfg["weekly_day"] - now.weekday()) % 7
        if days_ahead == 0 and target <= now:
            days_ahead = 7

        await asyncio.sleep((target + timedelta(days=days_ahead) - now).total_seconds())

        channel = bot.get_channel(cfg["weekly_post_channel"])
        if channel:
            ctx = await bot.get_context(await channel.send("⏳ Weekly results..."))
            await bot.get_command("weeklytest")(ctx, 7)

        await asyncio.sleep(60)
