"""
데이터 분할 및 전처리 스크립트
Stage 1: split - 소스 데이터를 train/test로 분할
Stage 2: preprocess - Hampel 필터 적용, 결측치 처리
"""
import argparse
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
        "raw_train": base_path / "raw" / "train",
        "raw_test": base_path / "raw" / "test",
        "preprocessed": base_path / "preprocessed",
    }


def stage_split(dataset_name: str, train_ratio: float = 0.8):
    """
    소스 데이터셋을 train/test로 분할

    Args:
        dataset_name: data/{dataset_name}에서 원본 데이터 읽기
        train_ratio: train/test 분할 비율
    """
    logger.info(f"🔄 Stage 1: Split - {dataset_name} 데이터셋 분할 시작")

    paths = get_data_paths()
    source_path = Path(__file__).parent.parent.parent.parent / "data" / dataset_name

    paths["raw_train"].mkdir(parents=True, exist_ok=True)
    paths["raw_test"].mkdir(parents=True, exist_ok=True)

    # TODO: 실제 데이터셋 로드 및 분할 로직
    # 예: CSV 파일 읽기, 랜덤 분할, numpy 배열로 저장

    logger.info(f"✅ Split 완료: {paths['raw_train']}, {paths['raw_test']}")


def stage_preprocess(hampel_window: int = 5, n_sigma: float = 3.0):
    """
    전처리: Hampel 필터, 선형보간

    Args:
        hampel_window: Hampel 필터 윈도우 크기
        n_sigma: 시그마 값
    """
    logger.info("🔄 Stage 2: Preprocess - Hampel 필터 및 보간 시작")

    paths = get_data_paths()

    # TODO: 실제 전처리 로직
    # 1. data/exp_001/raw/train, test에서 데이터 로드
    # 2. hampel_filter 적용 (shared core 사용)
    # 3. 선형보간으로 결측치 처리
    # 4. preprocessed/ 폴더에 저장

    paths["preprocessed"].mkdir(parents=True, exist_ok=True)

    logger.info(f"✅ Preprocess 완료: {paths['preprocessed']}")


def main():
    parser = argparse.ArgumentParser(description="데이터 분할 및 전처리")
    parser.add_argument("--stage", choices=["split", "preprocess"], required=True,
                        help="실행할 스테이지")
    args = parser.parse_args()

    params = load_params()
    experiment = params["experiment"]
    preprocessing = params["preprocessing"]

    if args.stage == "split":
        stage_split(
            dataset_name=experiment["dataset"],
            train_ratio=preprocessing["train_ratio"]
        )
    elif args.stage == "preprocess":
        stage_preprocess(
            hampel_window=preprocessing["hampel_window"],
            n_sigma=preprocessing["n_sigma"]
        )


if __name__ == "__main__":
    main()
