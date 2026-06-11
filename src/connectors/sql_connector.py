from typing import Any, Dict, Optional

import pandas as pd

from src.utils.database import DatabaseManager
from src.utils.logger import PipelineLogger


class SQLConnector:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.db = DatabaseManager(connection_string)
        self.logger = PipelineLogger.get_logger_for_module("pipeline.extract")

    def extract(self, query: str, params: Dict = None, chunk_size: int = None) -> pd.DataFrame:
        self.logger.info(f"Executando query de extração")
        df = self.db.read_query(query, params=params, chunksize=chunk_size)
        self.logger.info(f"Extração concluída: {len(df)} registros")
        return df

    def load(
        self,
        df: pd.DataFrame,
        table: str,
        if_exists: str = "replace",
        schema: str = None,
    ):
        self.logger.info(f"Iniciando carga na tabela: {table} ({len(df)} registros)")
        self.db.write_dataframe(df, table=table, if_exists=if_exists, schema=schema)
        self.logger.info(f"Carga concluída na tabela: {table}")
