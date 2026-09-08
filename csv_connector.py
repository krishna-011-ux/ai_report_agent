"""CSV Connector - CSV files se data padhta hai."""

import pandas as pd
from connectors.base_connector import BaseConnector


class CSVConnector(BaseConnector):
    def fetch(self) -> pd.DataFrame:
        path = self.config["csv"]["path"]
        print(f"[CSVConnector] Reading data from: {path}")
        df = pd.read_csv(path)
        return self.validate(df)
