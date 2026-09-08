"""
API Connector - kisi bhi REST API se JSON data leke DataFrame banata hai.
Nested JSON ke liye 'json_path' config diya ja sakta hai
(e.g. "data.records" agar response {"data": {"records": [...]}} jaisa ho)
"""

import requests
import pandas as pd
from connectors.base_connector import BaseConnector


class APIConnector(BaseConnector):
    def fetch(self) -> pd.DataFrame:
        cfg = self.config["api"]
        url = cfg["url"]
        method = cfg.get("method", "GET").upper()
        headers = cfg.get("headers", {})
        params = cfg.get("params", {})
        json_path = cfg.get("json_path")

        print(f"[APIConnector] Calling {method} {url}")
        response = requests.request(method, url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        # Agar data nested hai to json_path follow karke andar jao
        if json_path:
            for key in json_path.split("."):
                data = data[key]

        df = pd.json_normalize(data)
        return self.validate(df)
