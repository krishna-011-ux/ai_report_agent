"""
Google Sheets Connector
-----------------------
Reads live data from Google Sheets using the gspread library.

Setup (one-time configuration):
1. Create a Service Account in Google Cloud Console.
2. Enable the Google Sheets API and Google Drive API.
3. Download the Service Account JSON key and save it as
   config/gcreds.json.
4. Share your Google Sheet with the Service Account email address
   with Viewer access.
5. Add the sheet_id to config.yaml. You can find the SHEET_ID in
   the Google Sheets URL:
   docs.google.com/spreadsheets/d/<SHEET_ID>/edit
"""

import pandas as pd
from connectors.base_connector import BaseConnector


class GSheetConnector(BaseConnector):
    def fetch(self) -> pd.DataFrame:
        import gspread
        from google.oauth2.service_account import Credentials

        cfg = self.config["gsheet"]

        scopes = [
            "https://www.googleapis.com/auth/spreadsheets.readonly",
            "https://www.googleapis.com/auth/drive.readonly"
        ]

        creds = Credentials.from_service_account_file(
            cfg["credentials_file"],
            scopes=scopes
        )

        client = gspread.authorize(creds)

        print(
            f"[GSheetConnector] Opening spreadsheet: "
            f"{cfg['sheet_id']}"
        )

        sheet = client.open_by_key(
            cfg["sheet_id"]
        )

        worksheet = sheet.worksheet(
            cfg.get("worksheet_name", "Sheet1")
        )

        records = worksheet.get_all_records()

        df = pd.DataFrame(records)

        return self.validate(df)
