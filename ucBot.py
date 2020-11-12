import discord
from discord.ext import commands

ucBot = commands.Bot(command_prefix="!")


@ucBot.event
async def on_ready():
    print("ucBot online")
    await ucBot.change_presence(
        status=discord.Status.online,
        activity=discord.Activity("Registrations open!")
    )


@ucBot.command()
async def echo(ctx: commands.Context, arg: str):
    await ctx.send(arg)


@ucBot.command()
async def toggle(ctx: commands.Context):
    role = ctx.guild.get_role(228485722284228608)
    if role not in ctx.author.roles:
        await ctx.author.add_roles(role)
        await ctx.send("added role")
    else:
        await ctx.author.remove_roles(role)
        await ctx.send("removed role")
