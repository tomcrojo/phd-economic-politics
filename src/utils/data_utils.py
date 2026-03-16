"""
Data loading utilities for municipal economic data
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional
import json


def load_municipal_data(data_dir: str) -> Dict[str, pd.DataFrame]:
    """Load all municipal data files"""
    data_path = Path(data_dir)

    data = {}

    if (data_path / "municipios.csv").exists():
        data["municipios"] = pd.read_csv(data_path / "municipios.csv")

    if (data_path / "economic").exists():
        for file in (data_path / "economic").glob("*.csv"):
            data[f"economic_{file.stem}"] = pd.read_csv(file)

    if (data_path / "political").exists():
        for file in (data_path / "political").glob("*.csv"):
            data[f"political_{file.stem}"] = pd.read_csv(file)

    return data


def load_municipios_murcia(municipios_path: str) -> pd.DataFrame:
    """Load Murcia municipalities data"""
    df = pd.read_csv(municipios_path)
    return df


def create_dataset_from_sources(
    municipios_df: pd.DataFrame,
    economic_data: Dict[str, pd.DataFrame],
    political_data: Dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """Create unified dataset from multiple sources"""

    merged = municipios_df.copy()

    for key, df in economic_data.items():
        if "anno" in df.columns and "municipio" in df.columns:
            merged = merged.merge(df, on=["municipio", "anno"], how="left")

    for key, df in political_data.items():
        if "anno" in df.columns and "municipio" in df.columns:
            merged = merged.merge(df, on=["municipio", "anno"], how="left")

    return merged


def encode_political_party(party: str) -> int:
    """Encode political party as integer"""
    party_encoding = {
        "PP": 1,
        "PSOE": 2,
        "VOX": 3,
        "Ciudadanos": 4,
        "IU": 5,
        "PP": 6,
        "Otro": 7,
    }
    return party_encoding.get(party, 0)


def save_dataset(df: pd.DataFrame, output_path: str):
    """Save dataset to CSV"""
    df.to_csv(output_path, index=False)


def load_config(config_path: str) -> Dict:
    """Load configuration from JSON"""
    with open(config_path, "r") as f:
        return json.load(f)


if __name__ == "__main__":
    print("Data utilities loaded!")
