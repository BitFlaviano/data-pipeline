from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator, Optional

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


class DatabaseManager:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self._engine: Optional[Engine] = None

    def connect(self) -> Engine:
        if self._engine is None:
            self._engine = create_engine(self.connection_string)
        return self._engine

    def disconnect(self):
        if self._engine:
            self._engine.dispose()
            self._engine = None

    @contextmanager
    def connection(self):
        engine = self.connect()
        with engine.connect() as conn:
            yield conn

    def execute_query(self, query: str, params: dict = None) -> Any:
        with self.connection() as conn:
            result = conn.execute(text(query), params or {})
            conn.commit()
            return result

    def read_query(self, query: str, params: dict = None, chunksize: int = None) -> pd.DataFrame:
        return pd.read_sql_query(
            sql=query,
            con=self.connect(),
            params=params or {},
            chunksize=chunksize,
        )

    def write_dataframe(
        self,
        df: pd.DataFrame,
        table: str,
        if_exists: str = "replace",
        schema: str = None,
    ):
        df.to_sql(
            name=table,
            con=self.connect(),
            if_exists=if_exists,
            schema=schema,
            index=False,
            method="multi",
        )

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
