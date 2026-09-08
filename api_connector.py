"""
API Connector
-------------
Fetches JSON data from a REST API and converts it into a Pandas DataFrame.

For nested JSON responses, a 'json_path' can be specified in the configuration.
For example, use "data.records" if the API response has a structure like:
{"data": {"records": [...]}}
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

        response = requests.request(
            method,
            url,
            headers=headers,
            params=params,
            timeout=30
        )

        response.raise_for_status()
        data = response.json()

        # Follow the configured JSON path for nested API responses.
        if json_path:
            for key in json_path.split("."):
                data = data[key]

        df = pd.json_normalize(data)
        return self.validate(df)
