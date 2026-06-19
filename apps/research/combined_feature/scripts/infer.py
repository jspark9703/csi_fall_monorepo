"""
모델 추론 스크립트
독립 실행: 학습된 best_model.pt를 로드하여 새로운 데이터에 대한 추론 수행
"""
import argparse
import logging
from pathlib import Path

import yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_params():
    """params.yaml 로드"""
    with open("params.yaml", "r") as f:
        return yaml.safe_load(f)


def get_model_path(exp_name: str) -> Path:
    """모델 경로 반환"""
    base_path = Path(__file__).parent.parent / "data" / exp_name
    return base_path / "models" / "best_model.pt"


def infer(input_data_path: str, exp_name: str):
    """
    모델 추론 실행

    Args:
        input_data_path: 입력 데이터 파일 경로 (CSV, NPZ 등)
        exp_name: 사용할 모델 실험명
    """
    logger.info(f"🔄 Inference - {input_data_path} 데이터 추론 시작")

    model_path = get_model_path(exp_name)

    if not model_path.exists():
        logger.error(f"❌ 모델을 찾을 수 없습니다: {model_path}")
        raise FileNotFoundError(f"Model not found at {model_path}")

    # TODO: 실제 추론 로직
    # 1. best_model.pt 로드
    # 2. 입력 데이터 전처리 (특성 추출)
    # 3. 모델 추론 (forward pass)
    # 4. 결과 반환 (클래스 + 확률)

    logger.info(f"✅ Inference 완료")


def main():
    parser = argparse.ArgumentParser(description="모델 추론")
    parser.add_argument("--input", required=True, help="입력 데이터 파일 경로")
    parser.add_argument("--exp", default="exp_001", help="사용할 모델 실험명")
    parser.add_argument("--output", help="결과 저장 경로 (선택)")

    args = parser.parse_args()

    infer(
        input_data_path=args.input,
        exp_name=args.exp
    )


if __name__ == "__main__":
    main()
