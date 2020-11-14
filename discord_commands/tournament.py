from discord.ext import commands
from player_list import player_list
from settings_manager import settings_manager
from tetrio import tetrio_user


class tournament(commands.Cog):
    def __init__(self, bot: commands.Bot,
                 settings: settings_manager, players: player_list):
        self.bot = bot
        self.settings = settings
        self.player_list = players

    @commands.command(help="Registers you to the ongoing tournament")
    async def register(self, ctx: commands.Context, username: str = None):
        role = ctx.guild.get_role(self.settings.discord.participant_role)

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

        if player_data:
            await ctx.send(embed=player_data.current_stats.generate_embed())
        else:
            await ctx.send("Username not found")
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
        role = ctx.guild.get_role(self.settings.discord.participant_role)

        if role not in ctx.author.roles:
            await ctx.send("Not registered")
            return

        self.player_list.remove(ctx.author.id)
        self.player_list.update_spreadsheet()
        await ctx.author.remove_roles(role)
        await ctx.send(f"Unregistered Discord user {ctx.author}")

    @commands.command(hidden=True)
    async def player_list(self, ctx: commands.Context):
        msg = str(self.player_list)
        if msg:
            await ctx.send(msg)
        else:
            await ctx.send("No players")
