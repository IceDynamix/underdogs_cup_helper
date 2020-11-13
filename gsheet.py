from __future__ import print_function

import os.path
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


class spreadsheet:
    def __init__(self):
        self.service = build(
            "sheets", "v4", credentials=self.__credentials()
        ).spreadsheets()

    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    spreadsheet_id = "12ofvIJ0BI80Qz_GgU35nPlbsm4MVuOzxIx1D8l5iCnM"
    sheet_name = "regs"

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
        sheet_range = f"{self.sheet_name}!{a1notation}"
        result = self.service.values().get(
            spreadsheetId=self.spreadsheet_id,
            range=sheet_range
        ).execute()

        return result.get("values", [])

    def write_range(self, a1notation: str, values: list) -> None:
        sheet_range = f"{self.sheet_name}!{a1notation}"
        self.service.values().update(
            spreadsheetId=self.spreadsheet_id,
            range=sheet_range,
            valueInputOption="USER_ENTERED",
            body={"values": values}
        ).execute()

    def clear_range(self, a1notation) -> None:
        sheet_range = f"{self.sheet_name}!{a1notation}"
        self.service.values().clear(
            spreadsheetId=self.spreadsheet_id,
            range=sheet_range
        ).execute()
