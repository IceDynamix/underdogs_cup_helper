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
    rank_cap: str

    @classmethod
    def from_profile(cls, profile_name: str):
        with open(cls.path, 'r') as s:
            profiles = json.load(s)

        profile = profiles[profile_name]
        new_settings = settings(
            discord_channel=profile["discord_channel"],
            discord_participant_role=profile["discord_participant_role"],
            discord_staff_role=profile["discord_staff_role"],
            spreadsheet_id=profile["spreadsheet_id"],
            spreadsheet_registration_range=profile["spreadsheet_registration_range"],
            rank_cap=profile["rank_cap"]
        )

        print("Using profile " + profile_name)
        print(new_settings)

        return new_settings
