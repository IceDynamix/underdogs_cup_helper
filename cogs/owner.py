from time import time

import discord
import tetrio
from discord.ext import commands
from settings_manager import settings, settings_manager


class owner(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_check(self, ctx: commands.Context):
        return await self.bot.is_owner(ctx.author)

    @commands.command(hidden=True)
    async def echo(self, ctx: commands.Context, arg: str):
        await ctx.send(arg)

    @commands.command(hidden=True)
    async def toggle(self, ctx: commands.Context):
        role = ctx.guild.get_role(settings.discord.role)
        if role not in ctx.author.roles:
            await ctx.author.add_roles(role)
            await ctx.send("added role")
        else:
            await ctx.author.remove_roles(role)
            await ctx.send("removed role")

    @commands.command(hidden=True)
    async def update_cache(self, ctx: commands.Context):
        start = time()
        date = tetrio.retrieve_data("players", False)["date"]
        end = time()
        await ctx.send(
            "Updated cache, " +
            "took {:.2f} seconds, ".format(end - start) +
            "last data from {}".format(date))

    @commands.command(hidden=True)
    async def setup_check_in(self, ctx: commands.Context):
        embed = discord.Embed(
            title="Check-in",
            description="Please react to this message with the " +
            "green checkmark to check in!"
        )
        check_in_message = await ctx.send(embed=embed)
        await check_in_message.add_reaction("✅")
        print(f"Created check-in message <{check_in_message.id}>")

    @commands.command(name="load", hidden=True)
    async def load_cog(self, ctx, cog: str):
        self.bot.load_extension(cog)
        await ctx.send("Loaded cog successfully")

    @commands.command(name="unload", hidden=True)
    async def unload_cog(self, ctx, cog: str):
        self.bot.unload_extension(cog)
        await ctx.send("Unloaded cog successfully")

    @commands.command(name="reload", hidden=True)
    async def reload_cog(self, ctx, cog: str):
        self.bot.unload_extension(cog)
        self.bot.load_extension(cog)
        await ctx.send("Reloaded cog successfully")

    @commands.command(name="settings", hidden=True)
    async def reload_settings(self, ctx, profile: str):
        settings_manager.settings = settings.from_profile(profile)
        await ctx.send(
            f"Reloaded settings from profile {profile} successfully")


def setup(bot: commands.Bot):
    bot.add_cog(owner(bot))
