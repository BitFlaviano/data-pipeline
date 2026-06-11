from datetime import datetime
from typing import Any, Dict

import pandas as pd

from src.pipeline.base import PipelineStep
from src.utils.logger import PipelineLogger


class Transformer(PipelineStep):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = PipelineLogger.get_logger_for_module("pipeline.transform")

    def _clean_missing_values(self, df: pd.DataFrame, step: Dict) -> pd.DataFrame:
        strategy = step.get("strategy", "drop")
        columns = step.get("columns") or []

        if strategy == "drop":
            if columns:
                df = df.dropna(subset=columns)
            else:
                df = df.dropna()
        elif strategy == "fill":
            fill_value = step.get("fill_value", 0)
            if columns:
                for col in columns:
                    df[col] = df[col].fillna(fill_value)
            else:
                df = df.fillna(fill_value)
        elif strategy == "ffill":
            df = df.ffill()
        elif strategy == "bfill":
            df = df.bfill()

        return df

    def _remove_duplicates(self, df: pd.DataFrame, step: Dict) -> pd.DataFrame:
        subset = step.get("subset") or None
        df = df.drop_duplicates(subset=subset)
        return df

    def _convert_dtypes(self, df: pd.DataFrame, step: Dict) -> pd.DataFrame:
        mapping = step.get("mapping", {})
        for column, dtype in mapping.items():
            if column in df.columns:
                try:
                    df[column] = df[column].astype(dtype)
                except (ValueError, TypeError) as e:
                    self.logger.warning(f"Erro ao converter coluna {column} para {dtype}: {e}")
        return df

    def _rename_columns(self, df: pd.DataFrame, step: Dict) -> pd.DataFrame:
        mapping = step.get("mapping", {})
        df = df.rename(columns=mapping)
        return df

    def _filter_rows(self, df: pd.DataFrame, step: Dict) -> pd.DataFrame:
        condition = step.get("condition", "")
        if condition:
            df = df.query(condition)
        return df

    def _add_metadata(self, df: pd.DataFrame, step: Dict) -> pd.DataFrame:
        pipeline_version = self.config["pipeline"]["version"]
        columns_config = step.get("columns", [])

        for col_config in columns_config:
            if isinstance(col_config, dict):
                col_name = col_config.get("name", "metadata")
                col_type = col_config.get("type", "string")

                if col_type == "timestamp":
                    df[col_name] = datetime.now()
                elif col_type == "string" and col_name == "pipeline_version":
                    df[col_name] = pipeline_version
                else:
                    df[col_name] = None
            else:
                df[col_config] = None

        return df

    def execute(self, data: pd.DataFrame, context: dict = None) -> pd.DataFrame:
        if data is None or data.empty:
            self.logger.warning("Nenhum dado para transformar")
            return data

        self.logger.info(f"Iniciando transformação: {len(data)} registros")
        steps = self.config["transform"].get("steps", [])
        df = data.copy()

        for step in steps:
            if not step.get("enabled", True):
                continue

            step_name = step["name"]
            self.logger.info(f"Aplicando transformação: {step_name}")

            if step_name == "clean_missing_values":
                df = self._clean_missing_values(df, step)
            elif step_name == "remove_duplicates":
                df = self._remove_duplicates(df, step)
            elif step_name == "convert_dtypes":
                df = self._convert_dtypes(df, step)
            elif step_name == "rename_columns":
                df = self._rename_columns(df, step)
            elif step_name == "filter_rows":
                df = self._filter_rows(df, step)
            elif step_name == "add_metadata":
                df = self._add_metadata(df, step)

            self.logger.info(f"{step_name} concluído: {len(df)} registros")

        self.logger.info(f"Transformação concluída: {len(df)} registros")
        return df
