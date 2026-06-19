"""
특성 추출 스크립트
Stage 3: extract_features - ACF+CWT 특성 추출, PCA 차원 축소
"""
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
        "preprocessed": base_path / "preprocessed",
        "features": base_path / "features",
    }


def extract_features(dwt_level: int = 4, wavelet: str = "db4", n_pca: int = 3):
    """
    ACF + CWT 특성 추출

    Args:
        dwt_level: DWT 레벨
        wavelet: 웨이블릿 타입
        n_pca: PCA 차원 축소 차원
    """
    logger.info("🔄 Stage 3: Feature Extraction - ACF+CWT 특성 추출 시작")

    paths = get_data_paths()
    paths["features"].mkdir(parents=True, exist_ok=True)

    # TODO: 실제 특성 추출 로직
    # 1. preprocessed/ 에서 데이터 로드
    # 2. ACF (Auto-Correlation Function) 계산
    # 3. CWT (Continuous Wavelet Transform) 에너지 추출
    # 4. shared core의 pca_reduce 사용
    # 5. features.npz 저장

    # 예시 (가짜 데이터):
    # X = np.random.rand(100, 20)  # 100 샘플, 20 특성
    # y = np.random.randint(0, 2, 100)  # 이진 레이블
    # np.savez(paths["features"] / "features.npz", X=X, y=y)

    logger.info(f"✅ Feature Extraction 완료: {paths['features']}")


def main():
    params = load_params()
    feature_params = params["feature"]

    extract_features(
        dwt_level=feature_params["dwt_level"],
        wavelet=feature_params["wavelet"],
        n_pca=feature_params["n_pca"]
    )


if __name__ == "__main__":
    main()
