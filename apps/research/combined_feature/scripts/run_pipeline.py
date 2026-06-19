"""
전체 파이프라인 실행 스크립트
DVC repro + 자동 Git 커밋

사용:
  python scripts/run_pipeline.py
  또는
  python scripts/run_pipeline.py --exp exp_002 --dataset HT-HAR
"""
import argparse
import logging
import subprocess
import sys
from pathlib import Path

import yaml

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def load_params(params_path: Path = Path("params.yaml")) -> dict:
    """params.yaml 로드"""
    with open(params_path, "r") as f:
        return yaml.safe_load(f)


def save_params(params: dict, params_path: Path = Path("params.yaml")):
    """params.yaml 저장"""
    with open(params_path, "w") as f:
        yaml.dump(params, f, default_flow_style=False, sort_keys=False)


def run_command(cmd: list, description: str) -> bool:
    """
    명령어 실행 및 로깅

    Args:
        cmd: 실행할 명령어 리스트
        description: 명령어 설명

    Returns:
        성공 여부 (True/False)
    """
    logger.info(f"▶️  {description}")
    logger.debug(f"   Command: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=False,
            text=True
        )
        logger.info(f"✅ {description} 완료")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ {description} 실패: {e}")
        return False


def run_pipeline(exp_name: str, dataset_name: str):
    """
    전체 DVC 파이프라인 실행

    Args:
        exp_name: 실험 이름 (exp_001, exp_002, ...)
        dataset_name: 데이터셋 이름 (mandeley, HT-HAR, manual, ...)
    """
    logger.info("=" * 60)
    logger.info(f"🚀 DVC 파이프라인 시작")
    logger.info(f"   실험명: {exp_name}")
    logger.info(f"   데이터셋: {dataset_name}")
    logger.info("=" * 60)

    # 1. params.yaml 업데이트
    params = load_params()
    params["experiment"]["name"] = exp_name
    params["experiment"]["dataset"] = dataset_name
    save_params(params)
    logger.info(f"✅ params.yaml 업데이트: {exp_name}, {dataset_name}")

    # 2. DVC 파이프라인 실행
    if not run_command(
        ["dvc", "repro", "--verbose"],
        "DVC 파이프라인 실행 (split → preprocess → extract_features → train → visualize)"
    ):
        logger.error("❌ DVC 파이프라인 실행 실패")
        return False

    # 3. Git 커밋
    logger.info("=" * 60)
    logger.info("📝 Git 커밋 준비")
    logger.info("=" * 60)

    # dvc.lock, params.yaml, 메트릭 파일을 git에 추가
    files_to_commit = [
        "dvc.lock",
        "params.yaml",
        f"data/{exp_name}/result/metrics.json",
    ]

    for file_path in files_to_commit:
        run_command(
            ["git", "add", file_path],
            f"Git staging: {file_path}"
        )

    # 변경사항 확인
    result = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        capture_output=True
    )

    if result.returncode == 0:
        logger.info("⚠️  커밋할 변경사항 없음")
    else:
        # 커밋 실행
        commit_message = f"experiment: {exp_name} ({dataset_name})"
        if not run_command(
            ["git", "commit", "-m", commit_message],
            f"Git 커밋: {commit_message}"
        ):
            logger.error("❌ Git 커밋 실패")
            return False

    logger.info("=" * 60)
    logger.info("✅ 파이프라인 완료!")
    logger.info(f"   결과: data/{exp_name}/result/")
    logger.info(f"   모델: data/{exp_name}/models/best_model.pt")
    logger.info("=" * 60)

    return True


def main():
    parser = argparse.ArgumentParser(
        description="DVC 파이프라인 실행 + 자동 Git 커밋"
    )
    parser.add_argument(
        "--exp",
        default="exp_001",
        help="실험 이름 (기본값: exp_001)"
    )
    parser.add_argument(
        "--dataset",
        default="mandeley",
        help="데이터셋 이름 (기본값: mandeley)"
    )

    args = parser.parse_args()

    success = run_pipeline(exp_name=args.exp, dataset_name=args.dataset)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
