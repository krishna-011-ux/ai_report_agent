"""
SQL Connector - kisi bhi SQL database (PostgreSQL, MySQL, SQLite) se
data read karta hai SQLAlchemy connection string ke through.

Example connection strings:
  SQLite     : sqlite:///path/to/db.db
  PostgreSQL : postgresql://user:password@host:5432/dbname
  MySQL      : mysql+pymysql://user:password@host:3306/dbname
"""

import pandas as pd
from sqlalchemy import create_engine
from connectors.base_connector import BaseConnector


class SQLConnector(BaseConnector):
    def fetch(self) -> pd.DataFrame:
        cfg = self.config["sql"]
        conn_str = cfg["connection_string"]
        query = cfg["query"]
        print(f"[SQLConnector] Connecting to DB and running query...")
        engine = create_engine(conn_str)
        with engine.connect() as conn:
            df = pd.read_sql(query, conn)
        return self.validate(df)
