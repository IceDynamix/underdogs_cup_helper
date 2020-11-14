from __future__ import print_function

import os.path
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from settings_manager import settings


class spreadsheet:
    def __init__(self, settings: settings):
        self.settings = settings
        self.service = build(
            "sheets", "v4", credentials=self.__credentials()
        ).spreadsheets()

    scopes = ["https://www.googleapis.com/auth/spreadsheets"]

    def __credentials(self):
        creds = None
        token_path = "./credentials/token.pickle"
        if os.path.exists(token_path):
            with open(token_path, "rb") as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", self.scopes)
                creds = flow.run_local_server(port=0)
            with open(token_path, "wb") as token:
                pickle.dump(creds, token)
        return creds

    def read_range(self, a1notation: str) -> list:
        result = self.service.values().get(
            spreadsheetId=self.settings.spreadsheet_id,
            range=a1notation
        ).execute()

        return result.get("values", [])

    def write_range(self, a1notation: str, values: list) -> None:
        self.service.values().update(
            spreadsheetId=self.settings.spreadsheet_id,
            range=a1notation,
            valueInputOption="USER_ENTERED",
            body={"values": values}
        ).execute()

    def clear_range(self, a1notation) -> None:
        self.service.values().clear(
            spreadsheetId=self.settings.spreadsheet_id,
            range=a1notation
        ).execute()
