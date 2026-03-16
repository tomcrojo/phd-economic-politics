"""
Main training script for municipal economy prediction model
"""

import torch
import argparse
from pathlib import Path
import json
import sys

sys.path.append(str(Path(__file__).parent.parent))

from src.models.municipal_model import MunicipalEconomyModel, create_default_config
from src.utils.data_utils import load_municipal_data


def parse_args():
    parser = argparse.ArgumentParser(description="Train municipal economy model")
    parser.add_argument(
        "--config", type=str, default="config/default.json", help="Path to config file"
    )
    parser.add_argument(
        "--data-dir", type=str, default="data", help="Path to data directory"
    )
    parser.add_argument(
        "--save-path",
        type=str,
        default="models/best_model.pt",
        help="Path to save model",
    )
    parser.add_argument(
        "--epochs", type=int, default=None, help="Number of epochs (overrides config)"
    )
    parser.add_argument(
        "--device", type=str, default=None, help="Device to use (cuda/cpu)"
    )
    return parser.parse_args()


def main():
    args = parse_args()

    config = create_default_config()

    if Path(args.config).exists():
        with open(args.config, "r") as f:
            config.update(json.load(f))

    if args.epochs:
        config["epochs"] = args.epochs

    device = (
        args.device if args.device else ("cuda" if torch.cuda.is_available() else "cpu")
    )

    print(f"Training configuration:")
    print(f"  Device: {device}")
    print(f"  Epochs: {config['epochs']}")
    print(f"  Hidden dim: {config['hidden_dim']}")
    print(f"  Text embedding dim: {config['text_embedding_dim']}")

    model = MunicipalEconomyModel(config, device=device)

    data_path = Path(args.data_dir)
    train_path = data_path / "train.csv"
    val_path = data_path / "val.csv"
    test_path = data_path / "test.csv"

    if train_path.exists() and val_path.exists():
        print(f"\nLoading data from {data_path}")
        model.prepare_data(
            str(train_path),
            str(val_path),
            str(test_path) if test_path.exists() else None,
            batch_size=config["batch_size"],
        )

        print(f"Training model...")
        model.train(
            epochs=config["epochs"],
            early_stopping_patience=config.get("early_stopping_patience", 10),
            save_path=args.save_path,
        )

        print(f"\nModel saved to {args.save_path}")
    else:
        print(f"Training data not found at {train_path}")
        print("Please prepare the data first.")
        print("\nExpected data structure:")
        print("  data/")
        print("    train.csv")
        print("    val.csv")
        print("    test.csv (optional)")
        print("\nCSV columns should include:")
        print("  - municipio: municipality name")
        print("  - anno: year")
        print("  - ordenanza_text: text of municipal ordinances")
        print("  - poblacion: population")
        print("  - desempleo: unemployment rate")
        print("  - pib: GDP")
        print("  - renta_media: average income (target)")
        print("  - partido_governante: political party in government")
        print("  - recaudacion_fiscal: tax revenue")


if __name__ == "__main__":
    main()
