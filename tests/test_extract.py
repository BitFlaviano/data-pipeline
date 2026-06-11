import pandas as pd
import pytest
import tempfile
from pathlib import Path

from src.connectors.csv_connector import CSVConnector


@pytest.fixture
def sample_csv():
    df = pd.DataFrame({
        "id": [1, 2, 3],
        "nome": ["Alice", "Bob", "Carlos"],
        "idade": [25, 30, 35],
    })
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as f:
        df.to_csv(f.name, index=False)
        yield Path(f.name)
    Path(f.name).unlink()


def test_csv_extract(sample_csv):
    connector = CSVConnector(filepath=str(sample_csv))
    df = connector.extract()
    assert len(df) == 3
    assert list(df.columns) == ["id", "nome", "idade"]


def test_csv_extract_chunks(sample_csv):
    connector = CSVConnector(filepath=str(sample_csv), chunksize=2)
    chunks = list(connector.extract_chunks())
    assert len(chunks) >= 1


def test_csv_file_not_found():
    connector = CSVConnector(filepath="nonexistent.csv")
    with pytest.raises(FileNotFoundError):
        connector.extract()


def test_csv_load(tmp_path):
    df = pd.DataFrame({"col": [1, 2, 3]})
    output_path = tmp_path / "output.csv"
    connector = CSVConnector(filepath=str(output_path))
    connector.load(df)
    assert output_path.exists()
    loaded = pd.read_csv(output_path)
    assert len(loaded) == 3
