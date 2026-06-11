import pandas as pd
import pytest
import tempfile
from pathlib import Path

from src.connectors.csv_connector import CSVConnector


@pytest.fixture
def sample_data():
    return pd.DataFrame({
        "id": [1, 2, 3],
        "produto": ["A", "B", "C"],
        "valor": [100.0, 200.0, 300.0],
    })


def test_csv_load_overwrite(sample_data, tmp_path):
    output = tmp_path / "test_output.csv"
    connector = CSVConnector(filepath=str(output))
    connector.load(sample_data, mode="overwrite")
    assert output.exists()
    df = pd.read_csv(output)
    assert len(df) == 3


def test_csv_load_append(sample_data, tmp_path):
    output = tmp_path / "test_append.csv"
    sample_data.to_csv(output, index=False)
    connector = CSVConnector(filepath=str(output))
    connector.load(sample_data, mode="append")
    df = pd.read_csv(output)
    assert len(df) == 6


def test_csv_load_empty_data(tmp_path):
    output = tmp_path / "empty.csv"
    connector = CSVConnector(filepath=str(output))
    connector.load(pd.DataFrame())
    assert output.exists()
    assert pd.read_csv(output).empty
