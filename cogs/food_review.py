import asyncio
import os
import time
import discord
from discord.ext import commands
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def track_usage(bot, response):
    usage = bot.config.setdefault("usage", {"prompt_tokens": 0, "completion_tokens": 0})
    usage["prompt_tokens"] += response.usage.prompt_tokens
    usage["completion_tokens"] += response.usage.completion_tokens
    bot.save_config()

class FoodReview(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.cooldowns = {}
        self.off_topic_streak = 0
        self.off_topic_messages = []

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if message.channel.id != self.bot.config.get("food_channel"):
            return

        has_food_image = any(
            a.content_type and "image" in a.content_type
            for a in message.attachments
        )

        if not has_food_image:
            self.off_topic_streak += 1
            if message.content:
                self.off_topic_messages.append(f"{message.author.display_name}: {message.content}")
            if self.off_topic_streak >= 4:
                self.off_topic_streak = 0
                context = "\n".join(self.off_topic_messages)
                self.off_topic_messages = []
                async with message.channel.typing():
                    try:
                        response = await asyncio.to_thread(
                            self.ai.chat.completions.create,
                            model="gpt-4o-mini",
                            messages=[
                                {
                                    "role": "system",
                                    "content": (
                                        "You are a witty food-obsessed bot moderating a food-only Discord channel. "
                                        "People are going off-topic. Write one short, clever message (max 2 sentences) "
                                        "referencing what they were actually talking about, then redirect them back to food. "
                                        "Be funny but not mean. No emojis."
                                    )
                                },
                                {
                                    "role": "user",
                                    "content": f"These are the off-topic messages:\n{context}"
                                }
                            ]
                        )
                        track_usage(self.bot, response)
                        reply = response.choices[0].message.content
                    except Exception:
                        reply = "This channel is for food posts only. Please keep the chat on topic."
                await message.channel.send(reply)
            return

        self.off_topic_streak = 0
        self.off_topic_messages = []

        attachment = message.attachments[0]

        user_id = message.author.id
        now = time.time()

        if user_id in self.cooldowns:
            if now - self.cooldowns[user_id] < 5:
                return

        self.cooldowns[user_id] = now

        image_url = attachment.url

        async with message.channel.typing():
            try:
                response = await asyncio.to_thread(
                    self.ai.chat.completions.create,
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a funny, laid-back food critic in a Discord server.\n"
                                "You speak casually and conversationally, inspired by Anthony Bourdain but NOT harsh.\n"
                                "You are honest, but never rude or insulting.\n"
                                "Criticism should be light, playful, and constructive—not mean.\n\n"

                                "You prefer home cooking and give slightly higher ratings to homemade meals.\n"
                                "Snacks are welcome and should be rated appropriately for snacks.\n"
                                "Do not compare snacks to full meals.\n\n"

                                "Try to identify which restaurant the food is from and mention it if possible.\n\n"

                                "If the image is not food, say 'Not food lil bro' and give 0/10.\n"
                                "If the meal is less than or equal to 2/10, say 'dawg wth is that??? 😭😭'.\n"

                                "Format EXACTLY like:\n"
                                "Description. X/10\n\n"
                                "End with ONE single word on a new line describing the meal.\n"
                                "Do NOT include any label.\n\n"

                                "Keep it under 50 words."
                            )
                        },
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": f"Analyze this meal.{f' The user says: {message.content}' if message.content else ''}"},
                                {"type": "image_url", "image_url": {"url": image_url}}
                            ]
                        }
                    ]
                )

                track_usage(self.bot, response)

                reply = response.choices[0].message.content

                if len(reply) > 2000:
                    reply = reply[:1990] + "..."

                await message.reply(reply, mention_author=False)

            except Exception as e:
                print(e)
                await message.channel.send("Error analyzing meal.")

async def setup(bot):
    await bot.add_cog(FoodReview(bot))
