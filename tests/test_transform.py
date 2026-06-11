import pandas as pd
import pytest
from datetime import datetime

from src.pipeline.transform import Transformer


@pytest.fixture
def sample_data():
    return pd.DataFrame({
        "id": [1, 2, 3, 4, 4],
        "nome": ["Alice", "Bob", None, "Daniel", "Daniel"],
        "idade": [25, None, 35, 40, 40],
        "salario": [5000.0, 6000.0, 7000.0, 8000.0, 8000.0],
    })


@pytest.fixture
def config():
    return {
        "pipeline": {"version": "1.0.0"},
        "transform": {
            "steps": [
                {"name": "clean_missing_values", "enabled": True, "strategy": "drop"},
                {"name": "remove_duplicates", "enabled": True, "subset": []},
                {"name": "add_metadata", "enabled": True, "columns": [
                    {"name": "processed_at", "type": "timestamp"},
                    {"name": "pipeline_version", "type": "string"},
                ]},
            ]
        },
    }


def test_clean_missing_values(sample_data, config):
    transformer = Transformer(config)
    df = transformer._clean_missing_values(sample_data, {"strategy": "drop"})
    assert len(df) < len(sample_data)


def test_remove_duplicates(sample_data, config):
    transformer = Transformer(config)
    df = transformer._remove_duplicates(sample_data, {"subset": None})
    assert len(df) == 3


def test_add_metadata(sample_data, config):
    transformer = Transformer(config)
    step = {"columns": [{"name": "processed_at", "type": "timestamp"}]}
    df = transformer._add_metadata(sample_data, step)
    assert "processed_at" in df.columns
    assert isinstance(df["processed_at"].iloc[0], datetime)


def test_full_transform(sample_data, config):
    transformer = Transformer(config)
    df = transformer.execute(sample_data)
    assert len(df) == 2
    assert "processed_at" in df.columns
    assert "pipeline_version" in df.columns
