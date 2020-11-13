from discord.ext import commands
from settings_manager import settings_manager
import tetrio
from player_list import player_list


class tournament(commands.Cog):
    def __init__(self, bot: commands.Bot,
                 settings: settings_manager, player_list: player_list):
        self.bot = bot
        self.settings = settings
        self.player_list = player_list

    @commands.command(help="Registers you to the ongoing tournament")
    async def register(self, ctx: commands.Context, username: str = None):
        role = ctx.guild.get_role(self.settings.discord.role)

        if not username:
            username = ctx.author.display_name
        username = username.lower()

        print(ctx.author.id)

        if role in ctx.author.roles or \
                self.player_list.is_discord_registered(ctx.author.id):
            await ctx.send("Discord user already registered")
            return
        elif self.player_list.is_username_registered(username):
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

        self.player_list.add(ctx.author.id, ctx.author.name, username)
        self.player_list.update_spreadsheet()

        await ctx.author.add_roles(role)
        await ctx.send(
            "Registered Discord user " +
            f"{ctx.author.name}#{ctx.author.discriminator} " +
            f"as player {username}"
        )

    @commands.command(help="Unregister from the tournament if necessary")
    async def unregister(self, ctx: commands.Context):
        role = ctx.guild.get_role(self.settings.discord.role)

        if role not in ctx.author.roles:
            await ctx.send("Not registered")
            return

        self.player_list.remove(ctx.author.id)
        self.player_list.update_spreadsheet()
        await ctx.author.remove_roles(role)
        await ctx.send(
            "Unregistered Discord user " +
            f"{ctx.author.name}#{ctx.author.discriminator}"
        )
