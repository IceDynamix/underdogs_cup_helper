import json
from dataclasses import dataclass


@dataclass
class settings():
    path = "settings.json"

    discord_channel: int
    discord_participant_role: int
    discord_staff_role: int
    spreadsheet_id: str
    spreadsheet_registration_range: str

    @classmethod
    def from_profile(cls, profile: str):
        with open(cls.path, 'r') as s:
            settings = json.load(s)[profile]

        settings = settings(
            discord_channel=settings["discord_channel"],
            discord_participant_role=settings["discord_participant_role"],
            discord_staff_role=settings["discord_staff_role"],
            spreadsheet_id=settings["spreadsheet_id"],
            spreadsheet_registration_range=settings["spreadsheet_registration_range"]
        )

        print("Using profile " + profile)
        print(settings)

        return settings
