import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import os
import json
from pathlib import Path


class MunicipalDataset(Dataset):
    def __init__(
        self,
        data_path: str,
        text_column: str = "ordenanza_text",
        target_column: str = "renta_media",
        embedder: Optional[object] = None,
    ):
        self.data = pd.read_csv(data_path)
        self.text_column = text_column
        self.target_column = target_column
        self.embedder = embedder

        self.numeric_features = [
            "poblacion",
            "desempleo",
            "pib",
            "recaudacion_fiscal",
            "partido_governante",
            "anno",
        ]

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        row = self.data.iloc[idx]

        text = row[self.text_column] if pd.notna(row[self.text_column]) else ""

        numeric = torch.tensor(
            [row.get(f, 0) for f in self.numeric_features if f in row],
            dtype=torch.float32,
        )

        target = (
            torch.tensor(row[self.target_column], dtype=torch.float32)
            if self.target_column in row
            else torch.tensor(0.0)
        )

        return {
            "text": text,
            "numeric_features": numeric,
            "target": target,
            "municipio": row.get("municipio", ""),
            "anno": row.get("anno", 0),
        }


class TextEncoder(nn.Module):
    def __init__(self, embedding_dim: int = 768, hidden_dim: int = 256):
        super().__init__()
        self.bert_model_name = "bert-base-spanish-cased"

        try:
            from transformers import BertModel, BertTokenizer

            self.tokenizer = BertTokenizer.from_pretrained(self.bert_model_name)
            self.bert = BertModel.from_pretrained(self.bert_model_name)
            self.freeze_bert = True
        except ImportError:
            print("Transformers not installed. Using simple TF-IDF encoding.")
            self.bert = None
            self.tokenizer = None

        if self.bert is not None:
            if self.freeze_bert:
                for param in self.bert.parameters():
                    param.requires_grad = False

            self.projection = nn.Linear(embedding_dim, hidden_dim)
        else:
            self.projection = nn.Linear(5000, hidden_dim)
            self.tfidf_vectorizer = None

    def forward(self, texts: List[str]) -> torch.Tensor:
        if self.bert is not None:
            inputs = self.tokenizer(
                texts,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors="pt",
            )

            with torch.no_grad():
                outputs = self.bert(**inputs)

            embeddings = outputs.last_hidden_state[:, 0, :]
            return self.projection(embeddings)
        else:
            if self.tfidf_vectorizer is None:
                from sklearn.feature_extraction.text import TfidfVectorizer

                self.tfidf_vectorizer = TfidfVectorizer(max_features=5000)

            embeddings = self.tfidf_vectorizer.fit_transform(texts).toarray()
            return torch.tensor(embeddings, dtype=torch.float32)


class MixedNeuralNetwork(nn.Module):
    def __init__(
        self,
        text_embedding_dim: int = 256,
        numeric_feature_dim: int = 6,
        hidden_dim: int = 256,
        num_layers: int = 3,
        dropout: float = 0.3,
        output_dim: int = 1,
    ):
        super().__init__()

        self.text_encoder = TextEncoder(
            embedding_dim=768, hidden_dim=text_embedding_dim
        )

        combined_dim = text_embedding_dim + numeric_feature_dim

        layers = []
        in_dim = combined_dim

        for i in range(num_layers):
            layers.append(nn.Linear(in_dim, hidden_dim))
            layers.append(nn.BatchNorm1d(hidden_dim))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(dropout))
            in_dim = hidden_dim

        self.mlp = nn.Sequential(*layers)
        self.output = nn.Linear(hidden_dim, output_dim)

    def forward(
        self, text_embeddings: torch.Tensor, numeric_features: torch.Tensor
    ) -> torch.Tensor:
        combined = torch.cat([text_embeddings, numeric_features], dim=1)
        hidden = self.mlp(combined)
        return self.output(hidden)


class MunicipalEconomyModel:
    def __init__(
        self, config: Dict, device: str = "cuda" if torch.cuda.is_available() else "cpu"
    ):
        self.config = config
        self.device = device

        self.model = MixedNeuralNetwork(
            text_embedding_dim=config.get("text_embedding_dim", 256),
            numeric_feature_dim=config.get("numeric_feature_dim", 6),
            hidden_dim=config.get("hidden_dim", 256),
            num_layers=config.get("num_layers", 3),
            dropout=config.get("dropout", 0.3),
        ).to(device)

        self.optimizer = optim.Adam(
            self.model.parameters(),
            lr=config.get("learning_rate", 0.001),
            weight_decay=config.get("weight_decay", 1e-5),
        )

        self.criterion = nn.MSELoss()

        self.train_loader = None
        self.val_loader = None
        self.test_loader = None

        self.history = {
            "train_loss": [],
            "val_loss": [],
            "train_metrics": [],
            "val_metrics": [],
        }

    def prepare_data(
        self,
        train_path: str,
        val_path: str,
        test_path: Optional[str] = None,
        batch_size: int = 32,
    ):
        train_dataset = MunicipalDataset(train_path)
        val_dataset = MunicipalDataset(val_path)

        self.train_loader = DataLoader(
            train_dataset, batch_size=batch_size, shuffle=True
        )
        self.val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

        if test_path:
            test_dataset = MunicipalDataset(test_path)
            self.test_loader = DataLoader(
                test_dataset, batch_size=batch_size, shuffle=False
            )

    def train_epoch(self) -> float:
        self.model.train()
        total_loss = 0

        for batch in self.train_loader:
            text = batch["text"]
            numeric = batch["numeric_features"].to(self.device)
            targets = batch["target"].to(self.device)

            text_embeddings = self.model.text_encoder(text).to(self.device)

            self.optimizer.zero_grad()
            outputs = self.model(text_embeddings, numeric)
            loss = self.criterion(outputs.squeeze(), targets)
            loss.backward()
            self.optimizer.step()

            total_loss += loss.item()

        return total_loss / len(self.train_loader)

    def validate(self) -> float:
        self.model.eval()
        total_loss = 0

        with torch.no_grad():
            for batch in self.val_loader:
                text = batch["text"]
                numeric = batch["numeric_features"].to(self.device)
                targets = batch["target"].to(self.device)

                text_embeddings = self.model.text_encoder(text).to(self.device)
                outputs = self.model(text_embeddings, numeric)
                loss = self.criterion(outputs.squeeze(), targets)

                total_loss += loss.item()

        return total_loss / len(self.val_loader)

    def train(
        self,
        epochs: int,
        early_stopping_patience: int = 10,
        save_path: Optional[str] = None,
    ):
        best_val_loss = float("inf")
        patience_counter = 0

        for epoch in range(epochs):
            train_loss = self.train_epoch()
            val_loss = self.validate()

            self.history["train_loss"].append(train_loss)
            self.history["val_loss"].append(val_loss)

            print(f"Epoch {epoch + 1}/{epochs}")
            print(f"  Train Loss: {train_loss:.4f}")
            print(f"  Val Loss: {val_loss:.4f}")

            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0

                if save_path:
                    self.save(save_path)
            else:
                patience_counter += 1

            if patience_counter >= early_stopping_patience:
                print(f"Early stopping at epoch {epoch + 1}")
                break

    def predict(self, text: str, numeric_features: np.ndarray) -> float:
        self.model.eval()

        with torch.no_grad():
            text_embedding = self.model.text_encoder([text]).to(self.device)
            numeric = (
                torch.tensor(numeric_features, dtype=torch.float32)
                .unsqueeze(0)
                .to(self.device)
            )

            output = self.model(text_embedding, numeric)

        return output.item()

    def save(self, path: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        torch.save(
            {
                "model_state_dict": self.model.state_dict(),
                "optimizer_state_dict": self.optimizer.state_dict(),
                "config": self.config,
                "history": self.history,
            },
            path,
        )

    def load(self, path: str):
        checkpoint = torch.load(path, map_location=self.device)
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        self.config = checkpoint["config"]
        self.history = checkpoint["history"]


def create_default_config() -> Dict:
    return {
        "text_embedding_dim": 256,
        "numeric_feature_dim": 6,
        "hidden_dim": 256,
        "num_layers": 3,
        "dropout": 0.3,
        "learning_rate": 0.001,
        "weight_decay": 1e-5,
        "batch_size": 32,
        "epochs": 100,
        "early_stopping_patience": 10,
        "target_column": "renta_media",
        "text_column": "ordenanza_text",
    }


if __name__ == "__main__":
    config = create_default_config()
    model = MunicipalEconomyModel(config)
    print("Model initialized successfully!")
    print(f"Device: {model.device}")
    print(f"Model architecture:\n{model.model}")
