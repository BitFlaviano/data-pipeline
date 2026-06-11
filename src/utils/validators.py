from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd


def validate_file_exists(filepath: Path) -> bool:
    return filepath.exists() and filepath.is_file()


def validate_required_columns(df: pd.DataFrame, required_columns: List[str]) -> List[str]:
    missing = [col for col in required_columns if col not in df.columns]
    return missing


def validate_data_types(df: pd.DataFrame, type_mapping: Dict[str, type]) -> Dict[str, str]:
    errors = {}
    for column, expected_type in type_mapping.items():
        if column in df.columns:
            if not pd.api.types.is_dtype_equal(df[column].dtype, expected_type):
                errors[column] = f"Expected {expected_type}, got {df[column].dtype}"
    return errors


def validate_not_empty(df: pd.DataFrame) -> bool:
    return not df.empty


def validate_config(config: Dict[str, Any], required_fields: List[str]) -> List[str]:
    missing = [field for field in required_fields if field not in config]
    return missing
