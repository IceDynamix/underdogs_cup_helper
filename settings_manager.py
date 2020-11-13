import json
from dataclasses import dataclass


@dataclass
class discord_settings():
    channel: int
    role: int

    def __init__(self, settings: dict):
        self.channel = settings["discord"]["channel"]
        self.role = settings["discord"]["role"]


@dataclass
class spreadsheet_settings():
    spreadsheet_id: str
    registration_range: str

    def __init__(self, settings: dict):
        self.spreadsheet_id = settings["spreadsheet"]["spreadsheet_id"]
        self.registration_range = settings["spreadsheet"]["registration_range"]


class settings_manager():
    path = "settings.json"

    def __init__(self, profile: str):
        with open(self.path, 'r') as s:
            settings = json.load(s)[profile]
        self.discord = discord_settings(settings)
        self.spreadsheet = spreadsheet_settings(settings)
        print("Using profile " + profile)
        print(self.discord)
        print(self.spreadsheet)
