from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import pandas as pd

from src.utils.logger import PipelineLogger


@dataclass
class QualityCheckResult:
    check_name: str
    passed: bool
    details: str
    severity: str = "WARNING"
    row_count: Optional[int] = None


class DataQualityChecker:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.results: List[QualityCheckResult] = []
        self.logger = PipelineLogger.get_logger_for_module("pipeline")

    def check_null_values(self, df: pd.DataFrame, threshold: float = 0.1) -> QualityCheckResult:
        null_pct = df.isnull().mean()
        columns_above_threshold = null_pct[null_pct > threshold]

        passed = len(columns_above_threshold) == 0
        details = (
            "Todos os campos dentro do limite de nulos"
            if passed
            else f"Colunas com nulos acima de {threshold:.0%}: {columns_above_threshold.to_dict()}"
        )

        return QualityCheckResult(
            check_name="null_values",
            passed=passed,
            details=details,
            severity="ERROR" if not passed else "INFO",
            row_count=len(df),
        )

    def check_unique_values(self, df: pd.DataFrame, columns: List[str] = None) -> QualityCheckResult:
        cols = columns or []
        duplicates = df[cols].duplicated(keep=False) if cols else df.duplicated(keep=False)
        duplicate_count = duplicates.sum()

        passed = duplicate_count == 0
        details = (
            "Nenhuma duplicata encontrada"
            if passed
            else f"{duplicate_count} registros duplicados encontrados"
        )

        return QualityCheckResult(
            check_name="unique_values",
            passed=passed,
            details=details,
            severity="WARNING" if duplicate_count > 0 else "INFO",
            row_count=len(df),
        )

    def check_value_range(self, df: pd.DataFrame, rules: Dict[str, tuple]) -> QualityCheckResult:
        violations = []
        for column, (min_val, max_val) in rules.items():
            if column in df.columns:
                out_of_range = df[(df[column] < min_val) | (df[column] > max_val)]
                if not out_of_range.empty:
                    violations.append(f"{column}: {len(out_of_range)} valores fora de [{min_val}, {max_val}]")

        passed = len(violations) == 0
        details = "Todos os valores dentro dos intervalos" if passed else "; ".join(violations)

        return QualityCheckResult(
            check_name="value_range",
            passed=passed,
            details=details,
            severity="ERROR" if not passed else "INFO",
            row_count=len(df),
        )

    def check_schema(self, df: pd.DataFrame, expected_schema: Dict[str, str]) -> QualityCheckResult:
        errors = []
        for column, expected_dtype in expected_schema.items():
            if column not in df.columns:
                errors.append(f"Coluna ausente: {column}")
            elif str(df[column].dtype) != expected_dtype:
                errors.append(f"Tipo incorreto em '{column}': esperado {expected_dtype}, obtido {df[column].dtype}")

        passed = len(errors) == 0
        details = "Schema válido" if passed else "; ".join(errors)

        return QualityCheckResult(
            check_name="schema",
            passed=passed,
            details=details,
            severity="ERROR" if not passed else "INFO",
            row_count=len(df),
        )

    def run_all_checks(self, df: pd.DataFrame) -> List[QualityCheckResult]:
        self.results = []
        quality_config = self.config.get("quality", {})
        if not quality_config.get("enabled", True):
            self.logger.info("Quality checks desabilitados")
            return self.results

        self.logger.info("Iniciando verificações de qualidade")
        checks = quality_config.get("checks", [])

        for check in checks:
            if not check.get("enabled", True):
                continue

            check_name = check["name"]
            self.logger.info(f"Executando quality check: {check_name}")

            if check_name == "check_null_values":
                result = self.check_null_values(df, threshold=check.get("threshold", 0.1))
            elif check_name == "check_unique_values":
                result = self.check_unique_values(df, columns=check.get("columns"))
            elif check_name == "check_value_range":
                result = self.check_value_range(df, rules=check.get("rules", {}))
            elif check_name == "check_schema":
                result = self.check_schema(df, expected_schema=check.get("expected_schema", {}))
            else:
                self.logger.warning(f"Quality check desconhecido: {check_name}")
                continue

            self.results.append(result)
            status = "PASSOU" if result.passed else "FALHOU"
            self.logger.info(f"{check_name}: {status} - {result.details}")

        return self.results

    def summary(self) -> Dict[str, Any]:
        if not self.results:
            return {"status": "NO_CHECKS", "total": 0, "passed": 0, "failed": 0}

        passed = sum(1 for r in self.results if r.passed)
        failed = len(self.results) - passed

        return {
            "status": "PASSED" if failed == 0 else "FAILED",
            "total": len(self.results),
            "passed": passed,
            "failed": failed,
            "details": [
                {
                    "check": r.check_name,
                    "passed": r.passed,
                    "details": r.details,
                    "severity": r.severity,
                }
                for r in self.results
            ],
        }
