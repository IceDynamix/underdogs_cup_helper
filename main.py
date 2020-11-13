import discord
from tetrio import retrieve_data
from discord.ext import commands

BOT_CHANNEL = 477999746070347787
PARTICIPANT_ROLE = 228485722284228608

ucBot = commands.Bot(command_prefix="!")


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

    if role in ctx.author.roles:
        await ctx.send("Already registered")
        return

    if not username:
        username = ctx.author.display_name
    username = username.lower()

    playerbase_data = retrieve_data("players")

    # check if valid

    if username not in playerbase_data["latest_stats"]:
        if username in playerbase_data["unranked_stats"]:
            await ctx.send("Unranked on announcement date, you cannot participate")
            return
        await ctx.send("Username not found")
        return

    user_data = playerbase_data["latest_stats"][username]

    await ctx.send(
        f"User {username} found, rank: {user_data['rank'].upper()}"
    )

    # change discord nick to ign

    if ctx.author.display_name != username and not commands.is_owner():
        await ctx.author.edit(nick=username)

    # give participants role

    await ctx.author.add_roles(ctx.guild.get_role(PARTICIPANT_ROLE))


if __name__ == "__main__":
    with open("./credentials/token.secret") as tokenFile:
        token = tokenFile.read()
    ucBot.run(token)
