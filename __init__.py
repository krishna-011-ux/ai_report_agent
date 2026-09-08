"""
Connector Factory
-----------------
Returns the appropriate connector class based on the 'source_type'
specified in config.yaml.

To add a new data source, create a new connector file and add it
to the connector mapping below.
"""

from connectors.csv_connector import CSVConnector
from connectors.excel_connector import ExcelConnector
from connectors.sql_connector import SQLConnector
from connectors.api_connector import APIConnector
from connectors.gsheet_connector import GSheetConnector


CONNECTOR_MAP = {
    "csv": CSVConnector,
    "excel": ExcelConnector,
    "sql": SQLConnector,
    "api": APIConnector,
    "gsheet": GSheetConnector,
}


def get_connector(config: dict):
    source_type = config["data_source"]["source_type"].lower()

    if source_type not in CONNECTOR_MAP:
        raise ValueError(
            f"Unknown source_type '{source_type}'. "
            f"Valid options: {list(CONNECTOR_MAP.keys())}"
        )

    connector_class = CONNECTOR_MAP[source_type]

    return connector_class(config["data_source"])
