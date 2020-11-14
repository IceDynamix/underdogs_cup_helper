from dataclasses import dataclass
from datetime import datetime

from discord.ext import commands

from gsheet import spreadsheet
from settings_manager import settings
from tetrio import tetrio_user


@dataclass
class player():
    date_format = "%Y-%m-%d %H:%M"

    reg_timestamp: datetime
    discord_id: int
    discord_tag: str
    tetrio: tetrio_user

    @staticmethod
    def from_row(row: list, bot: commands.Bot):
        discord_id = int(row[1])
        discord_tag = row[2]
        username = row[3]

        return player(
            reg_timestamp=datetime.strptime(row[0], player.date_format),
            discord_id=discord_id,
            discord_tag=discord_tag,
            tetrio=tetrio_user.from_username(username)
        )

    def to_row(self):
        if type(self.reg_timestamp) == datetime:
            timestamp = self.reg_timestamp.strftime(self.date_format)
        else:
            timestamp = self.reg_timestamp
        return [
            timestamp,
            # gsheets will reduce the number to e notation if passed as int
            str(self.discord_id),
            self.discord_tag,
        ] + self.tetrio.to_row()

    def __str__(self) -> str:
        return f"{self.discord_tag}: {self.tetrio.username}"


class player_list():
    def __init__(self, bot: commands.Bot):
        self.spreadsheet = spreadsheet()
        self.bot = bot
        self.read_spreadsheet()

    def read_spreadsheet(self):
        rows = self.spreadsheet.read_range(
            settings.spreadsheet_registration_range)
        self.player_list = [
            player.from_row(row, self.bot)
            for row in rows if len(row) == 14
        ]

    def update_spreadsheet(self):
        reg_range = settings.spreadsheet_registration_range
        # only clear once data has been processed, otherwise it might
        # wipe all registrations
        data = [p.to_row() for p in self.player_list]
        self.spreadsheet.clear_range(reg_range)
        self.spreadsheet.write_range(reg_range, data)

    def add(self, discord_id: int, discord_tag: str, tetrio: tetrio_user):
        timestamp = datetime.utcnow().strftime(player.date_format)
        self.player_list.append(
            player(
                reg_timestamp=timestamp,
                discord_id=discord_id,
                discord_tag=discord_tag,
                tetrio=tetrio
            )
        )

        return True

    def is_discord_registered(self, discord_id: int) -> bool:
        return len([
            p for p in self.player_list
            if p.discord_id == discord_id
        ]) > 0

    def is_username_registered(self, username: str):
        return len([
            p for p in self.player_list
            if p.tetrio.username == username.lower()
        ]) > 0

    def remove(self, discord_id: int) -> None:
        self.player_list = [
            p for p in self.player_list
            if p.discord_id != discord_id
        ]

    def __str__(self) -> str:
        return "\n".join([str(p) for p in self.player_list])
