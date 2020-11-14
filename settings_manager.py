import json
import sys
from dataclasses import dataclass


@dataclass
class settings_manager():
    path = "settings.json"

    participant_channel: int
    participant_role: int
    staff_channel: int
    staff_role: int
    spreadsheet_id: str
    spreadsheet_registration_range: str
    rank_cap: str

    @classmethod
    def from_profile(cls, profile_name: str):
        with open(cls.path, 'r') as s:
            profiles = json.load(s)

        profile = profiles[profile_name]
        new_settings = settings_manager(
            participant_channel=profile["participant_channel"],
            participant_role=profile["participant_role"],
            staff_channel=profile["staff_channel"],
            staff_role=profile["staff_role"],
            spreadsheet_id=profile["spreadsheet_id"],
            spreadsheet_registration_range=profile["spreadsheet_registration_range"],
            rank_cap=profile["rank_cap"]
        )

        print("Using profile " + profile_name)
        print(new_settings)

        return new_settings


settings = settings_manager.from_profile(
    sys.argv[1] if len(sys.argv) > 1 else "debug")
