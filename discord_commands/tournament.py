from datetime import datetime

from discord.ext import commands, tasks
from player_list import player_list
from settings_manager import settings
from tetrio import retrieve_data, tetrio_user
import tetrio


class tournament(commands.Cog):
    def __init__(self, bot: commands.Bot, settings: settings):
        self.bot = bot
        self.settings = settings
        self.initial_update = False
        self.player_list = player_list(settings=self.settings, bot=self.bot)
        self.update_stats.start()

    @tasks.loop(hours=6)
    async def update_stats(self):
        if not self.initial_update:  # Don't run the first time
            self.initial_update = True
            return
        tetrio.current_playerbase_data = retrieve_data("players")
        tetrio.current_player_history_data = retrieve_data(
            "player_history")
        self.player_list = player_list(settings=self.settings, bot=self.bot)

    @update_stats.before_loop
    async def before_update_stats(self):
        await self.bot.wait_until_ready()

    @update_stats.after_loop
    async def on_update_cancel(self):
        if self.update_stats.is_being_cancelled():
            print(f"Could not update stats ({datetime.utcnow()})")

    @commands.command(help="Registers you to the ongoing tournament")
    async def register(self, ctx: commands.Context, username: str = None):
        role = ctx.guild.get_role(self.settings.discord_participant_role)

        if not username:
            username = ctx.author.display_name
        username = username.lower()

        if role in ctx.author.roles or \
                self.player_list.is_discord_registered(ctx.author.id):
            await ctx.send("Discord user already registered")
            return
        elif self.player_list.is_username_registered(username):
            await ctx.send("Tetr.io username already registered")
            return

        player_data = tetrio_user.from_username(username)

        if player_data.current_stats:
            await ctx.send(embed=player_data.current_stats.generate_embed())
        else:
            await ctx.send(f"Could not find user with username {username}")
            return

        can_participate, message = player_data.can_participate(
            self.settings, True)
        if not can_participate:
            await ctx.send(message)
            return

        # it's going to fail if you edit the owner
        if ctx.author.display_name != username and not commands.is_owner():
            await ctx.author.edit(nick=username)

        self.player_list.add(ctx.author.id, str(ctx.author), player_data)
        self.player_list.update_spreadsheet()

        await ctx.author.add_roles(role)
        await ctx.send(
            f"Registered Discord user {ctx.author} as player {username}"
        )

    @commands.command(help="Unregister from the tournament if necessary")
    async def unregister(self, ctx: commands.Context):
        role = ctx.guild.get_role(self.settings.discord_participant_role)

        if role not in ctx.author.roles:
            await ctx.send("Not registered")
            return

        self.player_list.remove(ctx.author.id)
        self.player_list.update_spreadsheet()
        await ctx.author.remove_roles(role)
        await ctx.send(f"Unregistered Discord user {ctx.author}")

    @commands.command(
        name="caniparticipate",
        help="Unsure about whether you can participate?",
    )
    async def can_i_participate(self, ctx: commands.Context,
                                username: str = None) -> bool:
        if not username:
            username = ctx.author.display_name
        username = username.lower()

        user = tetrio_user.from_username(username)
        if not user:
            ctx.send(f"Could not find user with username {username}")

        response = tetrio_user.from_username(
            username).can_participate(self.settings, True)
        await ctx.send(response)

    @commands.command(hidden=True)
    async def player_list(self, ctx: commands.Context):
        msg = str(self.player_list)
        if msg:
            await ctx.send(msg)
        else:
            await ctx.send("No players")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def update(self, ctx: commands.Context):
        if self.update_stats.is_running():
            await ctx.send("Already updating")
        else:
            self.update_stats.start()
