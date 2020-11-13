from dataclasses import dataclass
from datetime import datetime

from gsheet import spreadsheet


@dataclass
class player():
    date_format = "%Y-%m-%d %H:%M"

    discord_id: int
    discord_tag: str
    username: str
    reg_timestamp: datetime = datetime.utcnow()

    @classmethod
    def from_row(self, row: list):
        return player(
            reg_timestamp=datetime.strptime(row[0], self.date_format),
            discord_id=int(row[1]),
            discord_tag=row[2],
            username=row[3]
        )

    def to_row(self):
        return [
            self.reg_timestamp.strftime(self.date_format),
            self.discord_id,
            self.discord_tag,
            self.username
        ]


class player_list():
    sheet_range = "A2:D"

    def __init__(self):
        self.spreadsheet = spreadsheet()
        self.read_spreadsheet()

    def read_spreadsheet(self):
        rows = self.spreadsheet.read_range(self.sheet_range)
        self.player_list = [
            player.from_row(row) for row in rows
        ]

    def update_spreadsheet(self):
        self.spreadsheet.clear_range(self.sheet_range)
        self.spreadsheet.write_range(
            self.sheet_range,
            [p.to_row() for p in self.player_list]
        )

    def add(self, discord_id: int,
            discord_tag: str, username: str):
        timestamp = datetime.utcnow().strftime(self.date_format)
        self.player_list.append(
            player(timestamp, discord_id, discord_tag, username.lower())
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
            if p.username.lower() == username
        ]) > 0

    def remove(self, discord_id: int) -> None:
        self.player_list = [
            p for p in self.player_list
            if p.discord_id != discord_id
        ]
