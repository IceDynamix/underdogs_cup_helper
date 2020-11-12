import discord


class ucBot(discord.Client):
    async def on_ready(self):
        print("ucBot online")

    async def on_message(self, message):
        print("message received")
