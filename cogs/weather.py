import asyncio
from datetime import datetime, timedelta, timezone
import aiohttp
import discord
from discord.ext import commands, tasks

CENTRAL = timezone(timedelta(hours=-6))


class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.daily_weather.start()

    def cog_unload(self):
        self.daily_weather.cancel()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    async def get_forecast(self, lat, lon):
        """Fetch today's high, low, and rain % from Open-Meteo (no API key needed)."""
        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            "&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max"
            "&temperature_unit=fahrenheit"
            "&timezone=America%2FChicago"
            "&forecast_days=1"
        )
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status != 200:
                        return None
                    data = await resp.json()
        except Exception:
            return None

        daily = data.get("daily", {})
        if not daily or not daily.get("time"):
            return None

        return {
            "high":     daily["temperature_2m_max"][0],
            "low":      daily["temperature_2m_min"][0],
            "rain_pct": daily["precipitation_probability_max"][0],
            "date":     daily["time"][0],
        }

    async def build_embed(self):
        """Build the forecast embed. Returns None if not configured or API fails."""
        cfg = self.bot.config
        lat  = cfg.get("weather_lat")
        lon  = cfg.get("weather_lon")
        city = cfg.get("weather_city", "Unknown Location")

        if lat is None or lon is None:
            return None

        forecast = await self.get_forecast(lat, lon)
        if forecast is None:
            return None

        rain = forecast["rain_pct"]
        if rain >= 70:
            rain_emoji = "🌧️"
        elif rain >= 40:
            rain_emoji = "🌦️"
        elif rain >= 20:
            rain_emoji = "⛅"
        else:
            rain_emoji = "☀️"

        dt       = datetime.strptime(forecast["date"], "%Y-%m-%d")
        date_str = dt.strftime("%A, %B ") + str(dt.day)  # avoids %-d (Linux-only)

        embed = discord.Embed(
            title=f"🌤️ Weather Forecast — {city}",
            description=date_str,
            color=0x87CEEB,
            timestamp=datetime.now(CENTRAL),
        )
        embed.add_field(name="🌡️ High",              value=f"{forecast['high']:.0f}°F",  inline=True)
        embed.add_field(name="🌡️ Low",               value=f"{forecast['low']:.0f}°F",   inline=True)
        embed.add_field(name=f"{rain_emoji} Rain Chance", value=f"{rain}%",              inline=True)
        embed.set_footer(text="Powered by Open-Meteo • open-meteo.com")

        return embed

    # ------------------------------------------------------------------
    # !weather command
    # ------------------------------------------------------------------

    @commands.command()
    async def weather(self, ctx):
        """Show today's weather forecast."""
        cfg = self.bot.config
        if cfg.get("weather_lat") is None:
            await ctx.send(
                "❌ Weather location isn't set yet. "
                "Ask an admin to run `!setweathercity <city name>`."
            )
            return

        async with ctx.typing():
            embed = await self.build_embed()

        if embed is None:
            await ctx.send("⚠️ Couldn't fetch the forecast right now. Try again in a moment.")
            return

        await ctx.send(embed=embed)

    # ------------------------------------------------------------------
    # Daily 6 am task
    # ------------------------------------------------------------------

    @tasks.loop(hours=24)
    async def daily_weather(self):
        cfg = self.bot.config
        channel_id = cfg.get("weather_channel")
        if channel_id is None:
            return

        channel = self.bot.get_channel(channel_id)
        if channel is None:
            return

        embed = await self.build_embed()
        if embed:
            await channel.send(embed=embed)

    @daily_weather.before_loop
    async def before_daily_weather(self):
        await self.bot.wait_until_ready()

        # Sleep until the next 6:00 am Central
        now    = datetime.now(CENTRAL)
        target = now.replace(hour=6, minute=0, second=0, microsecond=0)
        if target <= now:
            target += timedelta(days=1)

        await asyncio.sleep((target - now).total_seconds())


async def setup(bot):
    await bot.add_cog(Weather(bot))
