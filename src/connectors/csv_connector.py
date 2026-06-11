from pathlib import Path
from typing import Any, Dict, Iterator, Optional

import pandas as pd

from src.utils.logger import PipelineLogger


class CSVConnector:
    def __init__(
        self,
        filepath: str,
        delimiter: str = ",",
        encoding: str = "utf-8",
        has_header: bool = True,
        chunksize: Optional[int] = None,
    ):
        self.filepath = Path(filepath)
        self.delimiter = delimiter
        self.encoding = encoding
        self.has_header = has_header
        self.chunksize = chunksize
        self.logger = PipelineLogger.get_logger_for_module("pipeline.extract")

    def extract(self, **kwargs) -> pd.DataFrame:
        if not self.filepath.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {self.filepath}")

        self.logger.info(f"Iniciando extração de: {self.filepath}")

        df = pd.read_csv(
            self.filepath,
            sep=self.delimiter,
            encoding=self.encoding,
            header=0 if self.has_header else None,
            chunksize=self.chunksize,
            **kwargs,
        )

        if self.chunksize:
            return pd.concat(df, ignore_index=True)

        self.logger.info(f"Extração concluída: {len(df)} registros carregados")
        return df

    def extract_chunks(self, **kwargs) -> Iterator[pd.DataFrame]:
        if not self.filepath.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {self.filepath}")

        self.logger.info(f"Iniciando extração em chunks de: {self.filepath}")

        return pd.read_csv(
            self.filepath,
            sep=self.delimiter,
            encoding=self.encoding,
            header=0 if self.has_header else None,
            chunksize=self.chunksize or 10000,
            **kwargs,
        )

    def load(self, df: pd.DataFrame, mode: str = "overwrite", **kwargs):
        self.filepath.parent.mkdir(parents=True, exist_ok=True)

        if mode == "overwrite":
            df.to_csv(self.filepath, index=False, encoding=self.encoding, **kwargs)
        elif mode == "append":
            df.to_csv(self.filepath, mode="a", header=False, index=False, encoding=self.encoding, **kwargs)

        self.logger.info(f"Dados salvos em: {self.filepath} ({len(df)} registros)")
