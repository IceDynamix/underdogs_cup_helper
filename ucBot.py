import discord
from discord.ext import commands
import sys

from player_list import player_list
import tetrio
from settings import settings
from time import time

profile = sys.argv[1] if len(sys.argv) > 1 else "debug"
settings = settings(profile)
ucBot = commands.Bot(command_prefix="!")
player_list = player_list(settings)


@ucBot.check
async def only_in_bot_channel(ctx: commands.Context):
    return ctx.channel.id == settings.discord.channel


@ucBot.check
async def no_dms(ctx: commands.Context):
    return ctx.guild is not None


@ucBot.event
async def on_ready():
    print("ucBot online")
    await ucBot.change_presence(
        status=discord.Status.online,
        activity=discord.CustomActivity("i like cheese")
    )


@ucBot.command(hidden=True)
@commands.is_owner()
async def echo(ctx: commands.Context, arg: str):
    await ctx.send(arg)


@ucBot.command(hidden=True)
@commands.is_owner()
async def toggle(ctx: commands.Context):
    role = ctx.guild.get_role(settings.discord.role)
    if role not in ctx.author.roles:
        await ctx.author.add_roles(role)
        await ctx.send("added role")
    else:
        await ctx.author.remove_roles(role)
        await ctx.send("removed role")


@ucBot.command(hidden=True)
@commands.is_owner()
async def update_cache(ctx: commands.Context):
    start = time()
    date = tetrio.retrieve_data("players", False)["date"]
    end = time()
    await ctx.send(
        "Updated cache, " +
        "took {:.2f} seconds, ".format(end - start) +
        "last data from {}".format(date))


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


@ucBot.command(help="Registers you to the ongoing tournament")
async def register(ctx: commands.Context, username: str = None):
    role = ctx.guild.get_role(settings.discord.role)

    if not username:
        username = ctx.author.display_name
    username = username.lower()

    if role in ctx.author.roles or \
            player_list.is_discord_registered(ctx.author.id):
        await ctx.send("Discord user already registered")
        return
    elif player_list.is_username_registered(username):
        await ctx.send("Tetr.io username already registered")
        return

    playerbase_data = tetrio.retrieve_data("players")

    # check if valid

    if username not in playerbase_data["latest_stats"]:
        if username in playerbase_data["unranked_stats"]:
            await ctx.send(
                f"Player {username} was unranked on announcement date, " +
                "which makes you ineligible to participate"
            )
            return
        await ctx.send(
            f"Username {username} not found, " +
            "please provide a valid username with `!register <username>`"
        )
        return

    user_data = playerbase_data["latest_stats"][username]

    await ctx.send(
        f"User {username} found, rank: {user_data['rank'].upper()}"
    )

    # it's going to fail if you edit the owner
    if ctx.author.display_name != username and not commands.is_owner():
        await ctx.author.edit(nick=username)

    player_list.add(ctx.author.id, ctx.author.name, username)
    player_list.update_spreadsheet()

    await ctx.author.add_roles(ctx.guild.get_role(settings.discord.role))
    await ctx.send(
        "Registered Discord user " +
        f"{ctx.author.name}#{ctx.author.discriminator} as player {username}"
    )


@ucBot.command(help="Unregister from the tournament if necessary")
async def unregister(ctx: commands.Context):
    role = ctx.guild.get_role(settings.discord.role)

    if role not in ctx.author.roles:
        await ctx.send("Not registered")
        return

    player_list.remove(ctx.author.id)
    player_list.update_spreadsheet()
    await ctx.author.remove_roles(role)
    await ctx.send(
        "Unregistered Discord user " +
        f"{ctx.author.name}#{ctx.author.discriminator}"
    )


if __name__ == "__main__":
    with open("./credentials/token.secret") as tokenFile:
        token = tokenFile.read()
    ucBot.run(token)
