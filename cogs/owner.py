from gsheet import spreadsheet
from time import time

import discord
import tetrio
from discord.ext import commands, tasks
from settings_manager import settings, settings_manager


class owner(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.update_checkins.start()

    @tasks.loop(minutes=2)
    async def update_checkins(self):
        print("Starting checkin update")
        # TODO Extract constants to settings
        channel = self.bot.get_guild(
            718603683624910941).get_channel(777355668955856916)
        message = await channel.fetch_message(780016256823984159)
        users = [
            [str(u.id)]
            for u in await message.reactions[0].users().flatten()
        ]
        print(f"Read {len(users)} reactions")
        sheet = spreadsheet()
        sheet_range = "checkin!A1:A"
        sheet.clear_range(sheet_range)
        spreadsheet().write_range(sheet_range, users)
        print("Wrote users to spreadsheet")

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
    async def load_cog(self, ctx: commands.Context, cog: str):
        self.bot.load_extension(cog)
        await ctx.send("Loaded cog successfully")

    @commands.command(name="unload", hidden=True)
    async def unload_cog(self, ctx: commands.Context, cog: str):
        self.bot.unload_extension(cog)
        await ctx.send("Unloaded cog successfully")

    @commands.command(name="reload", hidden=True)
    async def reload_cog(self, ctx: commands.Context, cog: str):
        self.bot.unload_extension(cog)
        self.bot.load_extension(cog)
        await ctx.send("Reloaded cog successfully")

    @commands.command(name="settings", hidden=True)
    async def reload_settings(self, ctx: commands.Context, profile: str):
        settings_manager.settings = settings.from_profile(profile)
        await ctx.send(
            f"Reloaded settings from profile {profile} successfully")

    @commands.command(hidden=True)
    async def force_update_checkins(self, ctx: commands.Context):
        if self.update_checkins.is_running():
            await ctx.send("Already running")
        else:
            self.update_checkins.start()


def setup(bot: commands.Bot):
    bot.add_cog(owner(bot))
