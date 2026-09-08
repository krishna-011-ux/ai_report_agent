"""
Excel Connector - Reads data from .xlsx and .xls files.
"""

import pandas as pd
from connectors.base_connector import BaseConnector


class ExcelConnector(BaseConnector):
    def fetch(self) -> pd.DataFrame:
        cfg = self.config["excel"]
        path = cfg["path"]
        sheet = cfg.get("sheet_name", 0)

        print(
            f"[ExcelConnector] Reading data from: "
            f"{path} (sheet={sheet})"
        )

        df = pd.read_excel(
            path,
            sheet_name=sheet
        )

        return self.validate(df)
