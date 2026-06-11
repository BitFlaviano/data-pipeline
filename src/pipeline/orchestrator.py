import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from src.pipeline.extract import Extractor
from src.pipeline.load import Loader
from src.pipeline.transform import Transformer
from src.quality.checks import DataQualityChecker
from src.utils.logger import PipelineLogger


@dataclass
class PipelineContext:
    pipeline_name: str
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    extracted_rows: int = 0
    transformed_rows: int = 0
    loaded_rows: int = 0
    quality_status: str = "NOT_RUN"
    stage: str = "initialized"
    errors: List[str] = field(default_factory=list)
    steps_completed: List[str] = field(default_factory=list)

    @property
    def duration_seconds(self) -> float:
        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pipeline": self.pipeline_name,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration_seconds,
            "stage": self.stage,
            "extracted_rows": self.extracted_rows,
            "transformed_rows": self.transformed_rows,
            "loaded_rows": self.loaded_rows,
            "quality_status": self.quality_status,
            "steps_completed": self.steps_completed,
            "errors": self.errors,
        }


class PipelineOrchestrator:
    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.logger = PipelineLogger.get_logger_for_module("pipeline")
        self.context = PipelineContext(
            pipeline_name=self.config["pipeline"]["name"]
        )
        self.extractor = Extractor(self.config)
        self.transformer = Transformer(self.config)
        self.loader = Loader(self.config)
        self.quality_checker = DataQualityChecker(self.config)

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Arquivo de configuração não encontrado: {config_path}")

        with open(path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        self.logger.info(f"Configuração carregada: {config['pipeline']['name']} v{config['pipeline']['version']}")
        return config

    def run(self) -> PipelineContext:
        self.logger.info(f"Iniciando pipeline: {self.context.pipeline_name}")
        self.context.stage = "extract"

        try:
            data = self.extractor.execute()
            self.context.extracted_rows = len(data)
            self.context.steps_completed.append("extract")

            self.context.stage = "quality_pre"
            quality_results = self.quality_checker.run_all_checks(data)
            quality_summary = self.quality_checker.summary()
            self.context.quality_status = quality_summary["status"]

            if quality_summary["failed"] > 0:
                self.logger.warning(f"Falhas em quality checks: {quality_summary['failed']}")

            self.context.stage = "transform"
            data = self.transformer.execute(data)
            self.context.transformed_rows = len(data)
            self.context.steps_completed.append("transform")

            self.context.stage = "load"
            success = self.loader.execute(data)
            if success:
                self.context.loaded_rows = len(data)
                self.context.steps_completed.append("load")

            self.context.stage = "completed"
            self.context.end_time = datetime.now()
            self.logger.info(f"Pipeline concluído com sucesso em {self.context.duration_seconds:.2f}s")

        except Exception as e:
            self.context.stage = "failed"
            self.context.end_time = datetime.now()
            self.context.errors.append(str(e))
            self.logger.error(f"Pipeline falhou: {e}")

        return self.context
