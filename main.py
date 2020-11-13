import discord
from discord.ext import commands

from player_list import player_list
from tetrio import retrieve_data

BOT_CHANNEL = 477999746070347787
PARTICIPANT_ROLE = 228485722284228608

ucBot = commands.Bot(command_prefix="!")
player_list = player_list()


@ucBot.check
async def only_in_bot_channel(ctx: commands.Context):
    return ctx.channel.id == BOT_CHANNEL


@ucBot.check
async def no_dms(ctx: commands.Context):
    return ctx.guild is not None


@ucBot.event
async def on_ready():
    print("ucBot online")
    await ucBot.change_presence(
        status=discord.Status.online,
        activity=discord.CustomActivity("Registrations are open!")
    )


@ucBot.command()
@commands.is_owner()
async def echo(ctx: commands.Context, arg: str):
    await ctx.send(arg)


@ucBot.command()
@commands.is_owner()
async def toggle(ctx: commands.Context):
    role = ctx.guild.get_role(PARTICIPANT_ROLE)
    if role not in ctx.author.roles:
        await ctx.author.add_roles(role)
        await ctx.send("added role")
    else:
        await ctx.author.remove_roles(role)
        await ctx.send("removed role")


@ucBot.command()
async def register(ctx: commands.Context, username: str = None):
    role = ctx.guild.get_role(PARTICIPANT_ROLE)

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

    playerbase_data = retrieve_data("players")

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

    await ctx.author.add_roles(ctx.guild.get_role(PARTICIPANT_ROLE))

    # TODO Add to player list


@ucBot.command()
async def unregister(ctx: commands.Context):
    role = ctx.guild.get_role(PARTICIPANT_ROLE)

    if role not in ctx.author.roles:
        await ctx.send("Not registered")
        return

    await ctx.author.remove_roles(role)
    await ctx.send("Unregistered player")

    # TODO Remove from player list

if __name__ == "__main__":
    with open("./credentials/token.secret") as tokenFile:
        token = tokenFile.read()
    ucBot.run(token)
