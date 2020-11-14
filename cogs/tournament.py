from datetime import datetime

import tetrio
from discord.ext import commands, tasks
from player_list import player_list
from settings_manager import settings
from tetrio import retrieve_data, tetrio_user


class tournament(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.initial_update = False
        self.player_list = player_list(bot=self.bot)
        self.update_stats.start()

    @tasks.loop(hours=6)
    async def update_stats(self):
        if not self.initial_update:  # Don't run the first time
            self.initial_update = True
            return
        tetrio.current_playerbase_data = retrieve_data("players")
        tetrio.current_player_history_data = retrieve_data(
            "player_history")
        self.player_list = player_list(bot=self.bot)

    @update_stats.before_loop
    async def before_update_stats(self):
        await self.bot.wait_until_ready()

    @update_stats.after_loop
    async def on_update_cancel(self):
        if self.update_stats.is_being_cancelled():
            print(f"Could not update stats ({datetime.utcnow()})")

    async def cog_check(self, ctx: commands.Context):
        return ctx.channel.id == settings.participant_channel or \
            ctx.channel.id == settings.staff_channel

    @commands.command(help="Registers you to the ongoing tournament")
    async def register(self, ctx: commands.Context, username: str = None):
        role = ctx.guild.get_role(settings.participant_role)

        if not username:
            username = ctx.author.display_name

        if role in ctx.author.roles or \
                self.player_list.is_discord_registered(ctx.author.id):
            await ctx.send("Discord user already registered")
            return
        elif self.player_list.is_username_registered(username):
            await ctx.send(
                "Tetr.io username already registered, please contact staff " +
                "if you truly are the owner of the Tetr.io account")
            return

        player_data = tetrio_user.from_username(username)

        if player_data.current_stats:
            await ctx.send(embed=player_data.current_stats.generate_embed())
        else:
            await ctx.send(f"Could not find user with username {username}")
            return

        can_participate, message = player_data.can_participate(True)
        if not can_participate:
            await ctx.send(message)
            return

        # it's going to fail if you edit the owner
        try:
            await ctx.author.edit(nick=username)
        except Exception:
            print(f"Can't change nickname of {ctx.author}")

        self.player_list.add(ctx.author.id, str(ctx.author), player_data)
        self.player_list.update_spreadsheet()

        await ctx.author.add_roles(role)
        await ctx.send(
            f"Registered Discord user {ctx.author} as player {username}"
        )

    @commands.command(
        help="Unregister from the tournament if necessary. Staff can " +
        "unregister players based on a Discord ID.")
    async def unregister(self, ctx: commands.Context, discord_id: str = None):
        staff_role = ctx.guild.get_role(settings.staff_role)

        if discord_id:
            # staff is removing the player
            if staff_role in ctx.author.roles:
                discord_id = int(discord_id)
                player_to_remove = await ctx.guild.fetch_member(discord_id)
                if not player_to_remove:
                    await ctx.send("User not on server")
                    return
            else:
                await ctx.send("Nice try, but I can't do that for you")
                return
        else:
            player_to_remove = ctx.author

        participant_role = ctx.guild.get_role(
            settings.participant_role)
        if participant_role not in player_to_remove.roles:
            await ctx.send("Not registered")
            return

        self.player_list.remove(player_to_remove.id)
        self.player_list.update_spreadsheet()
        await ctx.author.remove_roles(participant_role)
        await ctx.send(f"Unregistered Discord user {ctx.author}")

    @commands.command(
        help="Displays basic stats of a user, if no username is given " +
        "then it will attempt to look for your current UC Discord nickname")
    async def stats(self, ctx: commands.Context, username: str = None):
        if not username:
            username = ctx.author.display_name

        player = tetrio_user.from_username(username)
        if not player:
            await ctx.send(f"Could not find player `{username}`")
        else:
            await ctx.send(embed=player.current_stats.generate_embed())

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
            await ctx.send(f"Could not find user with username {username}")
        else:
            _, message = tetrio_user.from_username(
                username).can_participate(True)
            await ctx.send(message)

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


def setup(bot: commands.Bot):
    bot.add_cog(tournament(bot))
