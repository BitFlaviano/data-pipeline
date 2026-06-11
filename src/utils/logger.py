import logging
import logging.config
from pathlib import Path
from typing import Optional

import yaml


class PipelineLogger:
    _instances: dict = {}

    def __new__(cls, name: str = "pipeline", config_path: Optional[Path] = None):
        if name not in cls._instances:
            instance = super().__new__(cls)
            instance._initialized = False
            cls._instances[name] = instance
        return cls._instances[name]

    def __init__(self, name: str = "pipeline", config_path: Optional[Path] = None):
        if self._initialized:
            return
        self._initialized = True

        if config_path and Path(config_path).exists():
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)
                logging.config.dictConfig(config)
        else:
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            )

        self.logger = logging.getLogger(name)

    def get_logger(self) -> logging.Logger:
        return self.logger

    @staticmethod
    def get_logger_for_module(module_name: str) -> logging.Logger:
        return logging.getLogger(module_name)
