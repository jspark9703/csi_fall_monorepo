"""
DVC stage: feature matrix → 학습 + W&B Artifact 로깅.

wandb.Artifact('csi_features:v<N>') — 피처셋 계보 추적
wandb.Artifact('fall_model:v<N>') — 모델 체크포인트 계보 추적
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import torch
import torch.nn as nn
import wandb
import yaml
from torch.utils.data import DataLoader, Dataset

from fall_sensing.core.feature import dwt_energy_features, pca_reduce
from fall_sensing.core.sanitization import hampel_filter

logger = logging.getLogger(__name__)


@dataclass
class TrainConfig:
    data_root: Path = Path(os.getenv("DATA_ROOT", "data/processed"))
    model_output: Path = Path(os.getenv("MODEL_OUTPUT", "data/models"))
    mlflow_uri: str = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
    epochs: int = 50
    batch_size: int = 32
    learning_rate: float = 1e-3
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    n_classes: int = 2


class CSIFallDataset(Dataset):
    """
    PyTorch Dataset for preprocessed CSI DWT feature sequences.

    Expected on-disk layout under data_root:
        <split>/  (train / val / test)
            <label>/  (0_nonfall / 1_fall)
                *.npy  -- 2-D arrays of shape (window, n_features)
    """

    def __init__(self, root: Path, split: str = "train") -> None:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, int]:
        raise NotImplementedError


class FallDetectionModel(nn.Module):
    """
    Conv1D + BiLSTM fall detection classifier.

    Input  : (batch, window_len, n_features)
    Output : (batch, n_classes) logits
    """

    def __init__(
        self,
        n_features: int = 20,
        n_classes: int = 2,
        conv_channels: int = 64,
        lstm_hidden: int = 128,
        dropout: float = 0.3,
    ) -> None:
        super().__init__()
        raise NotImplementedError

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        raise NotImplementedError


def train_one_epoch(
    model: FallDetectionModel,
    loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    criterion: nn.Module,
    device: str,
) -> float:
    """Train for one epoch; return mean loss."""
    raise NotImplementedError


def main(params: Optional[dict] = None, use_wandb: bool = False) -> None:
    """
    Entry point: load data, build model, run training loop.

    Parameters
    ----------
    params : dict or None
        Training parameters. If None, loaded from params.yaml.
    use_wandb : bool
        Enable Weights & Biases experiment tracking (default: False).
        Can also be controlled via WANDB_ENABLED env var.
    """
    logging.basicConfig(level=logging.INFO)

    params_path = Path("apps/research/params.yaml")
    if not params_path.exists():
        params_path = Path("params.yaml")

    params = params or yaml.safe_load(params_path.read_text())

    use_wandb = use_wandb or os.getenv("WANDB_ENABLED", "").lower() == "true"

    if use_wandb:
        run = wandb.init(project="csi-fall-detection", config=params)
        logger.info("W&B run initialized: %s", run.id)
    else:
        logger.info("W&B disabled (set WANDB_ENABLED=true to enable)")
        run = None

    raise NotImplementedError("DVC training pipeline stub — implement training loop")


if __name__ == "__main__":
    main()
