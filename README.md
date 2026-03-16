# Neural Network for Municipal Economic Prediction

This project implements a deep learning model to predict municipal economic indicators based on political party policies and municipal ordinances.

## Project Structure

```
testing-inma/
├── data/
│   ├── municipios_murcia.md       # Municipal data documentation
│   ├── ordenanzas/                # Municipal ordinances (to be collected)
│   ├── economic/                  # Economic indicators
│   └── political/                 # Political party data
├── src/
│   ├── models/
│   │   └── municipal_model.py     # Neural network model
│   └── utils/
│       └── data_utils.py          # Data loading utilities
├── models/                        # Saved models
├── tests/                        # Unit tests
├── train.py                     # Training script
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Training

```bash
python train.py --data-dir data --epochs 50
```

### Configuration

Edit `config/default.json` to customize model parameters.

## Data Requirements

- Municipal population (>10,000 inhabitants for Region of Murcia)
- Political party in government (2011, 2015, 2019, 2022, 2025)
- Economic indicators:
  - Unemployment rate
  - Municipal GDP
  - Average income
  - Tax revenue

## Model Architecture

- Text encoder: BERT (Spanish) or TF-IDF fallback
- Mixed neural network combining:
  - Text embeddings from municipal ordinances
  - Tabular features (population, unemployment, etc.)
- Output: Economic indicator prediction

## References

- Paper: "Combining NLP and Deep Learning for Municipal Economic Prediction"
