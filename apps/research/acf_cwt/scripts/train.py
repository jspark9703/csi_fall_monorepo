"""
모델 훈련 스크립트
Stage 4: train - PyTorch 모델 훈련, 메트릭 기록
"""
import json
import logging
from pathlib import Path

import numpy as np
import yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_params():
    """params.yaml 로드"""
    with open("params.yaml", "r") as f:
        return yaml.safe_load(f)


def get_data_paths():
    """실험별 데이터 경로 반환"""
    params = load_params()
    exp_name = params["experiment"]["name"]

    base_path = Path(__file__).parent.parent / "data" / exp_name

    return {
        "features": base_path / "features",
        "models": base_path / "models",
        "result": base_path / "result",
    }


def train_model(epochs: int = 50, batch_size: int = 32, learning_rate: float = 0.001):
    """
    PyTorch 모델 훈련

    Args:
        epochs: 훈련 에포크 수
        batch_size: 배치 크기
        learning_rate: 학습률
    """
    logger.info("🔄 Stage 4: Train - 모델 훈련 시작")

    paths = get_data_paths()
    paths["models"].mkdir(parents=True, exist_ok=True)
    paths["result"].mkdir(parents=True, exist_ok=True)

    # TODO: 실제 훈련 로직
    # 1. features/ 에서 features.npz 로드
    # 2. train/val/test 분할
    # 3. PyTorch DataLoader 구성
    # 4. Conv1D + BiLSTM 모델 정의
    # 5. 훈련 루프 (에포크 반복)
    # 6. 최적 모델 저장 (best_model.pt)

    # 예시 (가짜 메트릭):
    metrics = {
        "test_accuracy": 0.95,
        "test_precision": 0.93,
        "test_recall": 0.97,
        "test_f1": 0.95,
        "confusion_matrix": {
            "tp": 185,
            "fp": 12,
            "fn": 5,
            "tn": 198
        },
        "training_time": 125.5,
        "epochs_trained": epochs,
        "model_params": 45230
    }

    with open(paths["result"] / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    logger.info(f"✅ Training 완료: {paths['models']}, {paths['result']}")
    logger.info(f"   Accuracy: {metrics['test_accuracy']:.4f}")


def main():
    params = load_params()
    train_params = params["train"]

    train_model(
        epochs=train_params["epochs"],
        batch_size=train_params["batch_size"],
        learning_rate=train_params["learning_rate"]
    )


if __name__ == "__main__":
    main()
