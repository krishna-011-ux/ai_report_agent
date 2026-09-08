"""
Google Sheets Connector
-----------------------
Google Sheets se live data padhta hai gspread library ke through.

Setup (ek baar karna hai):
1. Google Cloud Console mein ek Service Account banao
2. Google Sheets API + Google Drive API enable karo
3. Service account ki JSON key download karo -> config/gcreds.json mein rakho
4. Apni Google Sheet ko us service account ke email ke saath "Share" karo (Viewer access)
5. config.yaml mein sheet_id daalo (URL se: docs.google.com/spreadsheets/d/<SHEET_ID>/edit)
"""

import pandas as pd
from connectors.base_connector import BaseConnector


class GSheetConnector(BaseConnector):
    def fetch(self) -> pd.DataFrame:
        import gspread
        from google.oauth2.service_account import Credentials

        cfg = self.config["gsheet"]
        scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly",
                  "https://www.googleapis.com/auth/drive.readonly"]

        creds = Credentials.from_service_account_file(cfg["credentials_file"], scopes=scopes)
        client = gspread.authorize(creds)

        print(f"[GSheetConnector] Opening sheet: {cfg['sheet_id']}")
        sheet = client.open_by_key(cfg["sheet_id"])
        worksheet = sheet.worksheet(cfg.get("worksheet_name", "Sheet1"))

        records = worksheet.get_all_records()
        df = pd.DataFrame(records)
        return self.validate(df)
