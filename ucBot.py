import discord
from discord.ext import commands
import sys
import discord_commands.owner
import discord_commands.tournament

from player_list import player_list
import tetrio
from settings_manager import settings_manager


profile = sys.argv[1] if len(sys.argv) > 1 else "debug"
settings_manager = settings_manager(profile)
player_list = player_list(settings_manager)
ucBot = commands.Bot(command_prefix="!")

ucBot.add_cog(discord_commands.owner.owner(
    bot=ucBot, settings=settings_manager))
ucBot.add_cog(discord_commands.tournament.tournament(
    bot=ucBot, settings=settings_manager, player_list=player_list))


@ucBot.check
async def only_in_bot_channel(ctx: commands.Context):
    return ctx.channel.id == settings_manager.discord.channel


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


@ucBot.command(
    help="Displays basic stats of a user, if no username is given " +
    "then it will attempt to look for your current UC Discord nickname")
async def stats(ctx: commands.Context, username: str = None):
    if not username:
        username = ctx.author.display_name
    username = username.lower()

    embed = tetrio.generate_embed(username)
    if embed:
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"Could not find player `{username}`")


if __name__ == "__main__":
    with open("./credentials/token.secret") as tokenFile:
        token = tokenFile.read()
    ucBot.run(token)
