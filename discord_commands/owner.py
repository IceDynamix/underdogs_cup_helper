from time import time

from discord.ext import commands
from settings_manager import settings_manager
import tetrio


class owner(commands.Cog):

    def __init__(self, bot: commands.Bot, settings: settings_manager):
        self.bot = bot
        self.settings = settings

    async def cog_check(self, ctx: commands.Context):
        return commands.is_owner()

    @commands.command(hidden=True)
    async def echo(self, ctx: commands.Context, arg: str):
        await ctx.send(arg)

    @commands.command(hidden=True)
    async def toggle(self, ctx: commands.Context):
        role = ctx.guild.get_role(settings_manager.discord.role)
        if role not in ctx.author.roles:
            await ctx.author.add_roles(role)
            await ctx.send("added role")
        else:
            await ctx.author.remove_roles(role)
            await ctx.send("removed role")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def update_cache(self, ctx: commands.Context):
        start = time()
        date = tetrio.retrieve_data("players", False)["date"]
        end = time()
        await ctx.send(
            "Updated cache, " +
            "took {:.2f} seconds, ".format(end - start) +
            "last data from {}".format(date))
