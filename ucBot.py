#!env/bin/python3 
import sys

import discord
from discord.ext import commands

profile = sys.argv[1] if len(sys.argv) > 1 else "debug"
ucBot = commands.Bot(command_prefix="!")

extensions = [
    "cogs.owner",
    "cogs.tournament"
]


@ucBot.check
async def no_dms(ctx: commands.Context):
    return ctx.guild is not None


@ucBot.event
async def on_ready():
    print("Logged in as user " + str(ucBot.user))
    await ucBot.change_presence(
        status=discord.Status.online,
        activity=discord.CustomActivity("i like cheese")
    )


@ucBot.event
async def on_command(ctx: commands.Context):
    print(f"{ctx.author} <{ctx.author.id}>: {ctx.message.content}")


if __name__ == "__main__":
    for extension in extensions:
        ucBot.load_extension(extension)

    with open("./credentials/token.secret") as tokenFile:
        token = tokenFile.read()
    ucBot.run(token)
