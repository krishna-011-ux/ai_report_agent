"""
Base Connector
--------------
All data source connectors (CSV, Excel, SQL, API, and Google Sheets)
inherit from this abstract class.

This allows the pipeline to remain independent of the actual data source.
Regardless of where the data comes from, every connector returns a
standard Pandas DataFrame.
"""

from abc import ABC, abstractmethod
import pandas as pd


class BaseConnector(ABC):
    """Common interface for all data source connectors."""

    def __init__(self, config: dict):
        self.config = config

    @abstractmethod
    def fetch(self) -> pd.DataFrame:
        """Fetch data and return it as a Pandas DataFrame."""
        raise NotImplementedError

    def validate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Perform basic validation to ensure that the data is not empty."""
        if df is None or df.empty:
            raise ValueError(
                f"{self.__class__.__name__}: No data was retrieved from the data source. "
                f"Please check the configuration: {self.config}"
            )
        return df
