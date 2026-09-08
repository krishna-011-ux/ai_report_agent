"""
Base Connector
--------------
Har data source connector (CSV, Excel, SQL, API, Google Sheets) isi
abstract class se inherit karta hai. Isse pipeline ko farak nahi padta
data kahan se aa raha hai - sabka output ek standard Pandas DataFrame hota hai.
"""

from abc import ABC, abstractmethod
import pandas as pd


class BaseConnector(ABC):
    """Sabhi connectors ka common interface."""

    def __init__(self, config: dict):
        self.config = config

    @abstractmethod
    def fetch(self) -> pd.DataFrame:
        """Data fetch karke ek pandas DataFrame return karo."""
        raise NotImplementedError

    def validate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Basic validation - empty data check."""
        if df is None or df.empty:
            raise ValueError(
                f"{self.__class__.__name__}: Data source se koi data nahi mila. "
                f"Config check karo: {self.config}"
            )
        return df
