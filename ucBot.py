import sys

import discord
from discord.ext import commands

import discord_commands.owner
import discord_commands.tournament
from player_list import player_list
from settings_manager import settings
from tetrio import tetrio_user

profile = sys.argv[1] if len(sys.argv) > 1 else "debug"
settings = settings.from_profile(profile)
ucBot = commands.Bot(command_prefix="!")
player_list = player_list(settings, ucBot)

ucBot.add_cog(discord_commands.owner.owner(
    bot=ucBot, settings=settings))
ucBot.add_cog(discord_commands.tournament.tournament(
    bot=ucBot, settings=settings, players=player_list))


@ucBot.check
async def only_in_bot_channel(ctx: commands.Context):
    return ctx.channel.id == settings.discord_channel


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


@ucBot.command(
    help="Displays basic stats of a user, if no username is given " +
    "then it will attempt to look for your current UC Discord nickname")
async def stats(ctx: commands.Context, username: str = None):
    if not username:
        username = ctx.author.display_name

    player = tetrio_user.from_username(username).current_stats
    if player:
        await ctx.send(embed=player.generate_embed())
    else:
        await ctx.send(f"Could not find player `{username}`")


if __name__ == "__main__":
    with open("./credentials/token.secret") as tokenFile:
        token = tokenFile.read()
    ucBot.run(token)
