from typing import Any, Dict

import pandas as pd

from src.connectors import APIConnector, CSVConnector, SQLConnector
from src.pipeline.base import PipelineStep
from src.utils.logger import PipelineLogger


class Extractor(PipelineStep):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = PipelineLogger.get_logger_for_module("pipeline.extract")

    def _get_connector(self):
        source_type = self.config["extract"]["source"]
        source_config = self.config["extract"].get(source_type, {})

        if source_type == "csv":
            return CSVConnector(
                filepath=source_config["path"],
                delimiter=source_config.get("delimiter", ","),
                encoding=source_config.get("encoding", "utf-8"),
                has_header=source_config.get("has_header", True),
                chunksize=source_config.get("chunksize"),
            )
        elif source_type == "api":
            return APIConnector(
                base_url=source_config["url"],
                method=source_config.get("method", "GET"),
                headers=source_config.get("headers"),
                max_retries=self.config["pipeline"]["execution"]["max_retries"],
                retry_delay=self.config["pipeline"]["execution"]["retry_delay_seconds"],
            )
        elif source_type == "sql":
            return SQLConnector(
                connection_string=source_config["connection_string"]
            )
        else:
            raise ValueError(f"Fonte não suportada: {source_type}")

    def execute(self, data: Any = None, context: dict = None) -> pd.DataFrame:
        self.logger.info(f"Iniciando extração (fonte: {self.config['extract']['source']})")
        connector = self._get_connector()
        source_config = self.config["extract"][self.config["extract"]["source"]]

        if isinstance(connector, CSVConnector):
            df = connector.extract()
        elif isinstance(connector, APIConnector):
            pagination = source_config.get("pagination", {})
            df = connector.extract(
                endpoint=source_config.get("endpoint", ""),
                params=source_config.get("params", {}),
                pagination=pagination.get("enabled", False),
                page_size=pagination.get("page_size", 100),
                max_pages=pagination.get("max_pages", 10),
            )
        elif isinstance(connector, SQLConnector):
            df = connector.extract(
                query=source_config["query"],
                chunk_size=source_config.get("chunk_size"),
            )
        else:
            raise ValueError(f"Conector não reconhecido")

        if isinstance(connector, APIConnector):
            connector.close()

        context = context or {}
        context["extracted_rows"] = len(df)
        context["source_type"] = self.config["extract"]["source"]

        self.logger.info(f"Extração concluída: {len(df)} registros")
        return df
