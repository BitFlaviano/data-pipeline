from typing import Any, Dict

import pandas as pd

from src.connectors import CSVConnector, SQLConnector
from src.pipeline.base import PipelineStep
from src.utils.logger import PipelineLogger


class Loader(PipelineStep):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = PipelineLogger.get_logger_for_module("pipeline.load")

    def _get_connector(self):
        target_type = self.config["load"]["target"]
        target_config = self.config["load"].get(target_type, {})

        if target_type == "csv":
            return CSVConnector(
                filepath=target_config["path"],
                delimiter=target_config.get("delimiter", ","),
                encoding=target_config.get("encoding", "utf-8"),
            )
        elif target_type == "sql":
            return SQLConnector(
                connection_string=target_config["connection_string"]
            )
        else:
            raise ValueError(f"Destino não suportado: {target_type}")

    def execute(self, data: pd.DataFrame, context: dict = None) -> bool:
        if data is None or data.empty:
            self.logger.warning("Nenhum dado para carregar")
            return False

        self.logger.info(f"Iniciando carga: {len(data)} registros")
        connector = self._get_connector()
        target_config = self.config["load"][self.config["load"]["target"]]

        if isinstance(connector, CSVConnector):
            connector.load(data, mode=target_config.get("mode", "overwrite"))
        elif isinstance(connector, SQLConnector):
            connector.load(
                data,
                table=target_config["table"],
                if_exists=target_config.get("if_exists", "replace"),
            )

        self.logger.info(f"Carga concluída com sucesso: {len(data)} registros")
        return True
